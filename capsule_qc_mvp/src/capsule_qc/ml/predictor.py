from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from PIL import Image

from capsule_qc.ml.artifacts import ArtifactBundle, load_artifact_bundle
from capsule_qc.ml.preprocessing import image_to_tensor


class ModelNotReadyError(RuntimeError):
    """Raised when inference is requested before a model is available."""


@dataclass(slots=True)
class PredictionResult:
    status: str
    confidence: float
    defects: list[dict[str, Any]]


class ModelPredictor:
    def __init__(self, artifact_bundle: ArtifactBundle | None) -> None:
        self._artifact_bundle = artifact_bundle

    @classmethod
    def from_artifact_dir(cls, artifact_dir: Path, allow_missing_model: bool = False) -> "ModelPredictor":
        if not artifact_dir.exists():
            if allow_missing_model:
                return cls(None)
            raise FileNotFoundError(f"Model artifact directory not found: {artifact_dir}")
        try:
            return cls(load_artifact_bundle(artifact_dir))
        except FileNotFoundError:
            if allow_missing_model:
                return cls(None)
            raise

    @property
    def ready(self) -> bool:
        return self._artifact_bundle is not None

    def model_info(self) -> dict[str, Any]:
        if not self.ready:
            return {
                "loaded": False,
                "architecture": None,
                "labels": [],
                "image_size": None,
                "threshold": None,
            }
        bundle = self._artifact_bundle
        return {
            "loaded": True,
            "architecture": bundle.architecture,
            "labels": bundle.labels,
            "image_size": bundle.image_size,
            "threshold": bundle.threshold,
        }

    def inspect(self, image: Image.Image, threshold: float | None = None) -> PredictionResult:
        if not self.ready or self._artifact_bundle is None:
            raise ModelNotReadyError("Model artifact is not loaded")

        bundle = self._artifact_bundle
        model = bundle.model
        tensor = image_to_tensor(image, image_size=bundle.image_size).unsqueeze(0)
        with torch.no_grad():
            logits = model(tensor)
            probabilities = torch.softmax(logits, dim=1).squeeze(0)

        labels = bundle.labels
        no_ok_index = labels.index("no_ok") if "no_ok" in labels else min(len(labels) - 1, 1)
        ok_index = labels.index("ok") if "ok" in labels else 0
        selected_threshold = bundle.threshold if threshold is None else threshold
        no_ok_confidence = float(probabilities[no_ok_index].item())
        ok_confidence = float(probabilities[ok_index].item())

        if no_ok_confidence >= selected_threshold:
            return PredictionResult(status="defective", confidence=no_ok_confidence, defects=[])
        return PredictionResult(status="ok", confidence=ok_confidence, defects=[])
