import dotenv from "dotenv";

dotenv.config();

const requiredVars = ["JWT_SECRET"] as const;

const missingVars = requiredVars.filter((variable) => !process.env[variable]);
if (missingVars.length > 0) {
  throw new Error(`Missing environment variables: ${missingVars.join(", ")}`);
}

export const env = {
  port: Number(process.env.PORT || 3000),
  jwtSecret: process.env.JWT_SECRET as string
};
