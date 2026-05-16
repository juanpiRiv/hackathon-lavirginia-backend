from __future__ import annotations

import csv
import shutil
from pathlib import Path


SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def _collect_images(input_dirs: list[Path]) -> list[Path]:
    images: list[Path] = []
    for input_dir in input_dirs:
        if not input_dir.is_dir():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        for path in sorted(input_dir.rglob("*")):
            if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES:
                images.append(path)
    return images


def ingest_binary_folders(
    ok_dirs: list[Path],
    no_ok_dirs: list[Path],
    dataset_dir: Path,
    default_defect: str = "otro_no_ok_visible",
    capture_session_id: str = "session-auto",
    sku: str = "sku-unknown",
    lot_id: str = "lot-unknown",
    view: str = "front",
) -> dict[str, int | str]:
    ok_images = _collect_images(ok_dirs)
    no_ok_images = _collect_images(no_ok_dirs)
    if not ok_images:
        raise ValueError("No se encontraron imagenes OK en las carpetas provistas")
    if not no_ok_images:
        raise ValueError("No se encontraron imagenes NO OK en las carpetas provistas")

    curated_images_dir = dataset_dir / "curated" / "images"
    curated_images_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = dataset_dir / "curated" / "metadata.csv"

    rows: list[dict[str, str]] = []

    for index, source in enumerate(ok_images, start=1):
        normalized_name = f"ok_{index:06d}{source.suffix.lower()}"
        target = curated_images_dir / normalized_name
        shutil.copy2(source, target)
        rows.append(
            {
                "image_path": f"curated/images/{normalized_name}",
                "item_id": f"ok-item-{index:06d}",
                "sku": sku,
                "lot_id": lot_id,
                "view": view,
                "status": "ok",
                "primary_defect": "",
                "all_defects": "",
                "capture_session_id": capture_session_id,
                "notes": f"imported-from:{source.parent.name}",
            }
        )

    for index, source in enumerate(no_ok_images, start=1):
        normalized_name = f"no_ok_{index:06d}{source.suffix.lower()}"
        target = curated_images_dir / normalized_name
        shutil.copy2(source, target)
        rows.append(
            {
                "image_path": f"curated/images/{normalized_name}",
                "item_id": f"no-ok-item-{index:06d}",
                "sku": sku,
                "lot_id": lot_id,
                "view": view,
                "status": "no_ok",
                "primary_defect": default_defect,
                "all_defects": default_defect,
                "capture_session_id": capture_session_id,
                "notes": f"imported-from:{source.parent.name}",
            }
        )

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
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
        writer.writerows(rows)

    return {
        "ok": len(ok_images),
        "no_ok": len(no_ok_images),
        "manifest_path": str(manifest_path),
    }
