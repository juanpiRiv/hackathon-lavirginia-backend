import dotenv from "dotenv";

dotenv.config();

type RawEnv = Record<string, string | undefined>;

function requireVars(rawEnv: RawEnv, requiredVars: readonly string[]) {
  const missingVars = requiredVars.filter((variable) => !rawEnv[variable]);
  if (missingVars.length > 0) {
    throw new Error(`Missing environment variables: ${missingVars.join(", ")}`);
  }
}

export function buildEnv(rawEnv: RawEnv) {
  const normalizedMode = (rawEnv.PYTHON_MODEL_MODE ?? "assist")
    .replace(/['"]/g, "")
    .trim()
    .toLowerCase();
  const pythonModelMode = normalizedMode === "direct" ? "direct" : "assist";

  requireVars(rawEnv, ["JWT_SECRET", "VALIDATOR_API_KEY"]);
  if (pythonModelMode !== "direct") {
    requireVars(rawEnv, ["AI_GATEWAY_URL", "AI_GATEWAY_API_KEY"]);
  }

  return {
    port: Number(rawEnv.PORT || 3000),
    jwtSecret: rawEnv.JWT_SECRET as string,
    validatorApiKey: rawEnv.VALIDATOR_API_KEY as string,
    aiGatewayUrl: rawEnv.AI_GATEWAY_URL ?? "",
    aiGatewayApiKey: rawEnv.AI_GATEWAY_API_KEY ?? "",
    aiGatewayModel: rawEnv.AI_GATEWAY_MODEL ?? "gpt-4o-mini",
    aiGatewayTimeoutMs: Number(rawEnv.AI_GATEWAY_TIMEOUT_MS ?? 30000),
    maxImageSizeMb: Number(rawEnv.MAX_IMAGE_SIZE_MB ?? 10),
    pythonModelUrl: rawEnv.PYTHON_MODEL_URL ?? "http://localhost:8000",
    pythonModelTimeoutMs: Number(rawEnv.PYTHON_MODEL_TIMEOUT_MS ?? 5000),
    pythonModelMode,
  };
}

export const env = buildEnv(process.env);
