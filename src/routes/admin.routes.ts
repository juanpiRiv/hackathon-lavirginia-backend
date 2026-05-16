import { Router } from "express";
import { getProfile } from "../controllers/admin.controller";
import { requireAdminAuth } from "../middlewares/auth.middleware";

const router = Router();

router.get("/me", requireAdminAuth, getProfile);

export default router;
