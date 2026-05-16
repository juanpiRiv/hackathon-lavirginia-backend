import jwt from "jsonwebtoken";
import { prisma } from "../config/prisma";
import { env } from "../config/env";
import { AdminModel } from "../models/admin.model";

export const ADMIN_ROLE = "ADMIN";
const DEFAULT_OTP_CODE = "123456";

export async function requestAdminOtp(email: string) {
  const user = await prisma.user.findUnique({ where: { email } });

  if (!user || user.role !== ADMIN_ROLE) {
    return null;
  }

  const expiresAt = new Date(Date.now() + 10 * 60 * 1000);

  await prisma.otp.create({
    data: {
      email,
      code: DEFAULT_OTP_CODE,
      expiresAt,
      userId: user.id
    }
  });

  return {
    expiresAt,
    otpCode: DEFAULT_OTP_CODE
  };
}

export async function verifyAdminOtp(email: string, code: string) {
  const user = await prisma.user.findUnique({ where: { email } });

  if (!user || user.role !== ADMIN_ROLE) {
    return null;
  }

  const otp = await prisma.otp.findFirst({
    where: {
      email,
      expiresAt: {
        gt: new Date()
      }
    },
    orderBy: {
      createdAt: "desc"
    }
  });

  if (!otp || otp.code !== code) {
    return null;
  }

  await prisma.otp.delete({ where: { id: otp.id } });

  const admin = new AdminModel({ id: user.id, email: user.email, role: user.role });

  const token = jwt.sign(
    {
      sub: admin.id,
      email: admin.email,
      role: admin.role
    },
    env.jwtSecret,
    { expiresIn: "8h" }
  );

  return {
    token,
    user: {
      id: admin.id,
      email: admin.email,
      role: admin.role
    }
  };
}
