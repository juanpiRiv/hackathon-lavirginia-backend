# lavirginia-backend

Backend de validación de empaques de cápsulas de café. Recibe una imagen del empaque, la pre-analiza con un modelo ML propio (Python/PyTorch), luego la evalúa con un modelo de visión vía AI Gateway, y devuelve una decisión de control de calidad: **APROBADO** o **RECHAZADO**.

## Cómo funciona

```
Producto pasa por el scan
        ↓
POST /api/validator/validate-package
  imagen + metadata opcional
        ↓
Modelo Python (capsule_qc_mvp) — FastAPI en :8000
  POST /v1/inspect → { status, confidence, defects }
  (si no está entrenado o falla → continúa igual, no bloquea)
        ↓
AI Gateway (OpenCode GO / Kimi K2.6)
  recibe imagen + output del modelo Python
  evalúa 3 ejes:
    1. Rotura de cápsula (incluye café derramado)
    2. Desorden de cápsulas (deben ser 10, ordenadas)
    3. Rotura del empaquetado
        ↓
{ decision: "APROBADO" | "RECHAZADO", failed_axes, confidence, ... }
```

**Regla crítica:** si cualquier eje falla → `RECHAZADO`. Ante cualquier duda → `RECHAZADO`. Solo aprueba si los 3 ejes pasan con `confidence >= 0.85`.

**Degradación graceful:** si el modelo Python no está entrenado (devuelve 503) o falla por cualquier motivo, el sistema continúa normalmente con el AI Gateway. El campo `polygon_model_output` del cliente también puede omitirse sin problema.

---

## Stack

- Node.js 22 + Express 4 + TypeScript
- Prisma 7 + PostgreSQL (auth admin por OTP/JWT)
- Python 3.11 + FastAPI + PyTorch (modelo ML local en `capsule_qc_mvp/`)
- Multer (multipart/form-data)
- Fetch nativo Node 22 (sin SDK externo de AI)
- Docker Compose (3 servicios: `db`, `python-model`, `backend`)
- ESLint 10 + typescript-eslint
- GitHub Actions CI

---

## Modelo Python (capsule_qc_mvp)

Clasificador binario `ok/no_ok` entrenado con dataset propio. Se expone como servicio HTTP y el backend Node lo llama internamente antes de pasar al AI Gateway.

### Entrenamiento

```bash
cd capsule_qc_mvp
python -m pip install -e .

# Validar el dataset antes de entrenar
python -m capsule_qc.cli validate-manifest --manifest dataset/curated/metadata.csv

# Entrenar y guardar artifacts
python -m capsule_qc.cli train \
  --manifest dataset/curated/metadata.csv \
  --base-dir dataset \
  --artifact-dir artifacts/current
```

Templates para armar el dataset:
- [dataset/templates/metadata_template.csv](./capsule_qc_mvp/dataset/templates/metadata_template.csv)
- [dataset/templates/multilabel_template.csv](./capsule_qc_mvp/dataset/templates/multilabel_template.csv)

### Tests del módulo Python

```bash
cd capsule_qc_mvp
python -m unittest discover -s tests -v
```

### Sin modelo entrenado

El servicio puede arrancar sin weights entrenados con `CAPSULE_QC_ALLOW_MISSING_MODEL=true` (activado por defecto en `docker-compose.yml`). En ese caso devuelve `503` en `/v1/inspect` y el backend Node continúa sin su output — el AI Gateway evalúa la imagen solo.

---

## Configuración

### 1. Clonar y instalar

```bash
git clone https://github.com/juanpiRiv/hackathon-lavirginia-backend.git
cd hackathon-lavirginia-backend
npm install
```

### 2. Variables de entorno

Copiá `.env.example` a `.env` y completá los valores:

```bash
cp .env.example .env
```

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `JWT_SECRET` | ✅ | Secret para firmar tokens JWT del admin |
| `DATABASE_URL` | ✅ | Connection string PostgreSQL |
| `VALIDATOR_API_KEY` | ✅ | API key para consumir el endpoint de validación |
| `AI_GATEWAY_URL` | ✅ | URL del AI Gateway (OpenCode GO) |
| `AI_GATEWAY_API_KEY` | ✅ | API key de OpenCode GO |
| `AI_GATEWAY_MODEL` | ❌ | Modelo a usar (default: `opencode-go/kimi-k2.6`) |
| `AI_GATEWAY_TIMEOUT_MS` | ❌ | Timeout en ms para el AI Gateway (default: `30000`) |
| `MAX_IMAGE_SIZE_MB` | ❌ | Tamaño máximo de imagen (default: `10`) |
| `PYTHON_MODEL_URL` | ❌ | URL del modelo Python (default: `http://localhost:8000`) |
| `PYTHON_MODEL_TIMEOUT_MS` | ❌ | Timeout en ms para el modelo Python (default: `5000`) |
| `PORT` | ❌ | Puerto del servidor (default: `3000`) |

### 3. Base de datos

```bash
# Levantar PostgreSQL con Docker
docker compose up db -d

# Aplicar schema y seed del admin
npm run prisma:push
npm run seed
```

### 4. Levantar en desarrollo

