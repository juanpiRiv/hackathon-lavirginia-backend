from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader

from capsule_qc.data.manifest import InspectionRecord
from capsule_qc.ml.artifacts import save_artifact_bundle
from capsule_qc.ml.datasets import ManifestClassificationDataset
from capsule_qc.ml.metrics import BinaryMetrics, compute_binary_metrics
from capsule_qc.ml.models import build_model


@dataclass(slots=True)
class TrainingResult:
    artifact_dir: Path
    validation_metrics: BinaryMetrics


def _evaluate_model(model: nn.Module, loader: DataLoader, device: torch.device) -> BinaryMetrics:
    model.eval()
    targets: list[int] = []
    predictions: list[int] = []
    with torch.no_grad():
        for inputs, labels in loader:
            logits = model(inputs.to(device))
            preds = torch.argmax(logits, dim=1).cpu().tolist()
            predictions.extend(preds)
            targets.extend(labels.tolist())
    return compute_binary_metrics(targets, predictions)


def train_binary_classifier(
    train_records: list[InspectionRecord],
    val_records: list[InspectionRecord],
    base_dir: Path,
    artifact_dir: Path,
    architecture: str = "simple_cnn",
    image_size: int = 224,
    epochs: int = 3,
    batch_size: int = 8,
    learning_rate: float = 1e-3,
) -> TrainingResult:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(architecture=architecture, num_classes=2, pretrained=False).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = nn.CrossEntropyLoss()

    train_dataset = ManifestClassificationDataset(train_records, base_dir=base_dir, image_size=image_size)
    val_dataset = ManifestClassificationDataset(val_records, base_dir=base_dir, image_size=image_size)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    best_metrics = BinaryMetrics(accuracy=0.0, precision=0.0, recall=0.0, f1=0.0)
    best_state = None
    for _epoch in range(epochs):
        model.train()
        for inputs, labels in train_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            logits = model(inputs)
            loss = loss_fn(logits, labels)
            loss.backward()
            optimizer.step()
        metrics = _evaluate_model(model, val_loader, device=device)
        if metrics.f1 >= best_metrics.f1:
            best_metrics = metrics
            best_state = {key: value.detach().cpu() for key, value in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)
    save_artifact_bundle(
        artifact_dir=artifact_dir,
        model=model.cpu(),
        labels=["ok", "no_ok"],
        architecture=architecture,
        image_size=image_size,
        threshold=0.5,
        extra_metadata={"validation_metrics": asdict(best_metrics)},
    )
    (artifact_dir / "metrics_val.json").write_text(json.dumps(asdict(best_metrics), indent=2), encoding="utf-8")
    return TrainingResult(artifact_dir=artifact_dir, validation_metrics=best_metrics)
