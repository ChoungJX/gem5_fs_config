import argparse

from processors.core import TunedCPU

import m5
from m5.objects import *
from m5.params import *
from m5.util import *

from gem5.components.boards.mem_mode import MemMode
from gem5.components.boards.riscv_board import RiscvBoard
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_core import SimpleCore
from gem5.components.processors.switchable_processor import SwitchableProcessor
from gem5.isas import ISA
from gem5.resources.resource import (
    BootloaderResource,
    DiskImageResource,
    KernelResource,
)
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires

# from cachehierarchy.three_level_cache_hierarchy import ThreeLevelCacheHierarchy
# from gem5.components.cachehierarchies.ruby.caches.prebuilt.octopi_cache.octopi import OctopiCache
# from board import SkylakeARMBoard


# m5.disableAllListeners()

parser = argparse.ArgumentParser(description="test")

parser.add_argument(
    "--number",
    default=1,
    action="store",
    type=int,
    help="Rank of this system within the dist gem5 run.",
)

print(parser.parse_args().number)


requires(isa_required=ISA.RISCV)

from cachehierarchy.three_level_cache_hierarchy import ThreeLevelCacheHierarchy

cache_hierarchy = ThreeLevelCacheHierarchy()


# addToPath("../")
# import configs.ruby.MESI_Two_Level
# test_cache = configs.ruby.MESI_Two_Level.create_system(full_system=True)

# test_cache = OctopiCache(
#     l1d_size="32kB",
#     l1d_assoc=8,
#     l1i_size="32kB",
#     l1i_assoc=8,
#     l2_size="1MB",
#     l2_assoc=16,
#     l3_size="12MB",
#     l3_assoc=16,
#     num_core_complexes=2,
#     is_fullsystem=True
# )

memory = DualChannelDDR4_2400(size="3GB")


class TunedCore(BaseCPUCore):
    """
    An out of order core for X86.
    The LSQ depth (split equally between loads and stores), the width of the
    core, and the number of entries in the reorder buffer are configurable.
    """

    def __init__(self, cpu_type: CPUTypes, core_id):
        super().__init__(core=TunedCPU(cpu_id=core_id), isa=ISA.RISCV)

        self._cpu_type = cpu_type

    def get_type(self) -> CPUTypes:
        return self._cpu_type


processor = SwitchableProcessor(
    starting_cores="boot",
    switchable_cores={
        "boot": [
            SimpleCore(cpu_type=CPUTypes.ATOMIC, core_id=0, isa=ISA.RISCV),
            SimpleCore(cpu_type=CPUTypes.ATOMIC, core_id=1, isa=ISA.RISCV),
        ],
        "OoO": [
            TunedCore(
                cpu_type=CPUTypes.TIMING,
                core_id=0,
            ),
            TunedCore(
                cpu_type=CPUTypes.TIMING,
                core_id=1,
            ),
        ],
    },
)


class SkylakeProcessor(BaseCPUProcessor):
    """
    A single core out of order processor for X86.
    The LSQ depth (split equally between loads and stores), the width of the
    core, and the number of entries in the reorder buffer are configurable.
    """

    def __init__(self):
        self._cpu_type = CPUTypes.O3
        skylakecore = [
            TunedCore(
                cpu_type=CPUTypes.TIMING,
                core_id=0,
            ),
            TunedCore(
                cpu_type=CPUTypes.TIMING,
                core_id=1,
            ),
        ]

        super().__init__(cores=skylakecore)


board = RiscvBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
    # cache_hierarchy=test_cache,
)

board.set_mem_mode(MemMode.ATOMIC_NONCACHING)
# board.set_mem_mode(MemMode.TIMING)

# board.etherlink = DistEtherLink(
#     dist_rank=parser.parse_args().number,
#     dist_size=2,
#     server_port=2201,
#     sync_start="1000000000000t",
#     sync_repeat="10us",
#     delay="3ms"
# )

# board.etherlink.int0 = Parent.board.ethernet.interface


if parser.parse_args().number == 0:
    board.set_kernel_disk_workload(
        bootloader=BootloaderResource(
            "/home/linfeng/bin/riscv/opensbi/fw_jump.elf"
        ),
        kernel=KernelResource("/home/linfeng/bin/riscv/opensbi/vmlinux"),
        disk_image=DiskImageResource(
            "/home/linfeng/bin/riscv/riscv-disk.img",
        ),
    )
else:
    board.set_kernel_disk_workload(
        bootloader=BootloaderResource(
            "/home/linfeng/bin/riscv/opensbi/fw_jump.elf"
        ),
        kernel=KernelResource("/home/linfeng/bin/riscv/opensbi/vmlinux"),
        disk_image=DiskImageResource(
            "/home/linfeng/bin/riscv/riscv-disk.img",
        ),
    )


def begin_workload():
    processor.switch_to_processor("OoO")
    board.set_mem_mode(MemMode.TIMING)


simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.WORKBEGIN: (func() for func in [begin_workload]),
    },
)


simulator.run()
