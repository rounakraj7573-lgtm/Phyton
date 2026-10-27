import os
import subprocess
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="PyStudio Python Runner", version="1.0.0")

allowed_origins = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

RUNNER_IMAGE = os.getenv("RUNNER_IMAGE", "pystudio-python-runner:latest")
TIME_LIMIT_SECONDS = int(os.getenv("TIME_LIMIT_SECONDS", "5"))
MAX_CODE_CHARS = int(os.getenv("MAX_CODE_CHARS", "12000"))
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
_requests = defaultdict(deque)
_lock = Lock()


class RunRequest(BaseModel):
    code: str = Field(min_length=1, max_length=12000)


@app.get("/health")
def health():
    return {"status": "ok", "runner": RUNNER_IMAGE}


@app.post("/run")
def run_code(body: RunRequest, request: Request):
    code = body.code
    if len(code) > MAX_CODE_CHARS:
        raise HTTPException(status_code=413, detail="Code is too long.")

    # Basic per-IP rate limit. Use a managed gateway/WAF for production scale.
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    with _lock:
        bucket = _requests[ip]
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Too many runs. Wait a minute and try again.")
        bucket.append(now)

    # Every run gets a disposable, unprivileged container with no network,
    # a read-only root filesystem, strict resource limits, and no capabilities.
    command = [
        "docker", "run", "--rm", "-i",
        "--network", "none",
        "--memory", "192m", "--memory-swap", "192m",
        "--cpus", "0.5", "--pids-limit", "64",
        "--read-only", "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
        "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
        "--user", "65534:65534",
        RUNNER_IMAGE, "python", "-I", "-c", code,
    ]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=TIME_LIMIT_SECONDS,
            input="", check=False,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail=f"Execution timed out after {TIME_LIMIT_SECONDS} seconds.")
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Python runner is not configured on this host.")

    return {
        "stdout": result.stdout[-20000:],
        "stderr": result.stderr[-12000:],
        "exit_code": result.returncode,
    }
