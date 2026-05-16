import dotenv from "dotenv";

dotenv.config();

const requiredVars = [
  "JWT_SECRET",
  "VALIDATOR_API_KEY",
  "AI_GATEWAY_URL",
  "AI_GATEWAY_API_KEY",
] as const;

const missingVars = requiredVars.filter((variable) => !process.env[variable]);
if (missingVars.length > 0) {
  throw new Error(`Missing environment variables: ${missingVars.join(", ")}`);
}

export const env = {
  port: Number(process.env.PORT || 3000),
  jwtSecret: process.env.JWT_SECRET as string,
  validatorApiKey: process.env.VALIDATOR_API_KEY as string,
  aiGatewayUrl: process.env.AI_GATEWAY_URL as string,
  aiGatewayApiKey: process.env.AI_GATEWAY_API_KEY as string,
  aiGatewayModel: process.env.AI_GATEWAY_MODEL ?? "gpt-4o-mini",
  aiGatewayTimeoutMs: Number(process.env.AI_GATEWAY_TIMEOUT_MS ?? 30000),
  maxImageSizeMb: Number(process.env.MAX_IMAGE_SIZE_MB ?? 10),
};
