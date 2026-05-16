import { Router } from "express";
import multer from "multer";
import { requireValidatorApiKey } from "../middlewares/api-key.middleware";
import { uploadSingle } from "../middlewares/upload.middleware";
import { validatePackageHandler } from "../controllers/validator.controller";

const router = Router();

router.post(
  "/validate-package",
  requireValidatorApiKey,
  (req, res, next) => {
    uploadSingle(req, res, (err) => {
      if (err instanceof multer.MulterError) {
        return res.status(400).json({ error: "upload_error", message: err.message });
      }
      if (err) {
        return res.status(400).json({ error: "invalid_file", message: (err as Error).message });
      }
      return next();
    });
  },
  validatePackageHandler
);

export default router;
