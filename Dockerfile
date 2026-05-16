FROM node:22-alpine AS base
WORKDIR /app

# Required during image build so Prisma can load config and generate client.
ENV DATABASE_URL=postgresql://postgres:postgres@db:5432/lavirginia_backend?schema=public

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run prisma:generate
RUN npm run build

EXPOSE 3000

CMD ["sh", "-c", "npm run prisma:push && npm run seed && npm run start"]
