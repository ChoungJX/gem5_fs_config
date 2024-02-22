# Copyright (c) 2020 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Jason Lowe-Power, Trivikram Reddy

import math

import m5
from m5.objects import *


class port0(FUDesc):
    opList = [
        OpDesc(opClass="IntAlu", opLat=1),
        OpDesc(opClass="IntDiv", opLat=1, pipelined=True),
        OpDesc(opClass="FloatDiv", opLat=12, pipelined=True),
        OpDesc(opClass="FloatSqrt", opLat=24, pipelined=True),
        OpDesc(opClass="FloatAdd", opLat=4, pipelined=True),
        OpDesc(opClass="FloatCmp", opLat=4, pipelined=True),
        OpDesc(opClass="FloatCvt", opLat=4, pipelined=True),
        OpDesc(opClass="FloatMult", opLat=4, pipelined=True),
        OpDesc(opClass="FloatMultAcc", opLat=5, pipelined=True),
        OpDesc(opClass="SimdAdd", opLat=1),
        OpDesc(opClass="SimdAddAcc", opLat=1),
        OpDesc(opClass="SimdAlu", opLat=1),
        OpDesc(opClass="SimdCmp", opLat=1),
        OpDesc(opClass="SimdShift", opLat=1),
        OpDesc(opClass="SimdShiftAcc", opLat=1),
        OpDesc(opClass="SimdReduceAdd", opLat=1),
        OpDesc(opClass="SimdReduceAlu", opLat=1),
        OpDesc(opClass="SimdReduceCmp", opLat=1),
        OpDesc(opClass="SimdCvt", opLat=3, pipelined=True),
        OpDesc(opClass="SimdMisc"),
        OpDesc(opClass="SimdMult", opLat=4, pipelined=True),
        OpDesc(opClass="SimdMultAcc", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatAdd", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatAlu", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatCmp", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatReduceAdd", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatReduceCmp", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatCvt", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatMult", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatMultAcc", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatDiv", opLat=12, pipelined=True),
        OpDesc(opClass="SimdFloatSqrt", opLat=20, pipelined=True),
    ]
    count = 1


class port1(FUDesc):
    opList = [
        OpDesc(opClass="IntAlu", opLat=1),
        OpDesc(opClass="IntMult", opLat=3, pipelined=True),
        OpDesc(opClass="FloatAdd", opLat=4, pipelined=True),
        OpDesc(opClass="FloatCmp", opLat=4, pipelined=True),
        OpDesc(opClass="FloatCvt", opLat=4, pipelined=True),
        OpDesc(opClass="FloatMult", opLat=4, pipelined=True),
        OpDesc(opClass="FloatMultAcc", opLat=5, pipelined=True),
        OpDesc(opClass="SimdAdd", opLat=1),
        OpDesc(opClass="SimdAddAcc", opLat=1),
        OpDesc(opClass="SimdAlu", opLat=1),
        OpDesc(opClass="SimdCmp", opLat=1),
        OpDesc(opClass="SimdShift", opLat=1),
        OpDesc(opClass="SimdShiftAcc", opLat=1),
        OpDesc(opClass="SimdReduceAdd", opLat=1),
        OpDesc(opClass="SimdReduceAlu", opLat=1),
        OpDesc(opClass="SimdReduceCmp", opLat=1),
        OpDesc(opClass="SimdCvt", opLat=3, pipelined=True),
        OpDesc(opClass="SimdMisc"),
        OpDesc(opClass="SimdMult", opLat=4, pipelined=True),
        OpDesc(opClass="SimdMultAcc", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatAdd", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatAlu", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatCmp", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatReduceAdd", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatReduceCmp", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatCvt", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatMult", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatMultAcc", opLat=4, pipelined=True),
    ]
    count = 1


class port2(FUDesc):
    opList = [
        OpDesc(opClass="MemRead", opLat=1, pipelined=True),
        OpDesc(opClass="FloatMemRead", opLat=1, pipelined=True),
    ]
    count = 1


class port3(FUDesc):
    opList = [
        OpDesc(opClass="MemRead", opLat=1, pipelined=True),
        OpDesc(opClass="FloatMemRead", opLat=1, pipelined=True),
    ]
    count = 1


class port4(FUDesc):
    opList = [
        OpDesc(opClass="MemWrite", opLat=1, pipelined=True),
        OpDesc(opClass="FloatMemWrite", opLat=1, pipelined=True),
    ]
    count = 1


class port5(FUDesc):
    opList = [
        OpDesc(opClass="IntAlu", opLat=1),
        OpDesc(opClass="SimdAdd", opLat=1),
        OpDesc(opClass="SimdAddAcc", opLat=1),
        OpDesc(opClass="SimdAlu", opLat=1),
        OpDesc(opClass="SimdCmp", opLat=1),
        OpDesc(opClass="SimdShift", opLat=1),
        OpDesc(opClass="SimdMisc"),
        OpDesc(opClass="SimdShiftAcc", opLat=1),
        OpDesc(opClass="SimdReduceAdd", opLat=1),
        OpDesc(opClass="SimdReduceAlu", opLat=1),
        OpDesc(opClass="SimdReduceCmp", opLat=1),
        OpDesc(opClass="SimdFloatAdd", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatAlu", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatCmp", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatReduceAdd", opLat=4, pipelined=True),
        OpDesc(opClass="SimdFloatReduceCmp", opLat=4, pipelined=True),
    ]
    count = 1


class port6(FUDesc):
    opList = [
        OpDesc(opClass="IntAlu", opLat=1),
        OpDesc(opClass="SimdAdd", opLat=1),
        OpDesc(opClass="SimdAddAcc", opLat=1),
        OpDesc(opClass="SimdAlu", opLat=1),
        OpDesc(opClass="SimdCmp", opLat=1),
        OpDesc(opClass="SimdShift", opLat=1),
        OpDesc(opClass="SimdShiftAcc", opLat=1),
    ]
    count = 1


class port7(FUDesc):
    opList = [
        OpDesc(opClass="MemWrite", opLat=1, pipelined=True),
        OpDesc(opClass="FloatMemWrite", opLat=1, pipelined=True),
    ]
    count = 1


class ExecUnits(FUPool):
    FUList = [
        port0(),
        port1(),
        port2(),
        port3(),
        port4(),
        port5(),
        port6(),
        port7(),
    ]


class IndirectPred(SimpleIndirectPredictor):
    indirectSets = 128  # Cache sets for indirect predictor
    indirectWays = 4  # Ways for indirect predictor
    indirectTagSize = 16  # Indirect target cache tag bits
    indirectPathLength = 7  # Previous indirect targets to use for path history
    indirectGHRBits = 16  # Indirect GHR number of bits


class BranchPred(TAGE_SC_L_64KB):
    indirectBranchPred = IndirectPred()  # use NULL to disable


depth = 3
width = 4


class TunedCPU(DerivO3CPU):
    """Calibrated: configured to match the performance of hardware"""

    numThreads = 2

    branchPred = BranchPred()

    # Pipeline delays
    fetchToDecodeDelay = depth
    decodeToRenameDelay = 1
    renameToIEWDelay = 3 * depth
    issueToExecuteDelay = 1
    iewToCommitDelay = 2 * depth

    forwardComSize = 19
    backComSize = 19

    # Pipeline widths
    fetchWidth = width * 2
    decodeWidth = width * 2
    renameWidth = 3 * width
    issueWidth = 2 * width
    dispatchWidth = 2 * width
    wbWidth = 2 * width
    commitWidth = 2 * width
    squashWidth = 3 * width

    fuPool = ExecUnits()
    # IntDiv()
    fuPool.FUList[0].opList[1].opLat = 2
    # IntMult()
    fuPool.FUList[1].opList[1].opLat = 2
    # Load
    fuPool.FUList[2].count = 12
    # store
    fuPool.FUList[4].count = 12
    fuPool.FUList[6].count = 3

    fetchBufferSize = 16
    fetchQueueSize = 64
    numROBEntries = 336
    numIQEntries = 146
    LQEntries = 72 * 2
    SQEntries = 56 * 2
    numPhysIntRegs = 270
    numPhysFloatRegs = 252
    numPhysVecRegs = 164
    numPhysVecPredRegs = 64
    numPhysMatRegs = 4
