import dotenv from "dotenv";
dotenv.config();

import { PrismaClient } from "@prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";
import { Pool } from "pg";

function requiredDatabaseUrl() {
  const value = process.env.DATABASE_URL;
  if (!value) {
    throw new Error("DATABASE_URL is required");
  }

  return value;
}

const pool = new Pool({
  connectionString: requiredDatabaseUrl()
});

const adapter = new PrismaPg(pool);

export const prisma = new PrismaClient({ adapter });
