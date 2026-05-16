import { Request, Response, NextFunction } from "express";
import { requestAdminOtp, verifyAdminOtp } from "../services/auth.service";

export async function requestOtp(req: Request, res: Response, next: NextFunction) {
  try {
    const { email } = req.body as { email?: string };

    if (!email) {
      return res.status(400).json({ message: "email is required" });
    }

    const challenge = await requestAdminOtp(email);
    if (!challenge) {
      return res.status(401).json({ message: "Invalid admin user" });
    }

    return res.status(200).json({
      message: "OTP generated",
      expiresAt: challenge.expiresAt,
      otpCode: challenge.otpCode
    });
  } catch (error) {
    return next(error);
  }
}

export async function verifyOtp(req: Request, res: Response, next: NextFunction) {
  try {
    const { email, code } = req.body as { email?: string; code?: string };

    if (!email || !code) {
      return res.status(400).json({ message: "email and code are required" });
    }

    const session = await verifyAdminOtp(email, code);
    if (!session) {
      return res.status(401).json({ message: "Invalid or expired OTP" });
    }

    return res.status(200).json(session);
  } catch (error) {
    return next(error);
  }
}
