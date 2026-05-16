from __future__ import annotations

import random
import shutil
from collections import defaultdict
from pathlib import Path

from capsule_qc.data.manifest import InspectionRecord


def split_records_by_item(
    records: list[InspectionRecord],
    validation_ratio: float = 0.2,
    test_ratio: float = 0.1,
    seed: int = 42,
) -> dict[str, list[InspectionRecord]]:
    grouped: dict[str, list[InspectionRecord]] = defaultdict(list)
    for record in records:
        if record.is_trainable:
            grouped[record.item_id].append(record)

    item_ids = sorted(grouped)
    random.Random(seed).shuffle(item_ids)

    total = len(item_ids)
    test_cutoff = int(total * test_ratio)
    val_cutoff = test_cutoff + int(total * validation_ratio)

    splits = {"train": [], "val": [], "test": []}
    for index, item_id in enumerate(item_ids):
        if index < test_cutoff:
            split_name = "test"
        elif index < val_cutoff:
            split_name = "val"
        else:
            split_name = "train"
        splits[split_name].extend(grouped[item_id])
    return splits


def export_binary_imagefolder(
    records: list[InspectionRecord],
    base_dir: Path,
    output_dir: Path,
    validation_ratio: float = 0.2,
    test_ratio: float = 0.1,
    seed: int = 42,
) -> dict[str, int]:
    split_map = split_records_by_item(records, validation_ratio=validation_ratio, test_ratio=test_ratio, seed=seed)
    counts: dict[str, int] = {}
    for split_name, split_records in split_map.items():
        count = 0
        for record in split_records:
            source = Path(record.image_path)
            if not source.is_absolute():
                source = base_dir / source
            target_dir = output_dir / split_name / record.status
            target_dir.mkdir(parents=True, exist_ok=True)
            target_name = f"{record.item_id}_{Path(record.image_path).name}"
            shutil.copy2(source, target_dir / target_name)
            count += 1
        counts[split_name] = count
    return counts
