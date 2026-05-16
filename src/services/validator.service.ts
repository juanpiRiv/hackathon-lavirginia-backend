import { env } from "../config/env";
import { PACKAGE_VALIDATOR_SYSTEM_PROMPT, buildPackageValidatorUserPrompt } from "../prompts/package-validator.prompt";
import { callPythonModel } from "./python-model.service";
import { mapPythonModelResultToPackageValidatorResult } from "./python-model.mapper";
import { FailedAxes, ImageQuality, PackageValidatorResult } from "../types/validator";

interface ValidatePackageParams {
  file: Express.Multer.File;
  packageMetadata: unknown;
  polygonModelOutput: unknown;
  requestId: string;
}

function fallbackRejection(reason: string, validatorSummary: string): PackageValidatorResult {
  return {
    decision: "RECHAZADO",
    approved: false,
    confidence: 1,
    reason,
    secondary_reasons: [],
    observations: [],
    validator_summary: validatorSummary,
    failed_axes: { capsule_damage: false, capsule_disorder: false, packaging_damage: false },
    image_quality: "poor",
  };
}

function isValidImageQuality(value: unknown): value is ImageQuality {
  return ["good", "acceptable", "poor"].includes(value as string);
}

function isValidFailedAxes(value: unknown): value is FailedAxes {
  if (typeof value !== "object" || value === null) return false;
  const axes = value as Record<string, unknown>;
  return (
    typeof axes.capsule_damage === "boolean" &&
    typeof axes.capsule_disorder === "boolean" &&
    typeof axes.packaging_damage === "boolean"
  );
}

function parseAndValidateAiResponse(raw: string): PackageValidatorResult | null {
  let parsed: Record<string, unknown>;

  try {
    parsed = JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return null;
  }

  const { decision, approved, confidence, reason, secondary_reasons, observations, validator_summary, failed_axes, image_quality } = parsed;

  if (decision !== "APROBADO" && decision !== "RECHAZADO") return null;
  if (typeof approved !== "boolean") return null;
  if (typeof confidence !== "number" || confidence < 0 || confidence > 1) return null;
  if (typeof reason !== "string") return null;
  if (!Array.isArray(secondary_reasons) || !secondary_reasons.every((r) => typeof r === "string")) return null;
  if (!Array.isArray(observations) || !observations.every((o) => typeof o === "string")) return null;
  if (typeof validator_summary !== "string") return null;
  if (!isValidFailedAxes(failed_axes)) return null;
  if (!isValidImageQuality(image_quality)) return null;

  const coherentApproved = decision === "APROBADO";
  if (approved !== coherentApproved) return null;

  // Para APROBADO todos los ejes deben pasar (false)
  if (decision === "APROBADO") {
    if (failed_axes.capsule_damage || failed_axes.capsule_disorder || failed_axes.packaging_damage) {
      return null;
    }
  }

  if (decision === "APROBADO" && confidence < 0.85) {
    return {
      decision: "RECHAZADO",
      approved: false,
      confidence,
      reason: "low_image_quality",
      secondary_reasons: secondary_reasons as string[],
      observations: observations as string[],
      validator_summary,
      failed_axes,
      image_quality,
    };
  }

  return {
    decision,
    approved,
    confidence,
    reason,
    secondary_reasons: secondary_reasons as string[],
    observations: observations as string[],
    validator_summary,
    failed_axes,
    image_quality,
  };
}

export async function validatePackage({
  file,
  packageMetadata,
  polygonModelOutput,
  requestId,
}: ValidatePackageParams): Promise<PackageValidatorResult> {
  const pythonResult = await callPythonModel(file, requestId);
  if (env.pythonModelMode === "direct") {
    if (pythonResult) {
      return mapPythonModelResultToPackageValidatorResult(pythonResult);
    }
    console.error(`[validator] [${requestId}] direct mode: Python model unavailable`);
    return fallbackRejection("ai_gateway_error", "Modelo Python no disponible. Verificá que el servicio Python esté corriendo y listo.");
  }
  const resolvedPolygonOutput = pythonResult ?? polygonModelOutput;

  const base64Image = file.buffer.toString("base64");
  const userPrompt = buildPackageValidatorUserPrompt({ packageMetadata, polygonModelOutput: resolvedPolygonOutput });

  const payload = {
    model: env.aiGatewayModel,
    messages: [
      {
        role: "system",
        content: PACKAGE_VALIDATOR_SYSTEM_PROMPT,
      },
      {
        role: "user",
        content: [
          {
            type: "text",
            text: userPrompt,
          },
          {
            type: "image_url",
            image_url: {
              url: `data:${file.mimetype};base64,${base64Image}`,
            },
          },
        ],
      },
    ],
    temperature: 0,
  };

  let response: Response;

  try {
    response = await fetch(env.aiGatewayUrl, {
      method: "POST",
      signal: AbortSignal.timeout(env.aiGatewayTimeoutMs),
      headers: {
        "Authorization": `Bearer ${env.aiGatewayApiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "unknown error";
    console.error(`[validator] [${requestId}] AI Gateway fetch error: ${message}`);
    return fallbackRejection("ai_gateway_error", "Error interno de validación: no se pudo contactar al AI Gateway.");
  }

  if (!response.ok) {
    const errBody = await response.text().catch(() => "");
    console.error(`[validator] [${requestId}] AI Gateway HTTP ${response.status}: ${errBody.slice(0, 300)}`);
    return fallbackRejection("ai_gateway_error", "Error interno de validación: respuesta inválida del AI Gateway.");
  }

  let data: unknown;
  try {
    data = await response.json();
  } catch {
    console.error(`[validator] [${requestId}] Failed to parse AI Gateway JSON response`);
    return fallbackRejection("invalid_ai_response", "Error interno de validación: respuesta del AI Gateway no parseable.");
  }

  const content = (data as { choices?: { message?: { content?: string } }[] })
    ?.choices?.[0]?.message?.content;

  if (typeof content !== "string") {
    console.error(`[validator] [${requestId}] AI Gateway response missing choices[0].message.content`);
    return fallbackRejection("invalid_ai_response", "Error interno de validación: estructura de respuesta inesperada del AI Gateway.");
  }

  const result = parseAndValidateAiResponse(content);
  if (!result) {
    console.error(`[validator] [${requestId}] AI response failed schema validation`);
    return fallbackRejection("invalid_ai_response", "Error interno de validación: la respuesta del modelo no cumple el schema esperado.");
  }

  return result;
}
