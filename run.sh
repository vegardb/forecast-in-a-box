#!/bin/bash


set -euo pipefail

# export TRITON_PTXAS_PATH=/usr/local/cuda/bin/ptxas
# export TRITON_PTXAS_PATH=/home/vegardb/src/github.com/ecmwf/forecast-in-a-box/backend/.venv/lib/python3.11/site-packages/triton/backends/nvidia/bin/ptxas
export TRITON_PTXAS_PATH=/home/vegardb/src/github.com/ecmwf/forecast-in-a-box/backend/.fiab/tools/ptxas-cu129/nvidia/cuda_nvcc/bin/ptxas
export UV_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cu129
export UV_INDEX_STRATEGY=unsafe-best-match

just dev #full-reinstall
