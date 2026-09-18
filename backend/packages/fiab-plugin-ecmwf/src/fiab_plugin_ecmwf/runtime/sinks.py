import json
import logging
import pathlib

import earthkit.data

logger = logging.getLogger(__name__)


def write_zarr(fieldlist: earthkit.data.SimpleFieldList, path: str) -> bytes:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fieldlist.to_target("zarr", xarray_to_zarr_kwargs={"store": path, "mode": "w"})
    return path.encode("ascii")


def write_grib(fieldlist: earthkit.data.SimpleFieldList, path: str) -> bytes:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    formatted_path = path.replace("[", "{").replace("]", "}")
    fieldlist.to_target("file-pattern", formatted_path)
    # Returning the parent directory as file-pattern may write multiple files
    return str(p.parent).encode("ascii")


def log_dataset(fieldlist: earthkit.data.SimpleFieldList) -> bytes:
    summary = {
        "count": len(fieldlist),
        "fields": fieldlist.ls().to_dict(orient="records"),
    }
    encoded = json.dumps(summary, indent=2, default=str).encode("utf-8")
    logger.info("DummySink received %d field(s)", summary["count"])
    return encoded
