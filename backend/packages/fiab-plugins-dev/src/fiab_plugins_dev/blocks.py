# (C) Copyright 2026- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from cascade.low.func import Either
from earthkit.workflows.fluent import Action, Payload
from earthkit.workflows.nodetree import nodetree_new_dimension
from fiab_core.fable import (
    ActionLookup,
    BlockConfigurationOption,
    BlockInstanceOutput,
    ConfigurationOptionId,
    ConfigurationOptionRestriction,
    QubedOutput,
    RawOutput,
)
from fiab_core.plugin import Error
from fiab_core.tools.blocks import BlockInstanceConfigurationError, BlockInstanceRich, Sink


def _extract_dataset(inputs: dict[str, QubedOutput], name: str) -> QubedOutput:
    input_dataset = inputs.get(name)
    if not isinstance(input_dataset, QubedOutput):
        actual_type = type(input_dataset).__name__ if input_dataset is not None else "None"
        raise BlockInstanceConfigurationError(f"Unsupported input type for '{name}': expected QubedOutput, got {actual_type}")
    return input_dataset


def _dimensions(qube: QubedOutput) -> set[str]:
    return set(qube.dataqube.axes().keys())


class DummySink(Sink):
    title: str = "Dummy Sink"
    description: str = "Does nothing but produce a JSON summary of its input - useful for testing"
    configuration_options: dict[ConfigurationOptionId, BlockConfigurationOption] = {}
    inputs: list[str] = ["dataset"]

    def validate(
        self, block: BlockInstanceRich, inputs: dict[str, QubedOutput], restrictions: ConfigurationOptionRestriction
    ) -> BlockInstanceOutput:
        _extract_dataset(inputs, "dataset")  # check format of input and existence of dataset
        return RawOutput(type_fqn="bytes", mime_type="application/json")

    def compile(
        self,
        inputs: ActionLookup,
        block: BlockInstanceRich,
    ) -> Either[Action, Error]:  # type:ignore[invalid-argument] # semigroup
        input_task = block.input_ids["dataset"]

        temp_dim = nodetree_new_dimension(inputs[input_task].nodes)
        action = (
            inputs[input_task]
            .flatten(new_dim=temp_dim, reset_coords=True)
            .combine_branches(dim=temp_dim)
            .concatenate(dim=temp_dim)
            .map(Payload("fiab_plugins_dev.runtime.sinks.log_dataset"))
        )
        return Either.ok(action)

    def intersect(self, other: QubedOutput) -> bool:
        return bool(_dimensions(other))
