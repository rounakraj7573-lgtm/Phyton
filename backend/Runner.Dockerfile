FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Common scientific/data libraries. Some packages require platform-specific
# dependencies and not every package on PyPI can be supported.
RUN pip install --no-cache-dir \
    numpy pandas matplotlib scipy sympy scikit-learn pillow requests

USER 65534:65534
WORKDIR /tmp
