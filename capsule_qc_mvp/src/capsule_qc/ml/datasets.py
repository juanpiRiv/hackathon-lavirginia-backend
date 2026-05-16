from __future__ import annotations

from pathlib import Path

from PIL import Image
from torch.utils.data import Dataset

from capsule_qc.data.manifest import InspectionRecord
from capsule_qc.ml.preprocessing import image_to_tensor


class ManifestClassificationDataset(Dataset):
    def __init__(self, records: list[InspectionRecord], base_dir: Path, image_size: int) -> None:
        self.records = [record for record in records if record.is_trainable]
        self.base_dir = base_dir
        self.image_size = image_size

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int):
        record = self.records[index]
        image_path = Path(record.image_path)
        if not image_path.is_absolute():
            image_path = self.base_dir / image_path
        with Image.open(image_path) as image:
            tensor = image_to_tensor(image, image_size=self.image_size)
        return tensor, record.binary_label
