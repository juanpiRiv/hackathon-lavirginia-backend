FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY capsule_qc_mvp/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY capsule_qc_mvp/src /app/src
COPY capsule_qc_mvp/pyproject.toml capsule_qc_mvp/README.md /app/

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["sh", "-c", "uvicorn capsule_qc.api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
