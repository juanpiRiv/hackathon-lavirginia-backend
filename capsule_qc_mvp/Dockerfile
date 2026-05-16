FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src
COPY pyproject.toml README.md /app/

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "capsule_qc.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
