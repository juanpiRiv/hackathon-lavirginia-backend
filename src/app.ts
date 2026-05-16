import path from "path";
import express, { NextFunction, Request, Response } from "express";
import cors from "cors";
import authRoutes from "./routes/auth.routes";
import adminRoutes from "./routes/admin.routes";
import validatorRoutes from "./routes/validator.routes";

const app = express();
const publicDir = path.resolve(__dirname, "../public");

app.use(
  cors({
    origin: process.env.CORS_ORIGIN || "*"
  })
);
app.use(express.json());
app.use("/demo", express.static(publicDir));

app.get("/health", (_req: Request, res: Response) => {
  return res.status(200).json({ ok: true, service: "lavirginia-backend" });
});

app.get("/demo/camera", (_req: Request, res: Response) => {
  return res.sendFile(path.join(publicDir, "camera-demo.html"));
});

app.use("/api/auth", authRoutes);
app.use("/api/admin", adminRoutes);
app.use("/api/validator", validatorRoutes);

app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  return res.status(500).json({ message: err.message || "Internal Server Error" });
});

export default app;
