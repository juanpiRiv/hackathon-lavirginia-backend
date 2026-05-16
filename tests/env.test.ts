import test from "node:test";
import assert from "node:assert/strict";

test("buildEnv allows direct mode without AI gateway variables", async () => {
  process.env.JWT_SECRET = "bootstrap-secret";
  process.env.VALIDATOR_API_KEY = "bootstrap-key";
  process.env.AI_GATEWAY_URL = "http://bootstrap.local";
  process.env.AI_GATEWAY_API_KEY = "bootstrap-ai-key";

  const { buildEnv } = await import("../src/config/env");
  const env = buildEnv({
    JWT_SECRET: "secret",
    VALIDATOR_API_KEY: "validator-key",
    PYTHON_MODEL_MODE: "direct",
  });

  assert.equal(env.pythonModelMode, "direct");
  assert.equal(env.aiGatewayUrl, "");
  assert.equal(env.aiGatewayApiKey, "");
});

test("buildEnv requires AI gateway variables in assist mode", async () => {
  process.env.JWT_SECRET = "bootstrap-secret";
  process.env.VALIDATOR_API_KEY = "bootstrap-key";
  process.env.AI_GATEWAY_URL = "http://bootstrap.local";
  process.env.AI_GATEWAY_API_KEY = "bootstrap-ai-key";

  const { buildEnv } = await import("../src/config/env");
  assert.throws(
    () =>
      buildEnv({
        JWT_SECRET: "secret",
        VALIDATOR_API_KEY: "validator-key",
        PYTHON_MODEL_MODE: "assist",
      }),
    /Missing environment variables/,
  );
});
