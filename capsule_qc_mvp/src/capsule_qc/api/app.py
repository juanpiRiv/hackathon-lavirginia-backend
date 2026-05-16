from __future__ import annotations

import time
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from capsule_qc.api.schemas import HealthResponse, InspectResponse, ModelInfoResponse, ReadyResponse
from capsule_qc.ml.predictor import ModelNotReadyError, ModelPredictor
from capsule_qc.settings import Settings


ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}


def _load_predictor(settings: Settings) -> ModelPredictor:
    try:
        return ModelPredictor.from_artifact_dir(
            artifact_dir=settings.model_path,
            allow_missing_model=settings.allow_missing_model,
        )
    except FileNotFoundError:
        return ModelPredictor(None)


def _decode_image(upload: UploadFile, payload: bytes) -> Image.Image:
    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported media type")
    try:
        from io import BytesIO

        return Image.open(BytesIO(payload)).convert("RGB")
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=422, detail="Invalid image payload") from exc


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings.from_env()
    app = FastAPI(title=resolved_settings.app_name, version=resolved_settings.app_version)
    app.state.settings = resolved_settings
    app.state.predictor = _load_predictor(resolved_settings)

    @app.get("/v1/healthz", response_model=HealthResponse)
    def healthz() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.get("/v1/readyz", response_model=ReadyResponse)
    def readyz():
        predictor: ModelPredictor = app.state.predictor
        tmp_dir = Path(".")
        payload = ReadyResponse(
            status="ready" if predictor.ready else "not_ready",
            model_loaded=predictor.ready,
            temp_dir_writable=tmp_dir.exists(),
        )
        if predictor.ready:
            return payload
        return JSONResponse(status_code=503, content=payload.model_dump())

    @app.get("/v1/model/info", response_model=ModelInfoResponse)
    def model_info() -> ModelInfoResponse:
        predictor: ModelPredictor = app.state.predictor
        info = predictor.model_info()
        return ModelInfoResponse(
            name="capsule-box-inspector",
            version=resolved_settings.app_version,
            loaded=info["loaded"],
            architecture=info["architecture"],
            labels=info["labels"],
            image_size=info["image_size"],
            threshold=info["threshold"],
        )

    @app.post("/v1/inspect", response_model=InspectResponse)
    async def inspect(
        file: UploadFile = File(...),
        include_annotated: bool = Form(False),
        threshold: float | None = Form(None),
        client_reference: str | None = Form(None),
    ) -> InspectResponse:
        request_id = str(uuid.uuid4())
        settings_obj: Settings = app.state.settings
        raw_bytes = await file.read()
        if not raw_bytes:
            raise HTTPException(status_code=422, detail="Empty image payload")
        if len(raw_bytes) > settings_obj.max_upload_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large")

        image = _decode_image(file, raw_bytes)
        predictor: ModelPredictor = app.state.predictor
        started = time.perf_counter()
        try:
            prediction = predictor.inspect(image=image, threshold=threshold)
        except ModelNotReadyError as exc:
            raise HTTPException(status_code=503, detail="Model is not ready") from exc
        elapsed_ms = int((time.perf_counter() - started) * 1000)

        return InspectResponse(
            request_id=request_id,
            client_reference=client_reference,
            status=prediction.status,
            confidence=prediction.confidence,
            defects=prediction.defects,
            model_version=resolved_settings.app_version,
            processing_ms=elapsed_ms,
            annotated_image=None if not include_annotated else None,
        )

    return app


app = create_app()
