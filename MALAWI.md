uv run skinny-wms -f /tmp/out.grib --host 0.0.0.0

constant_in_time for z og lsm

uv pip install --target backend/.fiab/tools/ptxas-cu129   --index-strategy unsafe-best-match   "nvidia-cuda-nvcc-cu12==12.9.86"


## Actually works

```bash
git clone git@github.com:vegardb/forecast-in-a-box.git
cd forecast-in-a-box
git checkout malawi
mkdir -p backend/.fiab/data_dir
cd graceful-gazelle/
./wrap_artifact_json.sh ~/src/graceful-gazelle_r4_inference_step18000-harrison.ckpt
cp config.toml ../backend/.fiab/
cd ..
uv pip install --target backend/.fiab/tools/ptxas-cu129   --index-strategy unsafe-best-match   "nvidia-cuda-nvcc-cu12==12.9.86"
./run.sh
```

On oldes installs, maybe remove `backend/.fiab/` and `backend/.venv` first.


Will need a late version of anemoi-inference?
* Wrapping around zero meridian

WMS: GRIB files must go into their own folder — one per run. Use the simulation ID.



## Bugs

* If the checkpoint does not exist when it is downloaded, no error message is shown.
