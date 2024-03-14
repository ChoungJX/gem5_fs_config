import argparse
import sys
from pathlib import Path
from typing import Optional

from cachehierarchy.three_level_cache_hierarchy import ThreeLevelCacheHierarchy
from processors.core import TunedCPU

import m5
from m5 import options
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

parser.add_argument(
    "--checkpoint",
    default=False,
    action="store",
    type=bool,
    help="If start from a checkpoint",
)

print("--number:", parser.parse_args().number)
print("--checkpoint:", parser.parse_args().checkpoint)


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
    starting_cores="boot",
    switchable_cores={
        "boot": [SimpleCore(cpu_type=CPUTypes.ATOMIC, core_id=0, isa=ISA.ARM)],
        "OoO": [
            TunedCore(
                cpu_type=CPUTypes.TIMING,
                core_id=0,
            )
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
            )
        ]

        super().__init__(cores=skylakecore)


release = ArmDefaultRelease()
platform = VExpress_GEM5_Foundation()


from gem5.components.boards.arm_board import ArmBoard

board = ArmBoard(
    clk_freq="3GHz",
    processor=processor,
    # processor=SkylakeProcessor(),
    memory=memory,
    cache_hierarchy=ThreeLevelCacheHierarchy(),
    # cache_hierarchy=test_cache,
    release=release,
    platform=platform,
)

# board.ethernet = IGbE_e1000(
#     pci_bus=0, pci_dev=0, pci_func=0, InterruptLine=1, InterruptPin=1
# )
# board.realview.attachPciDevice(
#     board.ethernet, bus=board.get_io_bus(), dma_ports=board.get_dma_ports()
# )


# board.etherlink = DistEtherLink(
#     dist_rank=parser.parse_args().number,
#     dist_size=21,
#     server_port=2200,
#     sync_start="1000000000000t",
#     sync_repeat="10us",
#     delay="3ms",
#     delay_var="1ms",
#     num_nodes=21,
# )

# board.etherlink.int0 = Parent.board.ethernet.interface

board.set_mem_mode(MemMode.ATOMIC_NONCACHING)
# board.set_mem_mode(MemMode.TIMING)

import shutil

file_dir = Path("/home/linfeng/work/gem5_debug/fs_config/script/mini-redis")
shutil.copy(
    (file_dir / "client_init.sh"),
    (file_dir / f"client_{parser.parse_args().number}"),
)
shutil.copy((file_dir / "server_init.sh"), (file_dir / "server"))


if parser.parse_args().number == 0:
    if parser.parse_args().checkpoint:
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
            readfile="/home/linfeng/work/gem5_debug/fs_config/script/mini-redis/server",
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
            readfile="/home/linfeng/work/gem5_debug/fs_config/script/mini-redis/server",
        )
else:
    if parser.parse_args().checkpoint:
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
                f"m5out/node{parser.parse_args().number}/cpt.1000000000000"
            ),
            readfile=f"/home/linfeng/work/gem5_debug/fs_config/script/mini-redis/client_{parser.parse_args().number}",
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
            readfile=f"/home/linfeng/work/gem5_debug/fs_config/script/mini-redis/client_{parser.parse_args().number}",
        )

# We define the system with the aforementioned system defined.

if parser.parse_args().number == 0:

    def init_sys():
        print("init_sys")
        import shutil

        file_dir = Path(
            "/home/linfeng/work/gem5_debug/fs_config/script/mini-redis"
        )
        shutil.copy(
            "/home/linfeng/bin/async_test",
            (file_dir / "server"),
        )

    def boot_workload():
        print("boot_workload")
        import shutil

        scr_dir = Path("/home/linfeng/work/gem5_debug/fs_config/script")
        des_dir = Path(
            "/home/linfeng/work/gem5_debug/fs_config/script/mini-redis"
        )
        shutil.copy((scr_dir / f"s_server.sh"), (des_dir / f"server"))

    def begin_workload():
        print("begin_workload")
        processor.switch_to_processor("OoO")
        board.set_mem_mode(MemMode.TIMING)

    def end_workload():
        sys.exit(0)

    def save_checkpoint_generator():
        checkpoint_dir = Path(options.outdir)
        m5.checkpoint((checkpoint_dir / f"cpt.{str(m5.curTick())}").as_posix())

    def test():
        sys.exit(0)

    simulator = Simulator(
        board=board,
        full_system=True,
        on_exit_event={
            ExitEvent.WORKBEGIN: (
                func() for func in [init_sys, boot_workload, begin_workload]
            ),
            ExitEvent.WORKEND: (func() for func in [end_workload]),
            ExitEvent.CHECKPOINT: (
                func() for func in [save_checkpoint_generator]
            ),
            ExitEvent.EXIT: (func() for func in [test]),
        },
    )

    simulator.run()

else:

    def init_sys():
        print("init_sys")
        import shutil

        file_dir = Path(
            "/home/linfeng/work/gem5_debug/fs_config/script/mini-redis"
        )
        shutil.copy(
            "/home/linfeng/bin/mini_redis_arm/mini-redis-cli",
            (file_dir / f"client_{parser.parse_args().number}"),
        )

    def boot_workload():
        print("boot_workload")
        import shutil

        scr_dir = Path("/home/linfeng/work/gem5_debug/fs_config/script")
        des_dir = Path(
            "/home/linfeng/work/gem5_debug/fs_config/script/mini-redis"
        )
        shutil.copy(
            (scr_dir / f"s_client_{parser.parse_args().number}.sh"),
            (des_dir / f"client_{parser.parse_args().number}"),
        )

    def begin_workload():
        print("begin_workload")
        processor.switch_to_processor("OoO")
        board.set_mem_mode(MemMode.TIMING)

    def end_workload():
        sys.exit(0)

    def save_checkpoint_generator():
        checkpoint_dir = Path(options.outdir)
        m5.checkpoint((checkpoint_dir / f"cpt.{str(m5.curTick())}").as_posix())

    def test():
        sys.exit(0)

    simulator = Simulator(
        board=board,
        full_system=True,
        on_exit_event={
            ExitEvent.WORKBEGIN: (
                func() for func in [init_sys, boot_workload, begin_workload]
            ),
            ExitEvent.WORKEND: (func() for func in [end_workload]),
            ExitEvent.CHECKPOINT: (
                func() for func in [save_checkpoint_generator]
            ),
            ExitEvent.EXIT: (func() for func in [test]),
        },
    )

    simulator.run()
