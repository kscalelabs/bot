# Use the latest CUDA image as base.

FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

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

# Copies over and installs requirements file first.
COPY bot/requirements.txt .
RUN pip install -r requirements.txt

# Copies over code.
ADD bot/ bot/
COPY pyproject.toml .
COPY setup.py .
COPY setup.cfg .
COPY README.md .
COPY docker/worker/startup.sh ./startup.sh

# Installs the package.
RUN pip install '.'

# Exposes the port for FastAPI.
EXPOSE 8000

# Command to run database migrations.
ENTRYPOINT ["./startup.sh"]
