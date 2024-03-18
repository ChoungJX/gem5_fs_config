import argparse
import sys
from pathlib import Path

import m5
from m5 import options
from m5.objects import *
from m5.params import *
from m5.util import addToPath

addToPath("../../../../")

import shutil

from component.cachehierarchy.three_level_cache_hierarchy import (
    ThreeLevelCacheHierarchy,
)
from component.processors.coreWithSMT import TunedCPU

from gem5.components.boards.mem_mode import MemMode
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
from gem5.components.processors.cpu_types import CPUTypes
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

# m5.disableAllListeners()

parser = argparse.ArgumentParser(description="For dist-gem5 full system simulation")

parser.add_argument(
    "--numThreads",
    default=1,
    action="store",
    type=int,
    help="Rank of this system within the dist gem5 run.",
)

parser.add_argument(
    "--distPort",
    default=2200,
    action="store",
    type=int,
    help="Rank of this system within the dist gem5 run.",
)

parser.add_argument(
    "--checkpoint",
    default=False,
    action="store",
    type=bool,
    help="To boot the simulator from a checkpoint.",
)


print("=======================================================")
print("show your args:")
print("--numThreads:", parser.parse_args().numThreads)
print("--distPort:", parser.parse_args().distPort)
print("--checkpoint:", parser.parse_args().checkpoint)
print("=======================================================")


# =========================File Directory===========================
bootloader_path = "/home/linfeng/.cache/gem5/arm64-bootloader-foundation"
kernel_path = "/home/linfeng/.cache/gem5/arm64-linux-kernel-5.4.49"
system_image_path = "/home/linfeng/work/arm64-ubuntu-focal-server.img"
checkpoint_path = "m5out/mini/minis_all_free_detailed/cpt.1000000000000"

readfile_path = f"gem5_fs_config/data/script/mini-redis/server_{parser.parse_args().distPort}" # for m5 readfile
binary_path = "/home/linfeng/bin/web-test-1145141919810"  # your workload
init_script = "gem5_fs_config/data/web/init_server.sh"  # this script would be executed once the system booted
level2_script = "gem5_fs_config/data/script/s_server.sh"  # we use the init_script to trigger the level2_script so that we can execute arbitrary script from a checkpoint
# =================================================================


requires(isa_required=ISA.ARM)

memory = DualChannelDDR4_2400(size="2GB")


class TunedCore(BaseCPUCore):
    def __init__(self, cpu_type: CPUTypes, core_id, numThreads: int = 1):
        super().__init__(
            core=TunedCPU(cpu_id=core_id, numThreads=numThreads), isa=ISA.ARM
        )

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

    def __init__(self):
        self._cpu_type = CPUTypes.O3
        skylakecore = [
            TunedCore(
                cpu_type=CPUTypes.TIMING,
                core_id=0,
                numThreads=parser.parse_args().numThreads,
            )
        ]

        super().__init__(cores=skylakecore)


release = ArmDefaultRelease()
platform = VExpress_GEM5_Foundation()


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
    dist_rank=0,
    dist_size=3,
    server_port=parser.parse_args().distPort,
    sync_start="10t",
    sync_repeat="10us",
    delay="20us",
    delay_var="5us",
    num_nodes=3,
)

board.etherlink.int0 = Parent.board.ethernet.interface

# board.set_mem_mode(MemMode.ATOMIC_NONCACHING)
board.set_mem_mode(MemMode.TIMING)

shutil.copy(Path(init_script), Path(readfile_path))


if parser.parse_args().checkpoint:
    board.set_kernel_disk_workload(
        kernel=KernelResource(kernel_path),
        disk_image=DiskImageResource(
            system_image_path,
            root_partition="1",
        ),
        bootloader=BootloaderResource(bootloader_path),
        checkpoint=CheckpointResource(checkpoint_path),
        readfile=readfile_path,
    )

else:
    board.set_kernel_disk_workload(
        kernel=KernelResource(kernel_path),
        disk_image=DiskImageResource(
            system_image_path,
            root_partition="1",
        ),
        bootloader=BootloaderResource(bootloader_path),
        readfile=readfile_path,
    )


# We define the system with the aforementioned system defined.


def init_sys():
    print("Loading binary file")

    shutil.copy(Path(binary_path), Path(readfile_path))


def boot_workload():
    print("Loading level2 script")

    shutil.copy(Path(level2_script), Path(readfile_path))


def begin_workload():
    print("Start to boot workload...")
    # processor.switch_to_processor("OoO")
    # board.set_mem_mode(MemMode.TIMING)
    m5.stats.reset()


def end_workload():
    # sys.exit(0)
    print("aaa")


def save_checkpoint_generator():
    new_checkpoint_dir = Path(options.outdir)
    m5.checkpoint((new_checkpoint_dir / f"cpt.{str(m5.curTick())}").as_posix())


def test():
    # sys.exit(0)
    print("aaa")


def reset_stats():
    print("****************Reset Statistic****************")
    m5.stats.reset()


simulator = Simulator(
    board=board,
    full_system=True,
    on_exit_event={
        ExitEvent.WORKBEGIN: (
            func() for func in [init_sys, boot_workload, begin_workload]
        ),
        ExitEvent.WORKEND: (func() for func in [end_workload]),
        ExitEvent.CHECKPOINT: (func() for func in [save_checkpoint_generator]),
        ExitEvent.EXIT: (func() for func in [test]),
        ExitEvent.USER_INTERRUPT: (
            func()
            for func in [
                reset_stats,
                reset_stats,
                reset_stats,
                reset_stats,
                reset_stats,
            ]
        ),
    },
)

simulator.run()
