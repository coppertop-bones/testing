# TDD TESTS - OBJECT MANAGER

from coppertop.pipe import *
from coppertop.dm.core.types import pylist, pytuple
from coppertop.dm.testing import check, raises, equals, gt, different
from bones import jones
# from bones import jones_pvt
from bones.core.errors import NotYetImplemented
import coppertop.dm.pp
from coppertop.dm.pp import PP

import sys, itertools


def test_om():
    sys._k = jones.Kernel()
    om = sys._om = jones_pvt.OM(sys._k)
    tm = sys._k.tm

    mem = 1

    i32 = tm.atom('i32', mem, 4)
    p = om.alloc(i32)
    om.inc(p)
    om.count(p) == 1
    om.dec(p)
    om.count(p) == 0
    om.inc(p)
    om.inc(p)
    om.inc(p)
    om.count(p) == 3
    om.dec(p)
    om.count(p) == 3
    assert om.btypeid(p) == i32

    sys._om = None
    sys._k = None
    return "test_om passed"



def main():
    test_om() >> PP



if __name__ == '__main__':
    main()
    'passed' >> PP
