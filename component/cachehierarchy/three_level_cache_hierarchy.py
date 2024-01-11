from m5.objects import *

from gem5.components.boards.abstract_board import AbstractBoard
from gem5.components.cachehierarchies.classic.abstract_classic_cache_hierarchy import (
    AbstractClassicCacheHierarchy,
)
from gem5.isas import ISA

from .skylake_caches import *


class ThreeLevelCacheHierarchy(AbstractClassicCacheHierarchy):
    def __init__(self, l1dwritelatency=0, l3_bank_num=4) -> None:
        AbstractClassicCacheHierarchy.__init__(self=self)
        self.membus = SystemXBar(width=192)
        self.membus.badaddr_responder = BadAddr()
        self.membus.default = Self.badaddr_responder.pio
        self._l3_bank_num = l3_bank_num

        self._l1dwritelatency = l1dwritelatency

    def get_mem_side_port(self) -> Port:
        return self.membus.mem_side_ports

    def get_cpu_side_port(self) -> Port:
        return self.membus.cpu_side_ports

    def incorporate_cache(self, board: AbstractBoard) -> None:
        # Set up the system port for functional access from the simulator.
        board.connect_system_port(self.membus.cpu_side_ports)

        for cntr in board.get_memory().get_memory_controllers():
            cntr.port = self.membus.mem_side_ports

        # create caches and buses
        # self.l1icache = L1ICache()
        # self.l1dcache = L1DCache(self._l1dmshr, self._l1dwb)
        self.l1dcaches = [
            L1DCache() for _ in range(board.get_processor().get_num_cores())
        ]
        self.l1icaches = [
            L1ICache() for _ in range(board.get_processor().get_num_cores())
        ]

        self.iptw_caches = [
            MMUCache() for _ in range(board.get_processor().get_num_cores())
        ]
        # DTLB Page walk caches
        self.dptw_caches = [
            MMUCache() for _ in range(board.get_processor().get_num_cores())
        ]

        # self.l2cache = L2Cache(self._l2mshr, self._l2wb)
        self.l2caches = [
            L2Cache() for _ in range(board.get_processor().get_num_cores())
        ]

        self.l3cache = L3Cache()

        # self.ptwXBar = L2XBar()
        self.l2XBars = [
            L2XBar(width=192)
            for _ in range(board.get_processor().get_num_cores())
        ]

        self.l3XBar = L2XBar(width=192)

        # connect all the caches and buses
        # core = board.get_processor().get_cores()[0].core
        for i, cpu in enumerate(board.get_processor().get_cores()):
            cpu.connect_icache(self.l1icaches[i].cpu_side)
            cpu.connect_dcache(self.l1dcaches[i].cpu_side)

            self.l1icaches[i].mem_side = self.l2XBars[i].cpu_side_ports
            self.l1dcaches[i].mem_side = self.l2XBars[i].cpu_side_ports
            self.iptw_caches[i].mem_side = self.l2XBars[i].cpu_side_ports
            self.dptw_caches[i].mem_side = self.l2XBars[i].cpu_side_ports
            self.l2caches[i].connectCPUSideBus(self.l2XBars[i])
            self.l2caches[i].connectMemSideBus(self.l3XBar)

            cpu.connect_walker_ports(
                self.iptw_caches[i].cpu_side, self.dptw_caches[i].cpu_side
            )

            if board.get_processor().get_isa() == ISA.X86:
                int_req_port = self.membus.mem_side_ports
                int_resp_port = self.membus.cpu_side_ports
                cpu.connect_interrupt(int_req_port, int_resp_port)
            else:
                cpu.connect_interrupt()
            # self.ptwcache.mem_side = self.l2XBar.cpu_side_ports
            # cpu.connect_walker_ports(
            #     self.ptwXBar.cpu_side_ports, self.ptwXBar.cpu_side_ports
            # )
            # self.ptwcache.cpu_side = self.ptwXBar.mem_side_ports

        # self.l2cache.connectCPUSideBus(self.l2XBar)
        # self.l2cache.connectMemSideBus(self.l3XBar)

        self.l3cache.connectCPUSideBus(self.l3XBar)
        self.l3cache.connectMemSideBus(self.membus)

        # # Assume that we only need one interrupt controller
        # core.createInterruptController()
        # core.interrupts[0].pio = self.membus.mem_side_ports
        # core.interrupts[0].int_requestor = self.membus.cpu_side_ports
        # core.interrupts[0].int_responder = self.membus.mem_side_ports

        if board.has_coherent_io():
            self._setup_io_cache(board)

    def _setup_io_cache(self, board: AbstractBoard) -> None:
        """Create a cache for coherent I/O connections"""
        self.iocache = Cache(
            assoc=8,
            tag_latency=50,
            data_latency=50,
            response_latency=50,
            mshrs=20,
            size="1kB",
            tgts_per_mshr=12,
            addr_ranges=board.mem_ranges,
        )
        self.iocache.mem_side = self.membus.cpu_side_ports
        self.iocache.cpu_side = board.get_mem_side_coherent_io_port()
