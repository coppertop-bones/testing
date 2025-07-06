# **********************************************************************************************************************
#
#                             Copyright (c) 2019-2020 David Briant
#
# **********************************************************************************************************************

import pytest
skip = pytest.mark.skip


from coppertop.dm.testing import check, equals
from coppertop.dm.core import to
from coppertop.dm.examples.ranges.agents import IndexableFR, ListOR, ChainAsSingleFR
from coppertop.dm.examples.ranges.utils import rEach, rGetIRIter, rMaterialise
from coppertop.dm.examples.ranges.ex_count_lines_jsp import countLinesJsp, countLinesTrad, countLinesRanges1, \
    countLinesRanges2, countLinesRanges3, home, filename, expected
from coppertop.dm.examples.ranges.ex_format_calendar import test_allDaysInYear, test_datesBetween, \
    test_chunkingIntoMonths, test_checkNumberOfDaysInEachMonth, test__untilWeekdayName, test_WeekChunks, \
    test_WeekStrings, test_MonthTitle, test_oneMonthsOutput, test_firstQuarter
from coppertop.dm.examples.ranges.ex_lazy_vs_eager import test_datesBetween_lazy, test_datesBetween_eager


def test_listRanges():
    r = IndexableFR([1,2,3])
    o = ListOR([])
    while not r.empty:
        o.put(r.front)
        r.popFront()
    r.indexable >> check >> equals >> o.list

def test_rangeOrRanges():
    rOfR = [] >> to >> ChainAsSingleFR
    [e for e in rOfR >> rGetIRIter] >> check >> equals >> []
    rOfR = (IndexableFR([]), IndexableFR([])) >> to >> ChainAsSingleFR
    [e for e in rOfR >> rGetIRIter] >> check >> equals >> []
    rOfR = (IndexableFR([1]), IndexableFR([2])) >> to >> ChainAsSingleFR
    [e for e in rOfR >> rGetIRIter] >> check >> equals >> [1,2]

def test_other():
    [1, 2, 3] >> rEach >> (lambda x: x) >> rMaterialise >> check >> equals >> [1, 2, 3]

@skip
def test_take():
    r1 = IndexableFR([1,2,3])
    r2 = r1 >> take >> 3
    r1.popFront >> check >> equals >> 1
    r3 = r1 >> take >> 4
    r2 >> rMaterialise >> check >> equals >> [1,2,3]
    r3 >> rMaterialise >> check >> equals >> [2,3]

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


