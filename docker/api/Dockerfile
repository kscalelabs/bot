
# Dockerfile for the FastAPI application.

FROM ubuntu:22.04

WORKDIR /app

# Installs system packages.
RUN apt-get update -y && \
    apt-get install -y \
        ffmpeg \
        curl \
        gcc \
        make \
        python3.11 \
        python3.11-dev \
        python3.11-distutils \
        python3.11-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Installs Pip for Python 3.11.
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.11 get-pip.py && \
    rm get-pip.py

# Copies over code.
ADD bot/ bot/
ADD tests/ tests/
COPY pyproject.toml .
COPY setup.py .
COPY setup.cfg .
COPY README.md .

# Removes any existing Pip packages.
RUN rm -rf ~/.cache/pip

# Installs the package.
RUN pip install --no-cache-dir '.[dev]'

# Runs unit tests.
RUN python3.11 -m pytest

# Exposes the port for FastAPI.
EXPOSE 8000

# Command to run Gunicorn.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "bot.api.app.main:app", "--worker-class", "uvicorn.workers.UvicornWorker"]
