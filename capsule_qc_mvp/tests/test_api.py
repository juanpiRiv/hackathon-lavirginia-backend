from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from capsule_qc.api.app import create_app
from capsule_qc.ml.artifacts import save_artifact_bundle
from capsule_qc.ml.models import build_model
from capsule_qc.settings import Settings


class ApiTests(unittest.TestCase):
    def test_health_endpoint_is_alive(self) -> None:
        app = create_app(Settings(model_path=Path("missing"), allow_missing_model=True))
        client = TestClient(app)

        response = client.get("/v1/healthz")
        self.assertEqual(200, response.status_code)
        self.assertEqual({"status": "ok"}, response.json())

    def test_readyz_reports_not_ready_without_model(self) -> None:
        app = create_app(Settings(model_path=Path("missing"), allow_missing_model=False))
        client = TestClient(app)

        response = client.get("/v1/readyz")
        self.assertEqual(503, response.status_code)
        self.assertFalse(response.json()["model_loaded"])

    def test_inspect_returns_prediction_with_loaded_model(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp) / "artifact"
            model = build_model(architecture="simple_cnn", num_classes=2)
            save_artifact_bundle(
                artifact_dir=artifact_dir,
                model=model,
                labels=["ok", "no_ok"],
                architecture="simple_cnn",
                image_size=224,
                threshold=0.5,
            )

            app = create_app(Settings(model_path=artifact_dir, allow_missing_model=False))
            client = TestClient(app)

            image = Image.new("RGB", (256, 256), color=(120, 120, 120))
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG")
            buffer.seek(0)

            response = client.post(
                "/v1/inspect",
                files={"file": ("sample.jpg", buffer.getvalue(), "image/jpeg")},
            )

            self.assertEqual(200, response.status_code)
            payload = response.json()
            self.assertIn(payload["status"], {"ok", "defective"})
            self.assertIn("confidence", payload)