```bash
# Solo Node (requiere db levantada, Python model opcional en :8000)
npm run dev
# Server corriendo en http://localhost:3000
```

---

## Docker (setup completo)

Antes de levantar, editá `docker-compose.yml` y reemplazá `PONER_ACA_TU_OPENCODE_KEY` con tu API key real.

```bash
docker compose up --build
```

Levanta 3 servicios:

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| `db` | `5432` | PostgreSQL 16 |
| `python-model` | `8000` | FastAPI — clasificador ML de cápsulas |
| `backend` | `3001` | API Node.js principal |

El backend espera a que la DB esté healthy, aplica el schema, hace seed del admin y arranca. El modelo Python puede iniciarse sin weights entrenados (503 en inferencia, no bloquea el backend).

### Agregar weights al modelo Python

Si ya entrenaste el modelo localmente, copiá los artifacts al directorio montado:

```bash
cp -r capsule_qc_mvp/artifacts/current/* capsule_qc_mvp/artifacts/current/
docker compose restart python-model
```

---

## Endpoints

### Health check

```bash
GET /health
# → { "ok": true, "service": "lavirginia-backend" }
```

### Auth admin (OTP)

```bash
# Solicitar OTP (el código se devuelve en la respuesta — modo hackathon)
POST /api/auth/request-otp
Content-Type: application/json
{ "email": "mateoyastor60@gmail.com" }

# Verificar OTP y obtener JWT
POST /api/auth/verify-otp
Content-Type: application/json
{ "email": "mateoyastor60@gmail.com", "code": "123456" }
```

### Perfil admin (requiere JWT)

```bash
GET /api/admin/me
Authorization: Bearer <token>
```

### Validar empaque

```bash
POST /api/validator/validate-package
x-api-key: <VALIDATOR_API_KEY>
Content-Type: multipart/form-data

Campos:
  image              Imagen del empaque (requerida) — jpeg, png, webp, heic, heif
  package_metadata   JSON string opcional con metadata del empaque
  polygon_model_output  JSON string opcional (sobrescrito por modelo Python si disponible)
```

**Respuesta exitosa:**

```json
{
  "decision": "RECHAZADO",
  "approved": false,
  "confidence": 0.95,
  "reason": "coffee_leaked",
  "secondary_reasons": ["capsules_disordered"],
  "observations": [
    "Se observa café derramado en la esquina inferior izquierda.",
    "Dos cápsulas parecen estar fuera de posición."
  ],
  "validator_summary": "El empaque presenta café derramado visible y desorden en las cápsulas.",
  "failed_axes": {
    "capsule_damage": true,
    "capsule_disorder": true,
    "packaging_damage": false
  },
  "image_quality": "good"
}
```

### Modo de integracion con modelo Python

El backend soporta dos modos:

- `PYTHON_MODEL_MODE=assist`
  El backend llama al modelo Python y usa su salida como contexto para el AI Gateway.
- `PYTHON_MODEL_MODE=direct`
  El backend llama al modelo Python y devuelve la decision local directamente, sin depender del AI Gateway para esa validacion.

Para demo rapida con el modelo entrenado localmente, usar `PYTHON_MODEL_MODE=direct`.

### Demo con camara o foto manual

Si queres probar sin frontend dedicado, el backend expone una pagina de demo:

```bash
GET /demo/camera
```

Flujo:
- abre la camara del dispositivo
- captura una foto
- la envia al backend como `multipart/form-data`
- muestra el JSON de respuesta en pantalla

Notas:
- en local funciona bien sobre `http://localhost`
- en un VPS remoto, la camara del navegador normalmente requiere `https`
- el endpoint que usa la demo es el mismo endpoint productivo: `POST /api/validator/validate-package`

**Códigos de error:**

| Código | Motivo |
|--------|--------|
| `401` | API key ausente o inválida |
| `400` | Imagen faltante, tipo de archivo no permitido, o JSON inválido en metadata |
| `200` | Siempre — incluso ante error del AI Gateway (devuelve `RECHAZADO` con reason descriptivo) |

---

## Prueba rápida

```bash
# 1. Health check
curl http://localhost:3000/health

# 2. Sin API key → 401
curl -X POST http://localhost:3000/api/validator/validate-package

# 3. Sin imagen → 400
curl -X POST http://localhost:3000/api/validator/validate-package \
  -H "x-api-key: validator-dev-key"

# 4. Validación completa
curl -X POST http://localhost:3000/api/validator/validate-package \
  -H "x-api-key: validator-dev-key" \
  -F "image=@./sample.jpg" \
  -F 'package_metadata={"package_type":"capsule_box","expected_capsules":10}'

# 5. Con request ID propio (trazabilidad)
curl -X POST http://localhost:3000/api/validator/validate-package \
  -H "x-api-key: validator-dev-key" \
  -H "x-request-id: mi-request-123" \
  -F "image=@./sample.jpg"
```

Con Docker, reemplazá el puerto `3000` por `3001`.

---

## CI

GitHub Actions corre en cada PR y push a `main`:

1. `npm ci`
2. `prisma generate`
3. `npm run lint`
4. `npm run build`
