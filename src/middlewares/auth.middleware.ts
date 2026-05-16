import { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";
import { env } from "../config/env";
import { ADMIN_ROLE } from "../services/auth.service";

export function requireAdminAuth(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ message: "Missing or invalid Authorization header" });
  }

  const token = authHeader.split(" ")[1];

  try {
    const decoded = jwt.verify(token, env.jwtSecret) as {
      sub: string;
      email: string;
      role: string;
    };

    if (decoded.role !== ADMIN_ROLE) {
      return res.status(403).json({ message: "Forbidden" });
    }

    req.user = {
      id: decoded.sub,
      email: decoded.email,
      role: decoded.role
    };

    return next();
  } catch {
    return res.status(401).json({ message: "Invalid or expired token" });
  }
}
