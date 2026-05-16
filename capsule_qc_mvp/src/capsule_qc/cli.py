from __future__ import annotations

import argparse
import json
from pathlib import Path

from capsule_qc.data.exporters import export_binary_imagefolder, split_records_by_item
from capsule_qc.data.ingest import ingest_binary_folders
from capsule_qc.data.manifest import load_manifest
from capsule_qc.ml.training import train_binary_classifier


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="capsule-qc")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate-manifest", help="Validate metadata manifest")
    validate_parser.add_argument("--manifest", required=True, type=Path)

    export_parser = subparsers.add_parser("export-imagefolder", help="Export binary ImageFolder layout")
    export_parser.add_argument("--manifest", required=True, type=Path)
    export_parser.add_argument("--base-dir", required=True, type=Path)
    export_parser.add_argument("--output-dir", required=True, type=Path)
    export_parser.add_argument("--validation-ratio", type=float, default=0.2)
    export_parser.add_argument("--test-ratio", type=float, default=0.1)
    export_parser.add_argument("--seed", type=int, default=42)

    prepare_parser = subparsers.add_parser(
        "prepare-from-folders",
        help="Normalize fotos desde carpetas OK/NO OK, generar metadata y exportar dataset binario",
    )
    prepare_parser.add_argument("--ok-dir", action="append", required=True, type=Path)
    prepare_parser.add_argument("--no-ok-dir", action="append", required=True, type=Path)
    prepare_parser.add_argument("--dataset-dir", required=True, type=Path)
    prepare_parser.add_argument("--export-dir", required=True, type=Path)
    prepare_parser.add_argument("--default-defect", default="otro_no_ok_visible")
    prepare_parser.add_argument("--capture-session-id", default="session-auto")
    prepare_parser.add_argument("--sku", default="sku-unknown")
    prepare_parser.add_argument("--lot-id", default="lot-unknown")
    prepare_parser.add_argument("--view", default="front")
    prepare_parser.add_argument("--validation-ratio", type=float, default=0.2)
    prepare_parser.add_argument("--test-ratio", type=float, default=0.1)
    prepare_parser.add_argument("--seed", type=int, default=42)

    train_parser = subparsers.add_parser("train", help="Train a binary classifier from metadata")
    train_parser.add_argument("--manifest", required=True, type=Path)
    train_parser.add_argument("--base-dir", required=True, type=Path)
    train_parser.add_argument("--artifact-dir", required=True, type=Path)
    train_parser.add_argument("--architecture", default="simple_cnn")
    train_parser.add_argument("--image-size", type=int, default=224)
    train_parser.add_argument("--epochs", type=int, default=3)
    train_parser.add_argument("--batch-size", type=int, default=8)
    train_parser.add_argument("--learning-rate", type=float, default=1e-3)
    train_parser.add_argument("--validation-ratio", type=float, default=0.2)
    train_parser.add_argument("--test-ratio", type=float, default=0.1)
    train_parser.add_argument("--seed", type=int, default=42)
    return parser


def _cmd_validate_manifest(manifest: Path) -> int:
    records = load_manifest(manifest)
    counts: dict[str, int] = {}
    for record in records:
        counts[record.status] = counts.get(record.status, 0) + 1
    print(json.dumps({"records": len(records), "status_counts": counts}, indent=2))
    return 0


def _cmd_export_imagefolder(
    manifest: Path,
    base_dir: Path,
    output_dir: Path,
    validation_ratio: float,
    test_ratio: float,
    seed: int,
) -> int:
    records = load_manifest(manifest)
    counts = export_binary_imagefolder(
        records=records,
        base_dir=base_dir,
        output_dir=output_dir,
        validation_ratio=validation_ratio,
        test_ratio=test_ratio,
        seed=seed,
    )
    print(json.dumps(counts, indent=2))
    return 0


def _cmd_prepare_from_folders(
    ok_dirs: list[Path],
    no_ok_dirs: list[Path],
    dataset_dir: Path,
    export_dir: Path,
    default_defect: str,
    capture_session_id: str,
    sku: str,
    lot_id: str,
    view: str,
    validation_ratio: float,
    test_ratio: float,
    seed: int,
) -> int:
    result = ingest_binary_folders(
        ok_dirs=ok_dirs,
        no_ok_dirs=no_ok_dirs,
        dataset_dir=dataset_dir,
        default_defect=default_defect,
        capture_session_id=capture_session_id,
        sku=sku,
        lot_id=lot_id,
        view=view,
    )
    manifest_path = Path(str(result["manifest_path"]))
    records = load_manifest(manifest_path)
    export_counts = export_binary_imagefolder(
        records=records,
        base_dir=dataset_dir,
        output_dir=export_dir,
        validation_ratio=validation_ratio,
        test_ratio=test_ratio,
        seed=seed,
    )
    print(
        json.dumps(
            {
                "ingested": result,
                "exported": export_counts,
            },
            indent=2,
        )
    )
    return 0


def _cmd_train(
    manifest: Path,
    base_dir: Path,
    artifact_dir: Path,
    architecture: str,
    image_size: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    validation_ratio: float,
    test_ratio: float,
    seed: int,
) -> int:
    records = load_manifest(manifest)
    split_map = split_records_by_item(
        records,
        validation_ratio=validation_ratio,
        test_ratio=test_ratio,
        seed=seed,
    )
    result = train_binary_classifier(
        train_records=split_map["train"],
        val_records=split_map["val"],
        base_dir=base_dir,
        artifact_dir=artifact_dir,
        architecture=architecture,
        image_size=image_size,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
    )
    print(json.dumps(result.validation_metrics.to_dict(), indent=2))
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "validate-manifest":
        return _cmd_validate_manifest(args.manifest)
    if args.command == "export-imagefolder":
        return _cmd_export_imagefolder(
            manifest=args.manifest,
            base_dir=args.base_dir,
            output_dir=args.output_dir,
            validation_ratio=args.validation_ratio,
            test_ratio=args.test_ratio,
            seed=args.seed,
        )
    if args.command == "prepare-from-folders":
        return _cmd_prepare_from_folders(
            ok_dirs=args.ok_dir,
            no_ok_dirs=args.no_ok_dir,
            dataset_dir=args.dataset_dir,
            export_dir=args.export_dir,
            default_defect=args.default_defect,
            capture_session_id=args.capture_session_id,
            sku=args.sku,
            lot_id=args.lot_id,
            view=args.view,
            validation_ratio=args.validation_ratio,
            test_ratio=args.test_ratio,
            seed=args.seed,
        )
    if args.command == "train":
        return _cmd_train(
            manifest=args.manifest,
            base_dir=args.base_dir,
            artifact_dir=args.artifact_dir,
            architecture=args.architecture,
            image_size=args.image_size,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            validation_ratio=args.validation_ratio,
            test_ratio=args.test_ratio,
            seed=args.seed,
        )
    parser.error(f"Unsupported command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
