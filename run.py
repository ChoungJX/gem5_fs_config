import argparse
import sys
from pathlib import Path
from typing import Optional

from cachehierarchy.three_level_cache_hierarchy import ThreeLevelCacheHierarchy
from processors.corenoSMT import TunedCPU

import m5
from m5.objects import *
from m5.params import *

from gem5.components.boards.mem_mode import MemMode
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
from gem5.components.processors.cpu_types import (
    CPUTypes,
    get_mem_mode,
)
from gem5.components.processors.simple_core import SimpleCore
from gem5.components.processors.switchable_processor import SwitchableProcessor
from gem5.isas import ISA
from gem5.resources.resource import (
    BootloaderResource,
    CheckpointResource,
    DiskImageResource,
    KernelResource,
)
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires

# from gem5.components.cachehierarchies.ruby.caches.prebuilt.octopi_cache.octopi import OctopiCache
# from board import SkylakeARMBoard


m5.disableAllListeners()

parser = argparse.ArgumentParser(description="test")

parser.add_argument(
    "--number",
    default=1,
    action="store",
    type=int,
    help="Rank of this system within the dist gem5 run.",
)

print(parser.parse_args().number)


requires(isa_required=ISA.ARM)

memory = DualChannelDDR4_2400(size="2GB")


class TunedCore(BaseCPUCore):
    """
    An out of order core for X86.
    The LSQ depth (split equally between loads and stores), the width of the
    core, and the number of entries in the reorder buffer are configurable.
    """

    def __init__(self, cpu_type: CPUTypes, core_id):
        super().__init__(core=TunedCPU(cpu_id=core_id), isa=ISA.ARM)

        self._cpu_type = cpu_type

    def get_type(self) -> CPUTypes:
        return self._cpu_type


processor = SwitchableProcessor(
    starting_cores="OoO",
    switchable_cores={
        "boot": [
            SimpleCore(cpu_type=CPUTypes.ATOMIC, core_id=0, isa=ISA.ARM),
            SimpleCore(cpu_type=CPUTypes.ATOMIC, core_id=1, isa=ISA.ARM),
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


release = ArmDefaultRelease()
platform = VExpress_GEM5_Foundation()


# from cachehierarchy.octopi_cache.octopi import OctopiCache
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


from gem5.components.boards.arm_board import ArmBoard

board = ArmBoard(
    clk_freq="3GHz",
    # processor=processor,
    processor=SkylakeProcessor(),
    memory=memory,
    cache_hierarchy=ThreeLevelCacheHierarchy(),
    # cache_hierarchy=test_cache,
    release=release,
    platform=platform,
)

board.ethernet = IGbE_e1000(
    pci_bus=0, pci_dev=0, pci_func=0, InterruptLine=1, InterruptPin=1
)
board.realview.attachPciDevice(
    board.ethernet, bus=board.get_io_bus(), dma_ports=board.get_dma_ports()
)


board.etherlink = DistEtherLink(
    dist_rank=parser.parse_args().number,
    dist_size=2,
    server_port=2200,
    sync_start="1000000000000t",
    sync_repeat="10us",
    delay="3ms",
    delay_var="1ms",
    num_nodes=21,
)

board.etherlink.int0 = Parent.board.ethernet.interface

board.set_mem_mode(MemMode.ATOMIC_NONCACHING)
# board.set_mem_mode(MemMode.TIMING)


if parser.parse_args().number == 0:
    board.set_kernel_disk_workload(
        kernel=KernelResource(
            "/home/linfeng/.cache/gem5/arm64-linux-kernel-5.4.49"
        ),
        disk_image=DiskImageResource(
            "/home/linfeng/work/arm64-ubuntu-focal-server.img",
            root_partition="1",
        ),
        bootloader=BootloaderResource(
            "/home/linfeng/.cache/gem5/arm64-bootloader-foundation"
        ),
        checkpoint=CheckpointResource(
            "/home/linfeng/work/gem5_debug/m5out/node0/cpt.1000000000000"
        ),
        readfile="fs_config/script/s_server.sh",
    )
else:
    board.set_kernel_disk_workload(
        kernel=KernelResource(
            "/home/linfeng/.cache/gem5/arm64-linux-kernel-5.4.49"
        ),
        disk_image=DiskImageResource(
            "/home/linfeng/work/arm64-ubuntu-focal-server.img",
            root_partition="1",
        ),
        bootloader=BootloaderResource(
            "/home/linfeng/.cache/gem5/arm64-bootloader-foundation"
        ),
        checkpoint=CheckpointResource("m5out/node1/cpt.1000000000000"),
        readfile="fs_config/script/s_client_%s.sh"
        % (parser.parse_args().number),
    )

# We define the system with the aforementioned system defined.


def begin_workload():
    processor.switch_to_processor("OoO")
    board.set_mem_mode(MemMode.TIMING)


def end_workload():
    sys.exit(0)


def save_checkpoint_generator():
    """
    A generator for taking a checkpoint. It will take a checkpoint with the
    input path and the current simulation Ticks.
    The Simulation run loop will continue after executing the behavior of the
    generator.
    """
    while True:
        from m5 import options

        checkpoint_dir = Path(options.outdir)
        m5.checkpoint((checkpoint_dir / f"cpt.{str(m5.curTick())}").as_posix())
        yield False


simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.WORKBEGIN: (func() for func in [begin_workload]),
        ExitEvent.WORKEND: (func() for func in [end_workload]),
        ExitEvent.CHECKPOINT: save_checkpoint_generator(),
    },
)
# simulator = Simulator(board=board,full_system=True)
# Once the system successfully boots, it encounters an
# `m5_exit instruction encountered`. We stop the simulation then. When the
# simulation has ended you may inspect `m5out/board.terminal` to see
# the stdout.

# def unique_exit_event(number):
#     print("trigger cpt")
#     m5.checkpoint("m5out/node%s/test.cpt"%(number))
#     yield False


# simulator = Simulator(board=board,)

simulator.run()


def checkpoint():
    print("Start taking a checkpoint")
    simulator.save_checkpoint("test/ckp")
    print("Done taking a checkpoint")
