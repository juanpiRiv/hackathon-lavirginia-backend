from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import torch

from capsule_qc.ml.artifacts import load_artifact_bundle, save_artifact_bundle
from capsule_qc.ml.models import build_model


class ArtifactTests(unittest.TestCase):
    def test_save_and_load_artifact_bundle_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp) / "artifact"
            model = build_model(architecture="simple_cnn", num_classes=2)
            labels = ["ok", "no_ok"]

            save_artifact_bundle(
                artifact_dir=artifact_dir,
                model=model,
                labels=labels,
                architecture="simple_cnn",
                image_size=224,
                threshold=0.5,
            )

            bundle = load_artifact_bundle(artifact_dir)
            self.assertEqual("simple_cnn", bundle.architecture)
            self.assertEqual(labels, bundle.labels)
            self.assertEqual(224, bundle.image_size)
            self.assertIsInstance(bundle.model, torch.nn.Module)
