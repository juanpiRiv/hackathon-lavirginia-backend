import { PackageValidatorResult } from "../types/validator";
import { PythonModelResult } from "./python-model.service";

function hasToken(value: string, tokens: string[]): boolean {
  const normalized = value.toLowerCase();
  return tokens.some((token) => normalized.includes(token));
}

function resolvePrimaryReason(defectTypes: string[]): string {
  if (defectTypes.some((value) => hasToken(value, ["packaging", "caja", "deformacion"]))) {
    return "packaging_damaged";
  }
  if (defectTypes.some((value) => hasToken(value, ["rota", "damaged", "leaked"]))) {
    return "capsule_damaged";
  }
  if (defectTypes.some((value) => hasToken(value, ["faltante", "missing"]))) {
    return "capsules_missing";
  }
  if (defectTypes.some((value) => hasToken(value, ["desplazada", "alineada", "disposicion", "disorder"]))) {
    return "capsules_disordered";
  }
  return "capsules_disordered";
}

function resolveFailedAxes(defectTypes: string[]) {
  const packaging = defectTypes.some((value) => hasToken(value, ["packaging", "caja", "deformacion"]));
  const capsuleDamage = defectTypes.some((value) => hasToken(value, ["rota", "damaged", "leaked"]));
  const capsuleDisorder = defectTypes.some((value) =>
    hasToken(value, ["faltante", "missing", "desplazada", "alineada", "disposicion", "disorder"]),
  );

  // Semantica solicitada: true = eje OK, false = eje NO OK.
  return {
    capsule_damage: !capsuleDamage,
    capsule_disorder: !capsuleDisorder,
    packaging_damage: !packaging,
  };
}

export function mapPythonModelResultToPackageValidatorResult(
  pythonResult: PythonModelResult,
): PackageValidatorResult {
  if (pythonResult.status === "ok") {
    return {
      decision: "APROBADO",
      approved: true,
      confidence: pythonResult.confidence,
      reason: "package_looks_correct",
      secondary_reasons: [],
      observations: [],
      validator_summary: `Aprobado por modelo Python ${pythonResult.model_version}.`,
      failed_axes: {
        capsule_damage: true,
        capsule_disorder: true,
        packaging_damage: true,
      },
      image_quality: "acceptable",
    };
  }

  const defectTypes = pythonResult.defects
    .map((defect) => {
      if (typeof defect === "object" && defect !== null && "type" in defect && typeof defect.type === "string") {
        return defect.type;
      }
      return "unknown_defect";
    });

  const descriptions = pythonResult.defects
    .map((defect) => {
      if (typeof defect === "object" && defect !== null && "description" in defect && typeof defect.description === "string") {
        return defect.description;
      }
      return null;
    })
    .filter((value): value is string => value !== null);

  const primaryReason = resolvePrimaryReason(defectTypes);
  const failedAxes = resolveFailedAxes(defectTypes);
  const hasAnyAxisFalse = !failedAxes.capsule_damage || !failedAxes.capsule_disorder || !failedAxes.packaging_damage;

  return {
    decision: hasAnyAxisFalse ? "RECHAZADO" : "APROBADO",
    approved: !hasAnyAxisFalse,
    confidence: pythonResult.confidence,
    reason: hasAnyAxisFalse ? primaryReason : "package_looks_correct",
    secondary_reasons: defectTypes.slice(1),
    observations: descriptions,
    validator_summary: hasAnyAxisFalse
      ? `Rechazado por modelo Python ${pythonResult.model_version}.`
      : `Aprobado por modelo Python ${pythonResult.model_version}.`,
    failed_axes: failedAxes,
    image_quality: "acceptable",
  };
}
