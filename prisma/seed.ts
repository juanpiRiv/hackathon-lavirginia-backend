import dotenv from "dotenv";
import { PrismaClient } from "@prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";
import { Pool } from "pg";

dotenv.config();

const DEFAULT_ADMIN_EMAIL = process.env.ADMIN_EMAIL ?? "mateoyastor60@gmail.com";

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
const prisma = new PrismaClient({ adapter });

async function main() {
  await prisma.user.upsert({
    where: { email: DEFAULT_ADMIN_EMAIL },
    update: {
      role: "ADMIN"
    },
    create: {
      email: DEFAULT_ADMIN_EMAIL,
      role: "ADMIN"
    }
  });

  console.log(`Admin user seeded successfully: ${DEFAULT_ADMIN_EMAIL}`);
}

main()
  .catch((error) => {
    console.error(error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
    await pool.end();
  });
