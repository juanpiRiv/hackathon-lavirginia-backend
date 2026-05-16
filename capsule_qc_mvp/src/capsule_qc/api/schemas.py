from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class ReadyResponse(BaseModel):
    status: str
    model_loaded: bool
    temp_dir_writable: bool


class ModelInfoResponse(BaseModel):
    name: str
    version: str
    loaded: bool
    architecture: str | None
    labels: list[str]
    image_size: int | None
    threshold: float | None


class DefectResponse(BaseModel):
    type: str
    confidence: float
    description: str | None = None


class InspectResponse(BaseModel):
    request_id: str
    client_reference: str | None = None
    status: str
    confidence: float
    defects: list[DefectResponse]
    model_version: str
    processing_ms: int
    annotated_image: Any = None


class ErrorEnvelope(BaseModel):
    error: dict[str, Any] = Field(default_factory=dict)
    request_id: str
