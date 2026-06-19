# NoseCheck - Docker build for Render
#
# Why this exists: Render's native Python runtime has a read-only build
# filesystem, so `apt-get install` fails there (E: ... Read-only file
# system). MediaPipe needs a few OpenGL ES system libraries
# (libGLESv2.so.2 and friends) that aren't present in that environment.
# Switching to Render's Docker runtime gives us a normal Linux image where
# we control the base layers and CAN install system packages, which is the
# officially supported way to handle this on Render.

FROM python:3.9-slim

WORKDIR /app

# System libraries MediaPipe needs for its internal OpenGL ES / EGL usage,
# even though we use the "headless" OpenCV package. Without these, the app
# crashes with: "libGLESv2.so.2: cannot open shared object file"
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgles2 \
    libegl1 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching: this only
# re-runs when requirements-production.txt changes, not on every code edit)
COPY requirements-production.txt .
RUN pip install --no-cache-dir -r requirements-production.txt

# Download the MediaPipe Face Landmarker model at build time
RUN mkdir -p models && curl -sL -o models/face_landmarker.task \
    https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task

# Now copy the rest of the application code
COPY . .

# Render provides $PORT at runtime; gunicorn binds to it here
ENV WEB_CONCURRENCY=1
EXPOSE 10000

CMD gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:application
