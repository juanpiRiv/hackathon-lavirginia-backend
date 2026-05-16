from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from capsule_qc.data.manifest import ManifestValidationError, load_manifest


class ManifestTests(unittest.TestCase):
    def test_load_manifest_parses_valid_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "metadata.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "image_path",
                        "item_id",
                        "sku",
                        "lot_id",
                        "view",
                        "status",
                        "primary_defect",
                        "all_defects",
                        "capture_session_id",
                        "notes",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "image_path": "images/a.jpg",
                        "item_id": "item-1",
                        "sku": "sku-demo",
                        "lot_id": "lot-a",
                        "view": "front",
                        "status": "ok",
                        "primary_defect": "",
                        "all_defects": "",
                        "capture_session_id": "session-a",
                        "notes": "",
                    }
                )

            records = load_manifest(csv_path)
            self.assertEqual(1, len(records))
            self.assertEqual("ok", records[0].status)
            self.assertEqual([], records[0].all_defects)

    def test_load_manifest_rejects_invalid_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "metadata.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "image_path",
                        "item_id",
                        "sku",
                        "lot_id",
                        "view",
                        "status",
                        "primary_defect",
                        "all_defects",
                        "capture_session_id",
                        "notes",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "image_path": "images/a.jpg",
                        "item_id": "item-1",
                        "sku": "sku-demo",
                        "lot_id": "lot-a",
                        "view": "front",
                        "status": "broken",
                        "primary_defect": "",
                        "all_defects": "",
                        "capture_session_id": "session-a",
                        "notes": "",
                    }
                )

            with self.assertRaises(ManifestValidationError):
                load_manifest(csv_path)
