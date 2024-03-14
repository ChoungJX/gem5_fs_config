import argparse
import sys
from pathlib import Path

import m5
from m5 import options
from m5.objects import *
from m5.params import *
from m5.util import addToPath

addToPath("../../")

import shutil

from component.cachehierarchy.three_level_cache_hierarchy import (
    ThreeLevelCacheHierarchy,
)
from component.processors.core import TunedCPU

from gem5.components.boards.mem_mode import MemMode
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_core import SimpleCore
from gem5.components.processors.switchable_processor import SwitchableProcessor
from gem5.isas import ISA
from gem5.resources.resource import BinaryResource
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
requires(isa_required=ISA.ARM)
class TunedCore(BaseCPUCore):
    def __init__(self, cpu_type: CPUTypes, core_id):
        super().__init__(core=TunedCPU(cpu_id=core_id), isa=ISA.ARM)

        self._cpu_type = cpu_type

    def get_type(self) -> CPUTypes:
        return self._cpu_type



memory = DualChannelDDR4_2400(size="2GB")

from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
class SkylakeProcessor(BaseCPUProcessor):
    def __init__(self):
        self._cpu_type = CPUTypes.O3
        skylakecore = [
            TunedCore(
                cpu_type=CPUTypes.TIMING,
                core_id=0,
            )
        ]

        super().__init__(cores=skylakecore)

from gem5.components.boards.simple_board import SimpleBoard

board = SimpleBoard(
    clk_freq="3GHz",
    processor=SkylakeProcessor(),
    memory=memory,
    cache_hierarchy=ThreeLevelCacheHierarchy(),
)

board.set_mem_mode(MemMode.TIMING)
binary = '/home/jinlin/mini_redis_arm/sort'
board.set_se_binary_workload(BinaryResource(local_path=binary),arguments=[100])

simulator = Simulator(
    board=board,
    full_system=False
)

simulator.run()