uv run skinny-wms -f /tmp/out.grib --host 0.0.0.0

constant_in_time for z og lsm

uv pip install --target backend/.fiab/tools/ptxas-cu129   --index-strategy unsafe-best-match   "nvidia-cuda-nvcc-cu12==12.9.86"


## Actually worked

```bash
rm -rf backend/.fiab/
rm -rf backend/.venv
just dev
cd graceful-gazelle/
ll
./wrap_artifact_json.sh ~/src/graceful-gazelle_r4_inference_step18000-harrison.ckpt
cp config.toml ../backend/.fiab/
cd ..
just dev
./run.sh
cd backend/
uv pip install --target .fiab/tools/ptxas-cu129   --index-strategy unsafe-best-match   "nvidia-cuda-nvcc-cu12==12.9.86"
cd --
cd -
cd ..
./run.sh
```

## Experiment

```bash
rm -rf backend/.fiab/ backend/.venv
just dev
cd graceful-gazelle/
./wrap_artifact_json.sh ~/src/graceful-gazelle_r4_inference_step18000-harrison.ckpt
cp config.toml ../backend/.fiab/
cd ../backend/
uv pip install --target .fiab/tools/ptxas-cu129   --index-strategy unsafe-best-match   "nvidia-cuda-nvcc-cu12==12.9.86"
cd ..
./run.sh
```

Av en eller annen grunn virker ikke wms når filer havner i /tmp
* Årsak: en tilfeldig grib-fil velges for visning


Siste versjon av anemoi-inference trengs?

WMS: Grib-filer må inn i egen folder - en for hver run. Bruk simulation-id.



## Bugs

* Hvis checkpoint ikke fins når det lastes ned, så får man ingen feilmelding.
