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
from component.processors.coreWithSMT import TunedCPU

from gem5.components.boards.mem_mode import MemMode
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.base_cpu_core import BaseCPUCore
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

parser = argparse.ArgumentParser(
    description="For dist-gem5 full system simulation"
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
print("--checkpoint:", parser.parse_args().checkpoint)
print("=======================================================")


# =========================File Directory===========================
bootloader_path = "/Users/choungjx/WorkSpace/tmp/tmp_bin/bin/riscv/opensbi/fw_jump.elf"
kernel_path = "/Users/choungjx/WorkSpace/tmp/tmp_bin/bin/riscv/opensbi/vmlinux"
system_image_path = "/Users/choungjx/WorkSpace/tmp/tmp_bin/bin/riscv/riscv-disk.img"
checkpoint_path = "m5out/test/node1/cpt.324854903584"

readfile_path = "gem5_fs_config/data/readfile"  # for m5 readfile
binary_path = "/Users/choungjx/WorkSpace/tmp/tmp_bin/bin/redis-server"  # your workload
init_script = "gem5_fs_config/data/init_fast.sh"  # this script would be executed once the system booted
level2_script = "gem5_fs_config/data/level2.sh"  # we use the init_script to trigger the level2_script so that we can execute arbitrary script from a checkpoint
# =================================================================


requires(isa_required=ISA.RISCV)

memory = DualChannelDDR4_2400(size="2GB")


class TunedCore(BaseCPUCore):
    def __init__(self, cpu_type: CPUTypes, core_id):
        super().__init__(core=TunedCPU(cpu_id=core_id), isa=ISA.RISCV)

        self._cpu_type = cpu_type

    def get_type(self) -> CPUTypes:
        return self._cpu_type


class BootCore(BaseCPUCore):
    def __init__(self, cpu_type: CPUTypes, core_id):
        super().__init__(
            core=DerivO3CPU(cpu_id=core_id, numThreads=2), isa=ISA.ARM
        )

        self._cpu_type = cpu_type

    def get_type(self) -> CPUTypes:
        return self._cpu_type


from gem5.components.processors.base_cpu_processor import BaseCPUProcessor


class SkylakeProcessor(BaseCPUProcessor):
    def __init__(self):
        self._cpu_type = CPUTypes.O3
        skylakecore = [
            TunedCore(
                cpu_type=CPUTypes.TIMING,
                core_id=0,
            ),
            
        ]

        super().__init__(cores=skylakecore)


# processor = SwitchableProcessor(
#     starting_cores="boot",
#     switchable_cores={
#         "boot": [SimpleCore(cpu_type=CPUTypes.ATOMIC, core_id=0, isa=ISA.ARM), SimpleCore(cpu_type=CPUTypes.ATOMIC, core_id=1, isa=ISA.ARM)],
#         "OoO": [
#             TunedCore(
#                 cpu_type=CPUTypes.TIMING,
#                 core_id=0,
#             )
#         ],
#     },
# )

processor = SkylakeProcessor()



from gem5.components.boards.riscv_board import RiscvBoard

board = RiscvBoard(
    clk_freq="3GHz",
    # processor=processor,
    processor=SkylakeProcessor(),
    memory=memory,
    cache_hierarchy=ThreeLevelCacheHierarchy(),
    # cache_hierarchy=test_cache,
)


# board.set_mem_mode(MemMode.ATOMIC_NONCACHING)
board.set_mem_mode(MemMode.TIMING)

shutil.copy(Path(init_script), Path(readfile_path))


if parser.parse_args().checkpoint:
    board.set_kernel_disk_workload(
        kernel=KernelResource(kernel_path),
        disk_image=DiskImageResource(
            system_image_path,
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
    processor.switch_to_processor("OoO")
    board.set_mem_mode(MemMode.TIMING)


def end_workload():
    # sys.exit(0)
    print("end")


def save_checkpoint_generator():
    new_checkpoint_dir = Path(options.outdir)
    m5.checkpoint((new_checkpoint_dir / f"cpt.{str(m5.curTick())}").as_posix())


def test():
    sys.exit(0)
    print("end")


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
        ExitEvent.USER_INTERRUPT: (func() for func in [test])
    },
)

simulator.run()
