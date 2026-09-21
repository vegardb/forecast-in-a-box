# (C) Copyright 2026- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from fiab_core.fable import BlockFactoryId
from fiab_core.tools.blocks import QubedBlockBuilder
from fiab_core.tools.plugins import QubedPluginBuilder

from fiab_plugins_dev.blocks import DummySink

blocks: dict[BlockFactoryId, QubedBlockBuilder] = {
    BlockFactoryId("dummySink"): DummySink(),
}

plugin = QubedPluginBuilder(block_builders=blocks, base_environment=["fiab-plugins-dev"]).as_plugin()
