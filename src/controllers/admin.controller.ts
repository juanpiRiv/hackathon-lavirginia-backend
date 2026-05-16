import { Request, Response } from "express";

export function getProfile(req: Request, res: Response) {
  return res.status(200).json({ user: req.user });
}
