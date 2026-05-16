# Deploy VPS

Stack recomendado para demo estable:

- `caddy`: proxy reverso y TLS automatico
- `frontend`: Next.js publico
- `backend`: Node/Express privado
- `python-model`: FastAPI privado
- `db`: PostgreSQL privado

## Estructura esperada en el VPS

Clonar ambos repos como carpetas hermanas:

```bash
/opt/lavirginia/
  hackathon-lavirginia-backend/
  hackathon-v0-lavirginia-front/
```

El `docker-compose.yml` de esta carpeta asume exactamente esa disposicion.

## Preparacion

1. Clonar los repositorios:

```bash
mkdir -p /opt/lavirginia
cd /opt/lavirginia
git clone https://github.com/juanpiRiv/hackathon-lavirginia-backend.git
git clone https://github.com/MateoEmilio1/hackathon-v0-lavirginia-front.git
```

2. Copiar variables:

```bash
cd /opt/lavirginia/hackathon-lavirginia-backend/deploy/vps
cp .env.example .env
```

3. Editar `.env`:

- `DOMAIN`: dominio real apuntando al VPS
- `CADDY_EMAIL`: mail para certificados
- `JWT_SECRET`
- `POSTGRES_PASSWORD`
- `AI_GATEWAY_API_KEY`

4. Crear carpeta de pesos:

```bash
mkdir -p model_artifacts
```

Copiar ahi los artefactos del modelo entrenado:

```bash
model_artifacts/
  model.pth
  metadata.json
  metrics_val.json
```

## Levantar

```bash
docker compose up -d --build
```

## Actualizar el modelo sin romper la API

1. Reemplazar archivos dentro de `model_artifacts/`
2. Reiniciar solo el contenedor Python:

```bash
docker compose restart python-model
```

No hace falta reiniciar `frontend`, `backend` ni `db`.

## URLs

- app publica: `https://tu-dominio.com`
- health backend: `https://tu-dominio.com/health`
- auth backend: `https://tu-dominio.com/api/auth/...`
- validator backend: `https://tu-dominio.com/api/validator/...`

La UI publica del front usa `POST /api/inspect` sobre Next y Next reenvia internamente al backend.

## Notas practicas

- la camara en navegadores remotos requiere `https`
- `backend`, `python-model` y `db` no quedan expuestos a internet
- `docker compose` construye el frontend desde el repo hermano `hackathon-v0-lavirginia-front`
- el backend sigue ejecutando `prisma:push` y `seed` al arrancar; para hackathon eso simplifica el deploy
