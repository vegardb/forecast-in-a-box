# (C) Copyright 2026- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import json
import logging

import earthkit.data

logger = logging.getLogger(__name__)


def log_dataset(fieldlist: earthkit.data.SimpleFieldList) -> bytes:
    summary = {
        "count": len(fieldlist),
        "fields": fieldlist.ls().to_dict(orient="records"),
    }
    encoded = json.dumps(summary, indent=2, default=str).encode("utf-8")
    logger.info("DummySink received %d field(s)", summary["count"])
    return encoded
