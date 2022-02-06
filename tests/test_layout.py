import cowpatch as cow
import numpy as np
import pytest

def test_layout():
    """
    tests for layout

    checks that layouts with same structure but different
    parameters return same objects (and some error checking)

    see additional tests w.r.t. individual functions of the `layout` class
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

def test_layout__element_locations():
    """
    test layout's _element_locations function (2 static)
    """

    # design 1 : np.nans in grid
    design1 = np.array([[np.nan, 0, 0],
                   [1,1, np.nan]])
    width_px1 = 300
    height_px1 = 200

    layout1 = cow.layout(design = design1)
    areas1 = layout1._element_locations(width_px=width_px1,
                                        height_px=height_px1)
    areas1_e = [cow.area(x_left=100, y_top=0,
                    width=200,height=100,
                    _type="px"),
               cow.area(x_left=0, y_top=100,
                    width=200,height=100,
                    _type="px")]

    assert np.all([areas1[l_idx] == areas1_e[l_idx] for l_idx in [0,1]]), \
        "error in expected areas returned from simple layout (1)," +\
        " - potentially w.r.t. np.nans in design matrix"

    # design 2 : different shapes of plots
    design2 = np.array([[0,0,2,2],
                         [0,0,3,3],
                         [1,1,3,3]])

    rel_heights2 = np.array([1,2,1])
    rel_widths2 = np.array([1,1,2,3])
    width_px2 = 280
    height_px2 = 140

    layout2 = cow.layout(design = design2,
                         rel_heights = rel_heights2,
                         rel_widths = rel_widths2)
    areas2 = layout2._element_locations(width_px=width_px2,
                                        height_px=height_px2)

    loc1_p_e = cow.area(x_left=0,
                y_top=0,
                width=2/7 * 280,
                height=3/4 * 140,
                _type="px")

    loc2_p_e = cow.area(x_left=0,
                y_top=3/4 * 140,
                width=2/7 * 280,
                height=1/4 * 140,
                _type="px")

    loc3_p_e = cow.area(x_left=2/7 * 280,
                y_top=0,
                width=5/7 * 280,
                height=1/4 * 140,
                _type="px")

    loc4_p_e = cow.area(x_left=2/7 * 280,
                y_top=1/4 * 140,
                width=5/7 * 280,
                height=3/4 * 140,
                _type="px")
    area2_e = [loc1_p_e, loc2_p_e, loc3_p_e, loc4_p_e]

    assert np.all([areas2[l_idx] == area2_e[l_idx] for l_idx in [0,1,2,3]]), \
        "error in expected areas returned from simple layout (2)," +\
        " - potentially w.r.t. different sizes of widths of plots or"+\
        " relative widths and relative heights."

def test_layout__yokogaki_ordering():
    """
    test layout's _yokogaki_ordering function (2 static)
    """

    # design 1 : np.nans in grid
    design1 = np.array([[np.nan, 1, 1],
                   [0,0, np.nan]])
    layout1 = cow.layout(design = design1)
    yorder1 = layout1._yokogaki_ordering()


    assert np.all(yorder1 == np.array([1,0])), \
        "yokogaki ordering with simple example with np.nans failed (1)"

    # design 2 : different shapes of plots
    design2 = np.array([[0,0,2,2],
                         [0,0,3,3],
                         [1,1,3,3]])

    # relative structure won't effect this...
    rel_heights2 = np.array([1,2,1])
    rel_widths2 = np.array([1,1,2,3])

    layout2 = cow.layout(design = design2,
                         rel_heights = rel_heights2,
                         rel_widths = rel_widths2)
    yorder2 = layout2._yokogaki_ordering()

    assert np.all(yorder2 == np.array([0,2,3,1])), \
        "yokogaki ordering with second simple example failed (2)"

def test_area():
    """
    test of area (static example)
    """
    # design structure
    # [[1,1,3,3],
    #  [1,1,4,4],
    #  [2,2,4,4]]
    #
    # rel_heights = [1,2,1]
    # rel_widths = [1,1,2,3]
    #
    # width_px = 280 (px)
    # height_px = 140 (px)


    rel_heights = np.array([1,2,1])
    rel_widths = np.array([1,1,2,3])
    width_px = 280
    height_px = 140

    loc1 = cow.area(x_left=0,
                y_top=0,
                width=2,
                height=2,
                _type="design")

    loc2 = cow.area(x_left=0,
                y_top=2,
                width=2,
                height=1,
                _type="design")

    loc3 = cow.area(x_left=2,
                y_top=0,
                width=2,
                height=1,
                _type="design")

    loc4 = cow.area(x_left=2,
                y_top=1,
                width=2,
                height=2,
                _type="design")

    # convert to relative -------------
    loc1_r = loc1._design_to_relative(rel_widths=rel_widths,
                                      rel_heights=rel_heights)
    loc2_r = loc2._design_to_relative(rel_widths=rel_widths,
                                      rel_heights=rel_heights)
    loc3_r = loc3._design_to_relative(rel_widths=rel_widths,
                                      rel_heights=rel_heights)
    loc4_r = loc4._design_to_relative(rel_widths=rel_widths,
                                      rel_heights=rel_heights)


    # expected:

    loc1_r_e = cow.area(x_left=0,
                y_top=0,
                width=2/7,
                height=3/4,
                _type="relative")

    loc2_r_e = cow.area(x_left=0,
                y_top=3/4,
                width=2/7,
                height=1/4,
                _type="relative")

    loc3_r_e = cow.area(x_left=2/7,
                y_top=0,
                width=5/7,
                height=1/4,
                _type="relative")

    loc4_r_e = cow.area(x_left=2/7,
                y_top=1/4,
                width=5/7,
                height=3/4,
                _type="relative")

    assert loc1_r == loc1_r_e, \
        "transform of design to relative represent for static example failed (1)"

    assert loc2_r == loc2_r_e, \
        "transform of design to relative represent for static example failed (2)"

    assert loc3_r == loc3_r_e, \
        "transform of design to relative represent for static example failed (3)"

    assert loc4_r == loc4_r_e, \
        "transform of design to relative represent for static example failed (4)"


    # convert to pixel (2 ways!) -----------

    # direct to .px
    loc1_p1 = loc1.px(rel_widths=rel_widths,
                      rel_heights=rel_heights,
                      width_px=width_px,
                      height_px=height_px)
    loc2_p1 = loc2.px(rel_widths=rel_widths,
                      rel_heights=rel_heights,
                      width_px=width_px,
                      height_px=height_px)
    loc3_p1 = loc3.px(rel_widths=rel_widths,
                      rel_heights=rel_heights,
                      width_px=width_px,
                      height_px=height_px)
    loc4_p1 = loc4.px(rel_widths=rel_widths,
                      rel_heights=rel_heights,
                      width_px=width_px,
                      height_px=height_px)

    # through internals
    loc1_p2 = loc1_r._relative_to_px(width_px=width_px,
                                      height_px=height_px)
    loc2_p2 = loc2_r._relative_to_px(width_px=width_px,
                                      height_px=height_px)
    loc3_p2 = loc3_r._relative_to_px(width_px=width_px,
                                      height_px=height_px)
    loc4_p2 = loc4_r._relative_to_px(width_px=width_px,
                                      height_px=height_px)

    # expected
    loc1_p_e = cow.area(x_left=0,
                y_top=0,
                width=2/7 * 280,
                height=3/4 * 140,
                _type="px")

    loc2_p_e = cow.area(x_left=0,
                y_top=3/4 * 140,
                width=2/7 * 280,
                height=1/4 * 140,
                _type="px")

    loc3_p_e = cow.area(x_left=2/7 * 280,
                y_top=0,
                width=5/7 * 280,
                height=1/4 * 140,
                _type="px")

    loc4_p_e = cow.area(x_left=2/7 * 280,
                y_top=1/4 * 140,
                width=5/7 * 280,
                height=3/4 * 140,
                _type="px")

    # .px
    assert loc1_p1 == loc1_p_e, \
        "transform of design to px (.px) represent for static example failed (1)"

    assert loc2_p1 == loc2_p_e, \
        "transform of design to px (.px) represent for static example failed (2)"

    assert loc3_p1 == loc3_p_e, \
        "transform of design to px (.px) represent for static example failed (3)"

    assert loc4_p1 == loc4_p_e, \
        "transform of design to px (.px) represent for static example failed (4)"

    #  relative to px
    assert loc1_p2 == loc1_p_e, \
        "transform of relative to px represent for static example failed (1)"

    assert loc2_p2 == loc2_p_e, \
        "transform of relative to px represent for static example failed (2)"

    assert loc3_p2 == loc3_p_e, \
        "transform of relative to px represent for static example failed (3)"

    assert loc4_p2 == loc4_p_e, \
        "transform of relative to px represent for static example failed (4)"

    # errors for bad parameter input ------------

    # RELATIVE #

    # relative: px accidentally described as _type
    with pytest.raises(Exception) as e_info:
        loc_relative_error = cow.area(x_left=0,
                    y_top=0,
                    width=2/7 * 280,
                    height=3/4 * 140,
                    _type="relative")

    # relative: 0 width
    with pytest.raises(Exception) as e_info:
            loc_relative_error_0_width = cow.area(x_left=0,
                y_top=0,
                width=0,
                height=3/4,
                _type="relative")
    # relative: 0 height
    with pytest.raises(Exception) as e_info:
        loc_relative_error_0_width = cow.area(x_left=0,
                y_top=0,
                width=1/2,
                height=0,
                _type="relative")

    # relative: neg x_left
    with pytest.raises(Exception) as e_info:
        loc_relative_error_neg_x = cow.area(x_left=-1,
                y_top=0,
                width=2/4,
                height=3/4,
                _type="relative")
    # relative: 0 height
    with pytest.raises(Exception) as e_info:
        loc_relative_error_neg_y = cow.area(x_left=0,
                y_top=-1,
                width=1/2,
                height=1/2,
                _type="relative")

    # DESIGN #

    ### probably should catch this oversight, but could be a really large
    ### matrix...
    # # design: px accidentally described as _type
    # with pytest.raises(Exception) as e_info:
    #     loc_design_error_px = cow.area(x_left=0,
    #             y_top=0,
    #             width=2/7 * 280,
    #             height=3/4 * 140,
    #             _type="design")

    # design: relative accidentally described as _type
    with pytest.raises(Exception) as e_info:
        loc_design_error_relative = cow.area(x_left=0,
                y_top=0,
                width=2/7,
                height=3/4,
                _type="design")

    # design: 0 width
    with pytest.raises(Exception) as e_info:
        loc_design_error_0_width = cow.area(x_left=0,
                y_top=0,
                width=0,
                height=3,
                _type="design")
    # design: 0 height
    with pytest.raises(Exception) as e_info:
        loc_design_error_0_width = cow.area(x_left=0,
                y_top=0,
                width=1,
                height=0,
                _type="design")


    # design: neg x_left
    with pytest.raises(Exception) as e_info:
        loc_design_error_neg_x = cow.area(x_left=-1,
                y_top=0,
                width=2,
                height=3,
                _type="design")
    # relative: 0 height
    with pytest.raises(Exception) as e_info:
        loc_design_error_neg_y = cow.area(x_left=0,
                y_top=-1,
                width=1/2,
                height=1/2,
                _type="design")

    # PX #

    # px: 0 width
    with pytest.raises(Exception) as e_info:
        loc_px_error_0_width = cow.area(x_left=0,
                y_top=0,
                width=0,
                height=3* 280,
                _type="px")
    # px: 0 height
    with pytest.raises(Exception) as e_info:
        loc_px_error_0_width = cow.area(x_left=0,
                y_top=0,
                width=1* 280,
                height=0,
                _type="px")


    # px: neg x_left
    with pytest.raises(Exception) as e_info:
        loc_px_error_neg_x = cow.area(x_left=-1* 280,
                y_top=0,
                width=2* 280,
                height=3* 280,
                _type="px")
    # px: 0 height
    with pytest.raises(Exception) as e_info:
        loc_px_error_neg_y = cow.area(x_left=0,
                y_top=-1* 280,
                width=1/2* 280,
                height=1/2* 280,
                _type="px")

