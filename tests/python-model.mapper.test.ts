import test from "node:test";
import assert from "node:assert/strict";

import { mapPythonModelResultToPackageValidatorResult } from "../src/services/python-model.mapper";

test("maps ok python result to approved backend response", () => {
  const result = mapPythonModelResultToPackageValidatorResult({
    status: "ok",
    confidence: 0.91,
    defects: [],
    model_version: "capsule-qc-v0.1",
    processing_ms: 55,
  });

  assert.equal(result.decision, "APROBADO");
  assert.equal(result.approved, true);
  assert.equal(result.reason, "package_looks_correct");
  assert.deepEqual(result.failed_axes, {
    capsule_damage: false,
    capsule_disorder: false,
    packaging_damage: false,
  });
});

test("maps defective python result with packaging defect to rejected backend response", () => {
  const result = mapPythonModelResultToPackageValidatorResult({
    status: "defective",
    confidence: 0.88,
    defects: [
      {
        type: "packaging_roto_o_caja_danada",
        confidence: 0.83,
        description: "Packaging roto",
      },
    ],
    model_version: "capsule-qc-v0.1",
    processing_ms: 77,
  });

  assert.equal(result.decision, "RECHAZADO");
  assert.equal(result.approved, false);
  assert.equal(result.reason, "packaging_damaged");
  assert.deepEqual(result.failed_axes, {
    capsule_damage: false,
    capsule_disorder: false,
    packaging_damage: true,
  });
  assert.ok(result.validator_summary.includes("modelo Python"));
});
