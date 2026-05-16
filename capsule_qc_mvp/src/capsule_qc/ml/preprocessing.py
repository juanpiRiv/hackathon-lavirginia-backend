from __future__ import annotations

from typing import Final

import numpy as np
import torch
from PIL import Image, ImageOps


IMAGENET_MEAN: Final[tuple[float, float, float]] = (0.485, 0.456, 0.406)
IMAGENET_STD: Final[tuple[float, float, float]] = (0.229, 0.224, 0.225)


def prepare_image(image: Image.Image, image_size: int) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    return image.resize((image_size, image_size))


def image_to_tensor(image: Image.Image, image_size: int) -> torch.Tensor:
    prepared = prepare_image(image, image_size=image_size)
    array = np.asarray(prepared, dtype=np.float32) / 255.0
    tensor = torch.from_numpy(array).permute(2, 0, 1)
    mean = torch.tensor(IMAGENET_MEAN, dtype=torch.float32).view(3, 1, 1)
    std = torch.tensor(IMAGENET_STD, dtype=torch.float32).view(3, 1, 1)
    return (tensor - mean) / std
