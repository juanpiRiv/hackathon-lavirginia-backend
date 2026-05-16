import express, { NextFunction, Request, Response } from "express";
import authRoutes from "./routes/auth.routes";
import adminRoutes from "./routes/admin.routes";

const app = express();

app.use(express.json());

app.get("/health", (_req: Request, res: Response) => {
  return res.status(200).json({ ok: true, service: "lavirginia-backend" });
});

app.use("/api/auth", authRoutes);
app.use("/api/admin", adminRoutes);

app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  return res.status(500).json({ message: err.message || "Internal Server Error" });
});

export default app;
