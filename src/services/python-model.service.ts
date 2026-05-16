import { env } from "../config/env";

export interface PythonModelResult {
  status: "ok" | "defective";
  confidence: number;
  defects: unknown[];
  model_version: string;
  processing_ms: number;
}

export async function callPythonModel(
  file: Express.Multer.File,
  requestId: string
): Promise<PythonModelResult | null> {
  try {
    const formData = new FormData();
    const blob = new Blob([new Uint8Array(file.buffer)], { type: file.mimetype });
    formData.append("file", blob, file.originalname || "image");

    const response = await fetch(`${env.pythonModelUrl}/v1/inspect`, {
      method: "POST",
      signal: AbortSignal.timeout(env.pythonModelTimeoutMs),
      body: formData,
    });

    if (response.status === 503) {
      console.warn(`[python-model] [${requestId}] Model not ready — skipping`);
      return null;
    }

    if (!response.ok) {
      console.warn(`[python-model] [${requestId}] HTTP ${response.status} — skipping`);
      return null;
    }

    return await response.json() as PythonModelResult;
  } catch (err) {
    const message = err instanceof Error ? err.message : "unknown";
    console.warn(`[python-model] [${requestId}] Call failed: ${message} — skipping`);
    return null;
  }
}
