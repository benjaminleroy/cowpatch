import cowpatch as cow
import numpy as np
import pytest

def test_layout():
    """
    tests for layout

    checks that layouts with same structure but different
    parameters return same objects (and some error checking)

    """
    design1 = np.array([[np.nan, 0, 0],
                       [1,1, np.nan]])
    design2 = "#AA\nBB#"
    design3 = """
    #AA
    BB#
    """
    design4 = """
              #AA
              BB#
              """
    #^ what if this is tabbed?

    l1 = cow.layout(design = design1)
    l2 = cow.layout(design = design2)
    l3 = cow.layout(design = design3)
    l4 = cow.layout(design = design4)


    assert l2 == l1, \
        "expect string and matrix layout structure to create same matrix"
    assert l2 == l3, \
        "expect string inputs in different formats to be the same " +\
        "(trailing and leading extra rows)"
    assert l2 == l4, \
        "expect string inputs in different formats to be the same (tabbed +"+\
        "and trailing and leading extra rows)"

    # nrow + ncol (byrow checks of defaults) ----
    ncol3 = 3
    nrow3 = 4

    l5 = cow.layout(ncol = ncol3, nrow = nrow3)
    l6 = cow.layout(ncol = ncol3, nrow = nrow3, byrow = False)

    l5_1 = cow.layout(design = np.array([[1,2,3],
                                         [4,5,6],
                                         [7,8,9],
                                         [10,11,12]])-1)

    l6_1 = cow.layout(design = np.array([[1,5,9],
                                         [2,6,10],
                                         [3,7,11],
                                         [4,8,12]]) - 1)

    assert l5 == l5_1, \
        "expect default ncol/nrow and byrow (byrow = True) failed to preform"
    assert l6 == l6_1, \
        "expect default ncol/nrow with bycol (byrow = False) failed to preform"


    # error testing -----
    # index started incorrect
    with pytest.raises(Exception) as e_info:
        l7 = cow.layout(design = np.array([[1,2,3],
                                         [4,5,6],
                                         [7,8,9],
                                         [10,11,12]]))
    with pytest.raises(Exception) as e_info:
        l8 = cow.layout(design = np.array([[0,2],
                                            [0,2]]))
    with pytest.raises(Exception) as e_info:
        l9 = cow.layout(design = np.array([[0,2, np.nan],
                                            [0,2, np.nan]]))

    # widths and height are relative
    l1_1 = cow.layout(design = design1, rel_widths = [1,2,1],
                      rel_heights = [3,3])
    l1_2 = cow.layout(design = design1, rel_widths = [2,4,2],
                      rel_heights = [.5,.5])

    assert l1_1 == l1_2, \
        "relative heights don't effect similarity comparison"

