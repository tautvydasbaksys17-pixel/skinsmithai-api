# GPU-enabled Docker for Hugging Face Spaces (Docker type)
# Uses CUDA 12.1 runtime + Python 3.10

FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Python setup
RUN python3 -m pip install --upgrade pip

# (A) Install PyTorch with CUDA wheels
RUN pip install --extra-index-url https://download.pytorch.org/whl/cu121 \
    torch torchvision torchaudio

# (B) App deps
WORKDIR /workspace
COPY requirements.txt /workspace/requirements.txt
RUN pip install -r requirements.txt

# Optional speed boost
ENV DIFFUSERS_USE_XFORMERS=1
# xformers needs a build on CUDA 12; skip if it fails gracefully
RUN pip install xformers==0.0.27.post2 || true

# (C) Copy app
COPY app.py /workspace/app.py

# Expose API on 7860 (HF default) -> we’ll run uvicorn on 7860
EXPOSE 7860

CMD ["python3", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
