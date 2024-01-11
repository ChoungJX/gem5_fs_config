from gem5.isas import ISA
from gem5.utils.requires import requires
from gem5.simulate.simulator import Simulator
from gem5.components.boards.x86_board import X86Board
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.simple_core import SimpleCore
from gem5.resources.resource import DiskImageResource,KernelResource,BootloaderResource
from gem5.components.processors.switchable_processor import (
    SwitchableProcessor,
)
from gem5.simulate.exit_event import ExitEvent
from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
from gem5.components.processors.cpu_types import CPUTypes, get_mem_mode
from gem5.components.boards.mem_mode import MemMode

import m5
from m5.params import *
from m5.objects import *

from processors.core import TunedCPU
from cachehierarchy.three_level_cache_hierarchy import ThreeLevelCacheHierarchy
# from gem5.components.cachehierarchies.ruby.caches.prebuilt.octopi_cache.octopi import OctopiCache
# from board import SkylakeARMBoard

import argparse

# m5.disableAllListeners()

parser = argparse.ArgumentParser(
        description="test"
    )

parser.add_argument(
        "--number",
        default=1,
        action="store",
        type=int,
        help="Rank of this system within the dist gem5 run.",
    )

print(parser.parse_args().number)


requires(
    isa_required=ISA.X86
)

memory = DualChannelDDR4_2400(size="3GB")


class TunedCore(BaseCPUCore):
    """
    An out of order core for X86.
    The LSQ depth (split equally between loads and stores), the width of the
    core, and the number of entries in the reorder buffer are configurable.
    """

    def __init__(self, cpu_type: CPUTypes, core_id):
        super().__init__(core=TunedCPU(cpu_id=core_id), isa=ISA.X86)

        self._cpu_type = cpu_type

    def get_type(self) -> CPUTypes:
        return self._cpu_type
    

processor = SwitchableProcessor(
    starting_cores="boot",
    switchable_cores={
        "boot":[SimpleCore(cpu_type=CPUTypes.ATOMIC, core_id=0, isa=ISA.X86),SimpleCore(cpu_type=CPUTypes.ATOMIC, core_id=1, isa=ISA.X86)],
        "OoO":[TunedCore(cpu_type=CPUTypes.TIMING, core_id=0,),TunedCore(cpu_type=CPUTypes.TIMING, core_id=1,)]
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
        skylakecore=[TunedCore(cpu_type=CPUTypes.TIMING, core_id=0,)]

        super().__init__(
            cores = skylakecore
        )



# from cachehierarchy.octopi_cache.octopi import OctopiCache
from gem5.components.cachehierarchies.ruby.mesi_three_level_cache_hierarchy import MESIThreeLevelCacheHierarchy
test_cache = MESIThreeLevelCacheHierarchy(
        l1i_size="32kB",
        l1i_assoc=8,
        l1d_size="32kB",
        l1d_assoc=8,
        l2_size="1MB",
        l2_assoc=8,
        l3_assoc=16,
        l3_size="2MB",
        num_l3_banks=2
    )

# from gem5.components.cachehierarchies.classic.private_l1_cache_hierarchy import PrivateL1CacheHierarchy

board = X86Board(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    # cache_hierarchy=ThreeLevelCacheHierarchy(),
    cache_hierarchy=test_cache,
)


dev = IGbE_e1000(pci_bus=0, pci_dev=0, pci_func=0, InterruptLine=1, InterruptPin=1)
board.ethernet = dev

board.ethernet.host = board.pc.pci_host
board.ethernet.pio = board.get_dma_ports()[1]
board.ethernet.dma = board.iobus.cpu_side_ports



board.etherlink = DistEtherLink(
    dist_rank=parser.parse_args().number,
    dist_size=20,
    server_port=2200,
    sync_start="1000000000000t",
    sync_repeat="10us",
    delay="1ms"
)

board.etherlink.int0 = Parent.board.ethernet.interface

board.set_mem_mode(MemMode.ATOMIC_NONCACHING)
# board.set_mem_mode(MemMode.TIMING)


if parser.parse_args().number == 0:
    # board.set_kernel_disk_workload(    
    #     kernel = KernelResource("/home/linfeng/.cache/gem5/arm64-linux-kernel-5.4.49"),
    #     # disk_image = DiskImageResource("/home/jax/gem5_fs/gem5-resources/src/x86-ubuntu/disk-image/x86-ubuntu/x86-ubuntu-image/x86-ubuntu",
    #     #                                root_partition = "1"),
    #     # disk_image = DiskImageResource("/home/jax/.cache/gem5/x86-ubuntu-18.04-img",
    #     #                                root_partition = "1"),
    #     disk_image = DiskImageResource("/home/linfeng/work/arm64-ubuntu-focal-server.img",
    #                                 root_partition = "1"),
    #     bootloader = BootloaderResource("/home/linfeng/.cache/gem5/arm64-bootloader-foundation"),
    #     # bootloader = obtain_resource("arm64-bootloader-foundation"),
    #     readfile="arm_fs_quick_start/script/s_server.sh"
    #     # readfile_contents = command,
    #     # checkpoint=Path("m5out/node%s/"%(parser.parse_args().number))
    #     # readfile_contents = "ip a"
    # )
    readfile="arm_fs_quick_start/script/s_server.sh"
    board.set_kernel_disk_workload(
        kernel=KernelResource("/home/linfeng/bin/vmlinux-5.4.49"),
        disk_image=DiskImageResource("/home/linfeng/bin/x86-ubuntu.img",root_partition="1"),
        readfile=readfile
    )
else:
    # board.set_kernel_disk_workload(    
    #     kernel = KernelResource("/home/linfeng/.cache/gem5/arm64-linux-kernel-5.4.49"),
    #     # disk_image = DiskImageResource("/home/jax/gem5_fs/gem5-resources/src/x86-ubuntu/disk-image/x86-ubuntu/x86-ubuntu-image/x86-ubuntu",
    #     #                                root_partition = "1"),
    #     # disk_image = DiskImageResource("/home/jax/.cache/gem5/x86-ubuntu-18.04-img",
    #     #                                root_partition = "1"),
    #     disk_image = DiskImageResource("/home/linfeng/work/arm64-ubuntu-focal-server.img",
    #                                 root_partition = "1"),
    #     bootloader = BootloaderResource("/home/linfeng/.cache/gem5/arm64-bootloader-foundation"),
    #     # bootloader = obtain_resource("arm64-bootloader-foundation"),
    #     readfile="arm_fs_quick_start/script/s_client_%s.sh"%(parser.parse_args().number)
    #     # readfile_contents = command,
    #     # checkpoint=Path("m5out/node%s/"%(parser.parse_args().number))
    #     # readfile_contents = "ip a"
    # )
    readfile="arm_fs_quick_start/script/s_client_%s.sh"%(parser.parse_args().number)
    board.set_kernel_disk_workload(
        kernel=KernelResource("/home/linfeng/bin/vmlinux-5.4.49"),
        disk_image=DiskImageResource("/home/linfeng/bin/x86-ubuntu.img",root_partition="1"),
        readfile=readfile
    )

# We define the system with the aforementioned system defined.
    
def begin_workload():
    processor.switch_to_processor("OoO")
    board.set_mem_mode(MemMode.TIMING)


simulator = Simulator(board=board,
on_exit_event={
        ExitEvent.WORKBEGIN : (func() for func in [begin_workload]),
    })
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