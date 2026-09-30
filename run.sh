#!/bin/bash


set -euo pipefail


SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# export TRITON_PTXAS_PATH=/usr/local/cuda/bin/ptxas
# export TRITON_PTXAS_PATH=/home/vegardb/src/github.com/ecmwf/forecast-in-a-box/backend/.venv/lib/python3.11/site-packages/triton/backends/nvidia/bin/ptxas
export TRITON_PTXAS_PATH="${SCRIPT_DIR}/backend/.fiab/tools/ptxas-cu129/nvidia/cuda_nvcc/bin/ptxas"

export UV_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cu129
export UV_INDEX_STRATEGY=unsafe-best-match

pushd "${SCRIPT_DIR}/backend" > /dev/null
uv sync --extra runtime --all-packages

# TEMPORARY WORKAROUND: nvidia-cusparselt-cu13 ships a manylinux "sbsa"
# (server base system architecture) platform tag, which is aarch64 in
# practice but is not recognized as compatible by `uv pip check`. This makes
# `uv pip check` report a false-positive incompatibility, which blocks
# forecastbox's plugin-install/warmup subprocess (see
# backend/src/forecastbox/domain/plugin/compatibility.py::check_environment_baseline).
# Rewrite the recorded wheel tag to the equivalent generic aarch64 tag so `uv
# pip check` treats it as compatible. This only edits installed package
# metadata (no binaries are touched), and needs to be reapplied after every
# `uv sync`, hence it lives here rather than being a one-off manual edit.
for wheel_file in .venv/lib/python3.*/site-packages/nvidia_cusparselt_cu13-*.dist-info/WHEEL ; do
    if [ -f "$wheel_file" ] ; then
        sed -i -E 's/manylinux2014_sbsa/manylinux2014_aarch64/' "$wheel_file"
    fi
done
popd > /dev/null

just dev #full-reinstall
