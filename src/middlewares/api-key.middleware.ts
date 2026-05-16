import { Request, Response, NextFunction } from "express";
import { env } from "../config/env";

export function requireValidatorApiKey(req: Request, res: Response, next: NextFunction) {
  const apiKey = req.headers["x-api-key"];

  if (!apiKey || apiKey !== env.validatorApiKey) {
    return res.status(401).json({
      error: "unauthorized",
      message: "Invalid or missing API key"
    });
  }

  return next();
}
