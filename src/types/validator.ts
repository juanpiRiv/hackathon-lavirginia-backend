export type ValidatorDecision = "APROBADO" | "RECHAZADO";

export type ImageQuality = "good" | "acceptable" | "poor";

export const ALLOWED_REASONS = [
  "package_looks_correct",
  "capsule_damaged",
  "coffee_leaked",
  "capsules_disordered",
  "capsules_missing",
  "packaging_damaged",
  "low_image_quality",
  "ai_gateway_error",
  "invalid_ai_response",
] as const;

export type ValidatorReason = (typeof ALLOWED_REASONS)[number];

export interface FailedAxes {
  capsule_damage: boolean;
  capsule_disorder: boolean;
  packaging_damage: boolean;
}

export interface PackageValidatorResult {
  decision: ValidatorDecision;
  approved: boolean;
  confidence: number;
  reason: string;
  secondary_reasons: string[];
  observations: string[];
  validator_summary: string;
  failed_axes: FailedAxes;
  image_quality: ImageQuality;
}
