# **********************************************************************************************************************
#
#                             Copyright (c) 2019-2020 David Briant
#
# **********************************************************************************************************************

import pytest
skip = pytest.mark.skip


from coppertop.dm.testing import check, equals
from coppertop.dm.core import to, getAttr
from coppertop.dm.examples.ranges.nodes import SeqAdaptor, ListSink, Chain
from coppertop.dm.examples.ranges.utils import rMap, rTake, rExhaustInto, rTarget
from coppertop.dm.examples.ranges.ex_count_lines_jsp import countLinesJsp, countLinesTrad, countLinesRanges1, \
    countLinesRanges2, countLinesRanges3, home, filename, expected
from coppertop.dm.examples.ranges.ex_format_calendar import test_allDaysInYear, test_datesBetween, \
    test_chunkingIntoMonths, test_checkNumberOfDaysInEachMonth, test__untilWeekdayName, test_WeekChunks, \
    test_WeekStrings, test_MonthTitle, test_oneMonthsOutput, test_firstQuarter
from coppertop.dm.examples.ranges.ex_lazy_vs_eager import test_datesBetween_lazy, test_datesBetween_eager


def test_listRanges():
    seq = [1,2,3]
    r = SeqAdaptor(seq)
    o = ListSink([])
    while not r.empty:
        o.put(r.front)
        r.popFront()
    seq >> check >> equals >> o.list

def test_rangeOrRanges():
    rOfR = [] >> to >> Chain
    [e for e in rOfR] >> check >> equals >> []
    rOfR = (SeqAdaptor([]), SeqAdaptor([])) >> to >> Chain
    [e for e in rOfR] >> check >> equals >> []
    rOfR = (SeqAdaptor([1]), SeqAdaptor([2])) >> to >> Chain
    [e for e in rOfR] >> check >> equals >> [1,2]

def test_other():
    [1, 2, 3] >> rMap >> (lambda x: x) >> rExhaustInto >> ListSink() >> rTarget >> check >> equals >> [1, 2, 3]

@skip
def test_take():
    r1 = SeqAdaptor([1,2,3])
    r2 = r1 >> rTake >> 3
    r1 >> rFront >> check >> equals >> 1
    r3 = r1 >> rTake >> 4
    r2 >> rExhaustInto >> ListSink() >> rTarget >> check >> equals >> [1,2,3]
    r3 >> rExhaustInto >> ListSink() >> rTarget >> check >> equals >> [2,3]

def test_jsp():
    with open(home + filename) as f:
        actual = countLinesJsp(f)
    actual >> check >> equals >> expected

    with open(home + filename) as f:
        actual = countLinesTrad(f)
    actual >> check >> equals >> expected

    with open(home + filename) as f:
        actual = countLinesRanges1(f)
    actual >> check >> equals >> expected

    with open(home + filename) as f:
        actual = countLinesRanges2(f)
    actual >> check >> equals >> expected

    with open(home + filename) as f:
        actual = countLinesRanges3(f)
    actual >> check >> equals >> expected



def main():
    test_listRanges()
    test_rangeOrRanges()
    test_other()
    # test_take()

    test_jsp()

    test_allDaysInYear()
    test_datesBetween()
    test_chunkingIntoMonths()
    test_checkNumberOfDaysInEachMonth()
    test__untilWeekdayName()
    test_WeekChunks()
    test_WeekStrings()
    test_MonthTitle()
    test_oneMonthsOutput()
    # test_firstQuarter()

    test_datesBetween_lazy()
    test_datesBetween_eager()


if __name__ == '__main__':
    main()
    print('pass')


