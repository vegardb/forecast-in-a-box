# Running on NVIDIA GB10 (DGX Spark)

Notes for running forecast-in-a-box with GPU inference on an NVIDIA GB10
(DGX Spark), aarch64, compute capability 12.1 (`sm_121a`). This hardware is
new enough that a few things need extra configuration compared to a regular
x86_64 + CUDA setup. None of this is GB10-specific in principle, it should
apply to any recent Blackwell aarch64 GPU that hits the same issues.

## 1. CPU-only torch on aarch64

Plain PyPI only ships a CPU-only `torch` wheel for aarch64. To get a
CUDA-enabled build, point the resolver at the PyTorch CUDA wheel index and
pin the checkpoint's `torch` constraint to the matching `+cuXXX` local
version, for example `torch==2.8.0+cu129`.

In `backend/.fiab/config.toml`:

```toml
[cascade.constraints]
custom_pip_indices = ["https://download.pytorch.org/whl/cu129"]
```

And in the relevant checkpoint's `pip_package_constraints` (in an artifacts
JSON such as `backend/.fiab/local_artifacts.json`):

```
"torch==2.8.0+cu129"
```

## 2. `uv` picks up a stale `setuptools` from the cu129 index

`download.pytorch.org/whl/cu129` also mirrors an old `setuptools`. With
`uv`'s default index strategy (`first-index`), resolution can get stuck on
that stale version and fail to build packages that need a newer
`setuptools`. Work around this by setting, in the shell that runs `just dev`
(or however the backend is launched):

```sh
export UV_INDEX_STRATEGY=unsafe-best-match
```

This is inherited by cascade's `uv pip install` subprocess calls used to
build each job's worker venv.

## 3. One GPU, but more than one worker per host

Cascade only assigns a GPU to workers with `worker_num < gpu_count`. If you
have a single physical GPU (check with `nvidia-smi --list-gpus`) but
`workers_per_host` is greater than 1, the extra worker(s) get no GPU and any
GPU-only op will crash trying to run on the CPU. Set, in
`backend/.fiab/config.toml`:

```toml
[cascade.constraints]
default_workers_per_host = 1
```

(Adjust upward only if you actually have that many GPUs on the host.)

## 4. `ptxas` doesn't support `sm_121a`

The `ptxas` bundled inside `triton`'s own wheel (pulled in transitively by
`torch==2.8.0+cu129`) is built against an older CUDA toolkit and does not
recognize the `sm_121a` target that GB10/Blackwell needs. This surfaces as:

```
PTXASError: Internal Triton PTX codegen error
`ptxas` stderr:
ptxas fatal   : Value 'sm_121a' is not defined for option 'gpu-name'
```

This is not fixed by upgrading `torch`/`triton` alone: as of writing,
`triton` up to at least 3.7.x still bundles a CUDA 12.8 `ptxas`. The fix is
to install a newer, standalone `ptxas` (via the `nvidia-cuda-nvcc-cu12`
package, which does have a CUDA 12.9 `ptxas` that supports `sm_120a` /
`sm_121a`) and point triton at it via the `TRITON_PTXAS_PATH` environment
variable.

Because each cascade job builds its own throwaway worker venv at a random
path (`/tmp/cascade_worker_venv_XXXX`), don't try to install this per job
venv. Instead, install it once to a fixed location outside of any venv, and
point `TRITON_PTXAS_PATH` at that fixed path. Since `ptxas` is invoked as a
plain subprocess (not imported as a Python module), it works regardless of
which worker venv/Python is active, as long as the path is inherited in the
process environment.

```sh
uv pip install --target backend/.fiab/tools/ptxas-cu129 \
  --index-strategy unsafe-best-match \
  "nvidia-cuda-nvcc-cu12==12.9.86"
```

Then, in the same shell that runs `just dev`:

```sh
export TRITON_PTXAS_PATH="$(pwd)/backend/.fiab/tools/ptxas-cu129/nvidia/cuda_nvcc/bin/ptxas"
```

You can sanity-check the installed `ptxas` supports the target arch with:

```sh
backend/.fiab/tools/ptxas-cu129/nvidia/cuda_nvcc/bin/ptxas --help | grep -o 'sm_12[0-9]a\?' | sort -u
```

which should list `sm_120`, `sm_120a`, `sm_121`, `sm_121a`.

## Putting it together

A typical shell setup for `just dev` on a GB10 box, on top of the
`backend/.fiab/config.toml` changes from sections 1 and 3 above:

```sh
export UV_INDEX_STRATEGY=unsafe-best-match
export TRITON_PTXAS_PATH="$(pwd)/backend/.fiab/tools/ptxas-cu129/nvidia/cuda_nvcc/bin/ptxas"
just dev
```
