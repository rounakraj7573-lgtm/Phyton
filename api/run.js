import { Sandbox } from "@vercel/sandbox";

const MAX_CODE_CHARS = 12000;
const MAX_OUTPUT_CHARS = 16000;
const ALLOWED_ORIGINS = (process.env.ALLOWED_ORIGINS || "")
  .split(",").map((value) => value.trim()).filter(Boolean);

export default async function handler(request, response) {
  response.setHeader("Cache-Control", "no-store");
  const origin = request.headers.origin;

  if (origin && ALLOWED_ORIGINS.length && !ALLOWED_ORIGINS.includes(origin)) {
    return response.status(403).json({ error: "Origin not allowed." });
  }
  if (request.method === "OPTIONS") {
    if (origin && ALLOWED_ORIGINS.includes(origin)) {
      response.setHeader("Access-Control-Allow-Origin", origin);
      response.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
      response.setHeader("Access-Control-Allow-Headers", "Content-Type");
    }
    return response.status(204).end();
  }
  if (request.method !== "POST") {
    response.setHeader("Allow", "POST, OPTIONS");
    return response.status(405).json({ error: "Use POST." });
  }

  try {
    const body = request.body && typeof request.body === "object"
      ? request.body
      : {};
    const code = body.code;
    if (typeof code !== "string" || !code.trim()) {
      return response.status(400).json({ error: "Enter Python code first." });
    }
    if (code.length > MAX_CODE_CHARS) {
      return response.status(413).json({ error: "Code is too long (12,000 characters maximum)." });
    }

    const sandbox = await Sandbox.create({
      runtime: "python3.13",
      timeout: 30000
    });

    try {
      await sandbox.writeFiles([{
        path: "/vercel/sandbox/main.py",
        content: Buffer.from(code, "utf8")
      }]);
      const result = await sandbox.runCommand({
        cmd: "python",
        args: ["-I", "/vercel/sandbox/main.py"]
      });
      const stdout = (await result.stdout()).slice(0, MAX_OUTPUT_CHARS);
      const stderr = (await result.stderr()).slice(0, MAX_OUTPUT_CHARS);
      const payload = {
        stdout,
        stderr,
        exit_code: result.exitCode
      };
      if (origin && ALLOWED_ORIGINS.includes(origin)) {
        response.setHeader("Access-Control-Allow-Origin", origin);
        response.setHeader("Vary", "Origin");
      }
      return response.status(200).json(payload);
    } finally {
      await sandbox.stop().catch(() => {});
    }
  } catch (error) {
    console.error("Python execution failed:", error);
    return response.status(500).json({
      error: "Python runner could not start. Check the Vercel Sandbox setup and logs."
    });
  }
}
