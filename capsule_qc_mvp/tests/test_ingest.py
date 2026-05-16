from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from capsule_qc.data.ingest import ingest_binary_folders
from capsule_qc.data.manifest import load_manifest


class IngestTests(unittest.TestCase):
    def test_ingest_binary_folders_normalizes_names_and_generates_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ok_dir = root / "fotos_ok"
            no_ok_dir = root / "defectuosas"
            ok_dir.mkdir()
            no_ok_dir.mkdir()

            Image.new("RGB", (32, 32), color=(0, 255, 0)).save(ok_dir / "IMG_9281.JPG")
            Image.new("RGB", (32, 32), color=(255, 0, 0)).save(no_ok_dir / "whatsapp-image.png")

            dataset_dir = root / "dataset"
            result = ingest_binary_folders(
                ok_dirs=[ok_dir],
                no_ok_dirs=[no_ok_dir],
                dataset_dir=dataset_dir,
                default_defect="otro_no_ok_visible",
                capture_session_id="session-demo",
            )

            self.assertEqual(1, result["ok"])
            self.assertEqual(1, result["no_ok"])
            self.assertTrue((dataset_dir / "curated" / "metadata.csv").is_file())
            self.assertTrue((dataset_dir / "curated" / "images" / "ok_000001.jpg").is_file())
            self.assertTrue((dataset_dir / "curated" / "images" / "no_ok_000001.png").is_file())

            records = load_manifest(dataset_dir / "curated" / "metadata.csv")
            self.assertEqual(2, len(records))
            self.assertEqual(["ok", "no_ok"], [record.status for record in records])
            self.assertEqual("otro_no_ok_visible", records[1].primary_defect)
