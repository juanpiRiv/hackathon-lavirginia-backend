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

## Flujo esperado
1. Completar `dataset/templates/metadata_template.csv` con fotos reales.
2. Validar el manifest.
3. Entrenar un baseline binario.
4. Exportar el artefacto del modelo.
5. Levantar la API.
