FROM python:3.11-slim

# Faster, cleaner Python in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ---- System dependencies ----
# ffmpeg for MoviePy (stitch), clean apt caches to keep image small
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# ---- Python dependencies ----
# Upgrade pip tooling first
RUN python -m pip install --upgrade pip setuptools wheel

# If you have a pyproject with deps, you can `COPY pyproject.toml` and `pip install .`
# Install runtime deps explicitly (pin moviepy to stable 1.x and include its deps)
RUN pip install --no-cache-dir \
      "uvicorn[standard]" \
      fastapi \
      "pydantic>=2" \
      sqlmodel \
      sqlalchemy \
      "psycopg[binary]" \
      openai \
      "moviepy<2.0" \
      imageio \
      imageio-ffmpeg \
      numpy \
      "pillow>=10.0.0" \
      proglog \
      ffmpeg-python \
      "google-cloud-storage>=2.16.0"

# Sanity check imports at build time (fail fast if missing) - avoid Dockerfile heredoc for Cloud Build
RUN python -c "import sys; import moviepy, imageio_ffmpeg, numpy, PIL; print('OK: moviepy', getattr(moviepy, '__version__', '?'))"

# ---- App source ----
COPY app ./app

# Ensure media directory exists for StaticFiles mount
RUN mkdir -p /tmp/media

# Cloud Run provides $PORT; default to 8080 for local runs
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
