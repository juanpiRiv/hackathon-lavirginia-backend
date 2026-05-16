import { Request, Response, NextFunction } from "express";
import { validatePackage } from "../services/validator.service";

export async function validatePackageHandler(req: Request, res: Response, next: NextFunction) {
  try {
    const requestId = (req.headers["x-request-id"] as string | undefined) ?? crypto.randomUUID();

    if (!req.file) {
      return res.status(400).json({ message: "image is required" });
    }

    let packageMetadata: unknown = null;
    if (req.body.package_metadata !== undefined && req.body.package_metadata !== "") {
      try {
        packageMetadata = JSON.parse(req.body.package_metadata as string);
      } catch {
        return res.status(400).json({ message: "package_metadata must be valid JSON" });
      }
    }

    let polygonModelOutput: unknown = null;
    if (req.body.polygon_model_output !== undefined && req.body.polygon_model_output !== "") {
      try {
        polygonModelOutput = JSON.parse(req.body.polygon_model_output as string);
      } catch {
        return res.status(400).json({ message: "polygon_model_output must be valid JSON" });
      }
    }

    const result = await validatePackage({
      file: req.file,
      packageMetadata,
      polygonModelOutput,
      requestId,
    });

    return res.status(200).json(result);
  } catch (error) {
    return next(error);
  }
}
