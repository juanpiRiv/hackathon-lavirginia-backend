from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from torch import nn

from capsule_qc.ml.models import build_model


@dataclass(slots=True)
class ArtifactBundle:
    model: nn.Module
    labels: list[str]
    architecture: str
    image_size: int
    threshold: float
    metadata: dict[str, Any]


def save_artifact_bundle(
    artifact_dir: Path,
    model: nn.Module,
    labels: list[str],
    architecture: str,
    image_size: int,
    threshold: float,
    extra_metadata: dict[str, Any] | None = None,
) -> Path:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifact_dir / "model.pth"
    metadata_path = artifact_dir / "metadata.json"

    torch.save(model.state_dict(), model_path)
    metadata = {
        "architecture": architecture,
        "labels": labels,
        "image_size": image_size,
        "threshold": threshold,
        "defect_labels": [],
    }
    if extra_metadata:
        metadata.update(extra_metadata)

    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return artifact_dir


def load_artifact_bundle(artifact_dir: Path) -> ArtifactBundle:
    model_path = artifact_dir / "model.pth"
    metadata_path = artifact_dir / "metadata.json"
    if not model_path.is_file():
        raise FileNotFoundError(f"Missing model weights: {model_path}")
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Missing metadata: {metadata_path}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    labels = metadata["labels"]
    architecture = metadata["architecture"]
    image_size = int(metadata["image_size"])
    threshold = float(metadata["threshold"])

    model = build_model(architecture=architecture, num_classes=len(labels), pretrained=False)
    state_dict = torch.load(model_path, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()
    return ArtifactBundle(
        model=model,
        labels=labels,
        architecture=architecture,
        image_size=image_size,
        threshold=threshold,
        metadata=metadata,
    )
