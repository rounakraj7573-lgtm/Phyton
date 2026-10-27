# PyStudio Python Runner (Docker host required)

This service executes submitted Python code in a disposable Docker container.
It is designed for a dedicated host with Docker installed; it is **not** a
normal Vercel serverless function. Do not expose it publicly until TLS,
origin allow-listing, request limits, monitoring, and host-level isolation are
configured.

## Build the runner image

From the repository root:

```sh
docker build -t pystudio-python-runner:latest -f backend/Runner.Dockerfile .
```

## Install and start the API

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
ALLOWED_ORIGINS=https://YOUR-VERCEL-DOMAIN.vercel.app uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The API host must have access to the Docker daemon and the runner image built
above. Use a dedicated VM/host; Docker access is highly privileged. Put the API
behind HTTPS and a managed rate limiter, and configure the exact deployed
frontend origin in `ALLOWED_ORIGINS`.

- `GET /health` checks service status.
- `POST /run` JSON body: `{"code":"print('Hello')"}`.
- Responses contain `stdout`, `stderr`, and `exit_code`.

The runner includes common packages (NumPy, Pandas, Matplotlib, SciPy, SymPy,
scikit-learn, Pillow, Requests). This is not every PyPI package. Add vetted
dependencies to `Runner.Dockerfile` and rebuild the image when needed.

The frontend still needs the deployed API URL configured before browser runs
are routed here. Do not put private API keys in frontend JavaScript.
