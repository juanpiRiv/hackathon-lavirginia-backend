export type ValidatorDecision = "APROBADO" | "RECHAZADO";

export type PolygonModelConsistency =
  | "consistent"
  | "inconsistent"
  | "not_provided"
  | "unknown_format";

export type ImageQuality = "good" | "acceptable" | "poor";

export const ALLOWED_REASONS = [
  "package_looks_correct",
  "coffee_leak_detected",
  "capsules_disordered",
  "capsules_out_of_position",
  "capsules_stacked",
  "missing_capsules",
  "package_dirty",
  "package_damaged",
  "low_image_quality",
  "polygon_model_inconsistent",
  "insufficient_information",
  "unknown_defect",
  "ai_gateway_error",
  "invalid_ai_response",
] as const;

export type ValidatorReason = (typeof ALLOWED_REASONS)[number];

export interface PackageValidatorResult {
  decision: ValidatorDecision;
  approved: boolean;
  confidence: number;
  reason: string;
  secondary_reasons: string[];
  observations: string[];
  validator_summary: string;
  polygon_model_consistency: PolygonModelConsistency;
  image_quality: ImageQuality;
}
