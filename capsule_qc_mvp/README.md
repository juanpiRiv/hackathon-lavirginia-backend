# Capsule QC MVP

Proyecto modular para entrenar y servir un MVP de inspeccion visual de cajas/capsulas La Virginia.

## Alcance inicial
- Dataset propio con `metadata.csv`.
- Clasificacion binaria `ok/no_ok`.
- API FastAPI para `1 foto = 1 caja`.
- Docker listo para VPS.

## Estructura

```text
capsule_qc_mvp/
  dataset/
  src/capsule_qc/
  tests/
  Dockerfile
  docker-compose.yml
```

## Setup local

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Flujo rapido para hackathon

Si ya tenes fotos separadas en carpetas `OK` y `NO OK`, no hace falta armar `metadata.csv` a mano.

Este comando:
- busca imagenes recursivamente
- normaliza nombres
- copia todo a `dataset/curated/images`
- genera `dataset/curated/metadata.csv`
- exporta `train/val/test` en formato binario

```bash
python -m capsule_qc.cli prepare-from-folders \
  --ok-dir "C:/ruta/a/fotos_ok" \
  --ok-dir "C:/ruta/a/mas_fotos_ok" \
  --no-ok-dir "C:/ruta/a/fotos_no_ok" \
  --dataset-dir dataset \
  --export-dir dataset/exports/imagefolder_binary
```

Despues entrenas asi:

```bash
python -m capsule_qc.cli train \
  --manifest dataset/curated/metadata.csv \
  --base-dir dataset \
  --artifact-dir artifacts/current \
  --epochs 8 \
  --batch-size 8
```

## Flujo esperado
1. Completar `dataset/templates/metadata_template.csv` con fotos reales.
2. Validar el manifest.
3. Entrenar un baseline binario.
4. Exportar el artefacto del modelo.
5. Levantar la API.
