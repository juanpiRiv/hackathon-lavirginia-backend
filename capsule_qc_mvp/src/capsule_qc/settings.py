from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    model_path: Path
    max_upload_mb: int = 10
    image_size: int = 224
    default_threshold: float = 0.5
    allow_missing_model: bool = False
    app_name: str = "capsule-qc-mvp"
    app_version: str = "0.1.0"

    @classmethod
    def from_env(cls) -> "Settings":
        model_path = Path(os.getenv("CAPSULE_QC_MODEL_PATH", "artifacts/current"))
        max_upload_mb = int(os.getenv("CAPSULE_QC_MAX_UPLOAD_MB", "10"))
        image_size = int(os.getenv("CAPSULE_QC_IMAGE_SIZE", "224"))
        default_threshold = float(os.getenv("CAPSULE_QC_DEFAULT_THRESHOLD", "0.5"))
        allow_missing_model = os.getenv("CAPSULE_QC_ALLOW_MISSING_MODEL", "false").lower() == "true"
        return cls(
            model_path=model_path,
            max_upload_mb=max_upload_mb,
            image_size=image_size,
            default_threshold=default_threshold,
            allow_missing_model=allow_missing_model,
        )
