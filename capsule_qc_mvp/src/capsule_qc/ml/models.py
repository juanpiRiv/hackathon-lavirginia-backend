from __future__ import annotations

import torch
from torch import nn


class SimpleCNN(nn.Module):
    def __init__(self, num_classes: int) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Linear(64, num_classes)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        features = self.features(inputs)
        logits = self.classifier(features.flatten(1))
        return logits


def build_model(architecture: str, num_classes: int, pretrained: bool = False) -> nn.Module:
    if architecture == "simple_cnn":
        return SimpleCNN(num_classes=num_classes)

    if architecture == "resnet18":
        try:
            from torchvision.models import ResNet18_Weights, resnet18
        except ModuleNotFoundError as exc:
            raise RuntimeError("torchvision is required for architecture='resnet18'") from exc
        weights = ResNet18_Weights.DEFAULT if pretrained else None
        model = resnet18(weights=weights)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        return model

    raise ValueError(f"Unsupported architecture: {architecture}")
