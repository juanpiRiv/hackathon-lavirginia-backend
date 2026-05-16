import multer from "multer";
import { env } from "../config/env";

const ALLOWED_MIMETYPES = [
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/heic",
  "image/heif",
];

export const uploadSingle = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: env.maxImageSizeMb * 1024 * 1024,
  },
  fileFilter: (_req, file, cb) => {
    if (!ALLOWED_MIMETYPES.includes(file.mimetype)) {
      return cb(new Error(`Invalid file type: only ${ALLOWED_MIMETYPES.join(", ")} allowed`));
    }
    cb(null, true);
  },
}).single("image");
