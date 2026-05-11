"""Typed views over the raw `/getReadings` JSON dict.

Each submodule covers one category from the official `getReadings.xlsx`
field spec. Views are constructed by `myviolet.readings.VioletReadings`
from the raw dict and exposed as lazy memoized properties.
"""

from ._common import MeasuredValue, OutputBase

__all__ = ["MeasuredValue", "OutputBase"]
