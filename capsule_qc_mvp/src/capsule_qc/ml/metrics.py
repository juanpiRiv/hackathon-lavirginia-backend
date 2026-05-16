from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class BinaryMetrics:
    accuracy: float
    precision: float
    recall: float
    f1: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def compute_binary_metrics(targets: list[int], predictions: list[int]) -> BinaryMetrics:
    total = len(targets)
    if total == 0:
        return BinaryMetrics(accuracy=0.0, precision=0.0, recall=0.0, f1=0.0)

    tp = sum(1 for expected, pred in zip(targets, predictions) if expected == 1 and pred == 1)
    tn = sum(1 for expected, pred in zip(targets, predictions) if expected == 0 and pred == 0)
    fp = sum(1 for expected, pred in zip(targets, predictions) if expected == 0 and pred == 1)
    fn = sum(1 for expected, pred in zip(targets, predictions) if expected == 1 and pred == 0)

    accuracy = (tp + tn) / total
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return BinaryMetrics(accuracy=accuracy, precision=precision, recall=recall, f1=f1)
