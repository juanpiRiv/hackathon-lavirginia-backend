# hackathon-lavirginia-backend

Backend para La Virginia — Express + TypeScript + Prisma + PostgreSQL.
Autenticación por OTP (almacenado en DB) → JWT. Solo rol ADMIN.

## Skills (Auto-load based on context)

| Context | Read this file |
|---------|----------------|
| Any feature work: routes, controllers, services, models, middlewares, Prisma schema | `~/.claude/skills/lavirginia-backend/SKILL.md` |

Read the skill BEFORE writing any code.

## Stack

- **Runtime**: Node.js ≥18, Express 4
- **Language**: TypeScript (CommonJS, ES2022 target)
- **ORM**: Prisma 7 with `@prisma/adapter-pg` (connection pool via `pg`)
- **DB**: PostgreSQL
- **Auth**: OTP (6-digit, 10min TTL) → JWT (8h, signed with `JWT_SECRET`)
- **Dev**: `tsx watch` (no build step in dev)

## Project Layout

```
src/
├── app.ts              App + routes mount
├── server.ts           Entry point
├── config/env.ts       ENV validation (always use env.X)
├── config/prisma.ts    Prisma singleton
├── routes/             Path declarations
├── controllers/        HTTP layer
├── services/           Business logic
├── models/             Domain classes
├── middlewares/        Auth guard (requireAdminAuth)
└── types/express.d.ts  req.user typing
```

## Rules

- Never use `process.env.X` directly — always use the `env` object from `src/config/env.ts`
- Always use `return next(error)` in controllers to delegate to the global error handler
- Services interact with Prisma; controllers never import Prisma directly
- All routes under `/api/admin/*` require `requireAdminAuth` middleware
