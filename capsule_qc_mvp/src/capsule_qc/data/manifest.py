from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ALLOWED_STATUSES = {"ok", "no_ok", "review", "discard"}


class ManifestValidationError(ValueError):
    """Raised when the metadata manifest contains invalid rows."""


@dataclass(slots=True)
class InspectionRecord:
    image_path: str
    item_id: str
    sku: str
    lot_id: str
    view: str
    status: str
    primary_defect: str | None
    all_defects: list[str]
    capture_session_id: str
    notes: str
    split: str | None = None

    @property
    def is_trainable(self) -> bool:
        return self.status in {"ok", "no_ok"}

    @property
    def binary_label(self) -> int:
        if self.status == "ok":
            return 0
        if self.status == "no_ok":
            return 1
        raise ManifestValidationError(f"Record {self.item_id} is not trainable: status={self.status}")


def _split_defects(raw_value: str) -> list[str]:
    return [value.strip() for value in raw_value.split(";") if value.strip()]


def _require(value: str, field_name: str, row_index: int) -> str:
    if value.strip():
        return value.strip()
    raise ManifestValidationError(f"Row {row_index}: field '{field_name}' is required")


def _parse_row(row: dict[str, str], row_index: int) -> InspectionRecord:
    status = _require(row.get("status", ""), "status", row_index).lower()
    if status not in ALLOWED_STATUSES:
        raise ManifestValidationError(f"Row {row_index}: invalid status '{status}'")

    primary_defect = row.get("primary_defect", "").strip() or None
    all_defects = _split_defects(row.get("all_defects", ""))

    if status == "ok" and (primary_defect or all_defects):
        raise ManifestValidationError(f"Row {row_index}: OK rows cannot define defects")
    if status == "no_ok" and not primary_defect:
        raise ManifestValidationError(f"Row {row_index}: NO_OK rows require primary_defect")

    split_value = row.get("split", "").strip() or None
    return InspectionRecord(
        image_path=_require(row.get("image_path", ""), "image_path", row_index),
        item_id=_require(row.get("item_id", ""), "item_id", row_index),
        sku=_require(row.get("sku", ""), "sku", row_index),
        lot_id=_require(row.get("lot_id", ""), "lot_id", row_index),
        view=_require(row.get("view", ""), "view", row_index),
        status=status,
        primary_defect=primary_defect,
        all_defects=all_defects,
        capture_session_id=_require(row.get("capture_session_id", ""), "capture_session_id", row_index),
        notes=row.get("notes", "").strip(),
        split=split_value,
    )


def load_manifest(path: str | Path) -> list[InspectionRecord]:
    manifest_path = Path(path)
    if not manifest_path.is_file():
        raise ManifestValidationError(f"Manifest file not found: {manifest_path}")

    records: list[InspectionRecord] = []
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_index, row in enumerate(reader, start=2):
            records.append(_parse_row(row, row_index))
    return records
