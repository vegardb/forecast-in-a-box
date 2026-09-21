# (C) Copyright 2026- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import pytest
from fiab_core.fable import BlockFactoryId, BlockInstance, BlockInstanceId, QubedOutput, RawOutput
from fiab_core.tools.blocks import BlockInstanceRich
from qubed import Qube

from fiab_plugins_dev import plugin
from fiab_plugins_dev.blocks import DummySink

EXPECTED_FACTORY_IDS = {
    BlockFactoryId("dummySink"),
}


def _block() -> BlockInstance:
    return BlockInstance(
        input_ids={"dataset": BlockInstanceId("source_output")},
        configuration_values={},
    )


def _rich_block(factory_id: BlockFactoryId, builder: DummySink) -> BlockInstanceRich:
    return BlockInstanceRich.from_block(factory_id, _block(), builder.configuration_options)


@pytest.fixture
def dummy_output() -> QubedOutput:
    return QubedOutput(
        dataqube=Qube.from_datacube(
            {
                "param": ["2t", "msl"],
                "step": [0, 6, 12],
            }
        )
    )


def test_plugin_catalogue_contains_dummy_sink() -> None:
    assert set(plugin().catalogue.factories.keys()) == EXPECTED_FACTORY_IDS


def test_plugin_expands_qubed_output_to_dummy_sink(dummy_output: QubedOutput) -> None:
    assert {expansion.factory for expansion in plugin().expander(dummy_output)} == EXPECTED_FACTORY_IDS


def test_dummy_sink_intersects_dataset_with_dimensions(dummy_output: QubedOutput) -> None:
    block = DummySink()
    assert block.intersect(other=dummy_output)  # type: ignore[arg-type]


def test_dummy_sink_does_not_intersect_dimensionless_dataset() -> None:
    block = DummySink()
    assert not block.intersect(other=QubedOutput())  # type: ignore[arg-type]


def test_dummy_sink_validate_returns_json_raw_output(dummy_output: QubedOutput) -> None:
    factory_id = BlockFactoryId("dummySink")
    block = DummySink()
    rich_block = _rich_block(factory_id, block)
    output = block.validate(block=rich_block, inputs={"dataset": dummy_output}, restrictions={})
    assert isinstance(output, RawOutput)
    assert output.mime_type == "application/json"


def test_dummy_sink_validate_requires_dataset() -> None:
    factory_id = BlockFactoryId("dummySink")
    block = DummySink()
    rich_block = _rich_block(factory_id, block)
    with pytest.raises(Exception, match="Unsupported input type for 'dataset'"):
        block.validate(block=rich_block, inputs={}, restrictions={})
