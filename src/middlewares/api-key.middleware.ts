import { timingSafeEqual } from "crypto";
import { Request, Response, NextFunction } from "express";
import { env } from "../config/env";

export function requireValidatorApiKey(req: Request, res: Response, next: NextFunction) {
  const apiKey = req.headers["x-api-key"];

  const unauthorized = () =>
    res.status(401).json({ error: "unauthorized", message: "Invalid or missing API key" });

  if (typeof apiKey !== "string") return unauthorized();

  const expected = Buffer.from(env.validatorApiKey);
  const received = Buffer.from(apiKey);

  if (expected.length !== received.length || !timingSafeEqual(expected, received)) {
    return unauthorized();
  }

  return next();
}
