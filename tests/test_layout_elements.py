import cowpatch as cow
import numpy as np
import pytest
import re

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

    design5 = ".AA\nBB."
    design6 = """
    .AA
    BB.
    """
    design7 = """
              .AA
              BB.
              """

    l1 = cow.layout(design = design1)
    l2 = cow.layout(design = design2)
    l3 = cow.layout(design = design3)
    l4 = cow.layout(design = design4)
    l4 = cow.layout(design = design4)
    l5 = cow.layout(design = design5)
    l6 = cow.layout(design = design6)
    l7 = cow.layout(design = design7)


    assert l2 == l1, \
        "expect string (#) and matrix layout structure to create same matrix"
    assert l2 == l3, \
        "expect string (#) inputs in different formats to be the same " +\
        "(trailing and leading extra rows)"
    assert l2 == l4, \
        "expect string (#) inputs in different formats to be the same "+\
        "(tabbed + and trailing and leading extra rows)"
    assert l5 == l1, \
        "expect string (.) and matrix layout structure to create same matrix"
    assert l5 == l6, \
        "expect string (.) inputs in different formats to be the same " +\
        "(trailing and leading extra rows)"
    assert l5 == l7, \
        "expect string (#) inputs in different formats to be the same "+\
        "(tabbed + and trailing and leading extra rows)"

    # nrow + ncol (byrow checks of defaults) ----
    ncol3 = 3
    nrow3 = 4

    l5 = cow.layout(ncol = ncol3, nrow = nrow3)
    l6 = cow.layout(ncol = ncol3, nrow = nrow3, byrow = False)

    # we also don't want to auto this design (last row need not be complete...)
    l5_1 = cow.layout(design = np.array([[1,2,3],
                                         [4,5,6],
                                         [7,8,9],
                                         [10,11,12]])-1)

    l6_1 = cow.layout(design = np.array([[1,5,9],
                                         [2,6,10],
                                         [3,7,11],
                                         [4,8,12]]) - 1)

    assert l5 != l5_1, \
        "expect default ncol/nrow and byrow (byrow = True) to *not* be "+\
        "equalivant to a fulled defined design matrix"
    assert l6 != l6_1, \
        "expect default ncol/nrow with bycol (byrow = False) to *not* be "+\
        "equalivant to a fulled defined design matrix"

    assert l5._layout__design is None and \
        l6._layout__design is None, \
        "if only ncol and nrows are defined, design matrix shouldn't be full"

    # nrow or ncol = None
    # these need to be promises as we don't know the other dimensions

    l7 = cow.layout(ncol = 3)
    l8 = cow.layout(nrow = 4)

    assert l7._layout__design is None and \
        l8._layout__design is None, \
        "if only ncol (exculsive) or nrows are defined, design matrix "+\
        "shouldn't be full"



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
    width_pt1 = 300
    height_pt1 = 200

    layout1 = cow.layout(design = design1)
    areas1 = layout1._element_locations(width_pt=width_pt1,
                                        height_pt=height_pt1)
    areas1_e = [cow.area(x_left=100, y_top=0,
                    width=200,height=100,
                    _type="pt"),
               cow.area(x_left=0, y_top=100,
                    width=200,height=100,
                    _type="pt")]

    assert np.all([areas1[l_idx] == areas1_e[l_idx] for l_idx in [0,1]]), \
        "error in expected areas returned from simple layout (1)," +\
        " - potentially w.r.t. np.nans in design matrix"

    # design 2 : different shapes of plots
    design2 = np.array([[0,0,2,2],
                         [0,0,3,3],
                         [1,1,3,3]])

    rel_heights2 = np.array([1,2,1])
    rel_widths2 = np.array([1,1,2,3])
    width_pt2 = 280
    height_pt2 = 140

    layout2 = cow.layout(design = design2,
                         rel_heights = rel_heights2,
                         rel_widths = rel_widths2)
    areas2 = layout2._element_locations(width_pt=width_pt2,
                                        height_pt=height_pt2)

    loc1_p_e = cow.area(x_left=0,
                y_top=0,
                width=2/7 * 280,
                height=3/4 * 140,
                _type="pt")

    loc2_p_e = cow.area(x_left=0,
                y_top=3/4 * 140,
                width=2/7 * 280,
                height=1/4 * 140,
                _type="pt")

    loc3_p_e = cow.area(x_left=2/7 * 280,
                y_top=0,
                width=5/7 * 280,
                height=1/4 * 140,
                _type="pt")

    loc4_p_e = cow.area(x_left=2/7 * 280,
                y_top=1/4 * 140,
                width=5/7 * 280,
                height=3/4 * 140,
                _type="pt")
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

def test_layout__not_eq__():
    """
    test layout equal for things not equal... (basic test)
    """
    design1 = np.array([[np.nan, 0, 0],
                       [1,2, np.nan]])
    design3 = """
    #AA
    BB#
    """

    l1 = cow.layout(design = design1)
    l3 = cow.layout(design = design3)

    assert l1 != l3, \
        "two different layouts shouldn't be equal to each other (l1, l3)"

    assert l1 != "example string", \
        "layout doesn't equal a string..."

def test_layout__eq__():
    """
    test for equal layout even if not complete (nrow, ncol)
    """
    l1 = cow.layout(nrow = 1)
    l2 = cow.layout(nrow=1)

    assert l1 == l2, \
        "expected equality of layout even if not complete (nrow, but no ncol)"

    l1 = cow.layout(ncol = 1)
    l2 = cow.layout(ncol=1)

    assert l1 == l2, \
        "expected equality of layout even if not complete (ncol, but no nrow)"



def test_layout__element_locations2():
    """
    test assumes default relative widths and heights
    """
    l1 = cow.layout(design = np.array([[0,0,0,1,1,1],
                                       [0,0,0,2,2,2],
                                       [0,0,0,2,2,2]]))

    areas1 = l1._element_locations(width_pt=200,
                                   height_pt=90)

    assert np.allclose(areas1[0].width, 100) and \
        np.allclose(areas1[0].height, 90) and \
        np.allclose(areas1[0].x_left, 0) and \
        np.allclose(areas1[0].y_top, 0) and \
            np.allclose(areas1[1].width, 100) and \
        np.allclose(areas1[1].height, 30) and \
        np.allclose(areas1[1].x_left, 100) and \
        np.allclose(areas1[1].y_top, 0) and \
            np.allclose(areas1[2].width, 100) and \
        np.allclose(areas1[2].height, 60) and \
        np.allclose(areas1[2].x_left, 100) and \
        np.allclose(areas1[2].y_top, 30), \
        "areas relative to layout incorrectly sized (design input)"

    # only nrow input (full column) -------
    l2 = cow.layout(nrow = 3)

    areas2 = l2._element_locations(width_pt=200,
                                   height_pt=90, num_grobs = 3)

    assert np.allclose(areas2[0].width, 200) and \
        np.allclose(areas2[0].height, 30) and \
        np.allclose(areas2[0].x_left, 0) and \
        np.allclose(areas2[0].y_top, 0) and \
            np.allclose(areas2[1].width, 200) and \
        np.allclose(areas2[1].height, 30) and \
        np.allclose(areas2[1].x_left, 0) and \
        np.allclose(areas2[1].y_top, 30) and \
            np.allclose(areas2[2].width, 200) and \
        np.allclose(areas2[2].height, 30) and \
        np.allclose(areas2[2].x_left, 0) and \
        np.allclose(areas2[2].y_top, 60),\
        "areas relative to layout incorrectly sized (nrow=3)"

    # only nrow input (non-full column) -------

    areas2_4 = l2._element_locations(width_pt=200,
                                   height_pt=90, num_grobs = 4)

    assert np.allclose(areas2_4[0].width, 100) and \
        np.allclose(areas2_4[0].height, 30) and \
        np.allclose(areas2_4[0].x_left, 0) and \
        np.allclose(areas2_4[0].y_top, 0) and \
            np.allclose(areas2_4[1].width, 100) and \
        np.allclose(areas2_4[1].height, 30) and \
        np.allclose(areas2_4[1].x_left, 100) and \
        np.allclose(areas2_4[1].y_top, 0) and \
            np.allclose(areas2_4[2].width, 100) and \
        np.allclose(areas2_4[2].height, 30) and \
        np.allclose(areas2_4[2].x_left, 0) and \
        np.allclose(areas2_4[2].y_top, 30) and \
            np.allclose(areas2_4[3].width, 100) and \
        np.allclose(areas2_4[3].height, 30) and \
        np.allclose(areas2_4[3].x_left, 100) and \
        np.allclose(areas2_4[3].y_top, 30), \
        "areas relative to layout incorrectly sized (nrow=3, grobs = 4)"


    areas2_5 = l2._element_locations(width_pt=200,
                                   height_pt=90, num_grobs = 5)

    assert np.allclose(areas2_5[0].width, 100) and \
        np.allclose(areas2_5[0].height, 30) and \
        np.allclose(areas2_5[0].x_left, 0) and \
        np.allclose(areas2_5[0].y_top, 0) and \
            np.allclose(areas2_5[1].width, 100) and \
        np.allclose(areas2_5[1].height, 30) and \
        np.allclose(areas2_5[1].x_left, 100) and \
        np.allclose(areas2_5[1].y_top, 0) and \
            np.allclose(areas2_5[2].width, 100) and \
        np.allclose(areas2_5[2].height, 30) and \
        np.allclose(areas2_5[2].x_left, 0) and \
        np.allclose(areas2_5[2].y_top, 30) and \
            np.allclose(areas2_5[3].width, 100) and \
        np.allclose(areas2_5[3].height, 30) and \
        np.allclose(areas2_5[3].x_left, 100) and \
        np.allclose(areas2_5[3].y_top, 30) and \
            np.allclose(areas2_5[4].width, 100) and \
        np.allclose(areas2_5[4].height, 30) and \
        np.allclose(areas2_5[4].x_left, 0) and \
        np.allclose(areas2_5[4].y_top, 60), \
        "areas relative to layout incorrectly sized (nrow=3, grobs = 5)"



    # bycol ---
    l2_bc = cow.layout(nrow = 3,byrow=False)
    areas2_4_bc = l2_bc._element_locations(width_pt=200,
                                   height_pt=90, num_grobs = 4)

    assert np.allclose(areas2_4_bc[0].width, 100) and \
        np.allclose(areas2_4_bc[0].height, 30) and \
        np.allclose(areas2_4_bc[0].x_left, 0) and \
        np.allclose(areas2_4_bc[0].y_top, 0) and \
            np.allclose(areas2_4_bc[1].width, 100) and \
        np.allclose(areas2_4_bc[1].height, 30) and \
        np.allclose(areas2_4_bc[1].x_left, 0) and \
        np.allclose(areas2_4_bc[1].y_top, 30) and \
            np.allclose(areas2_4_bc[2].width, 100) and \
        np.allclose(areas2_4_bc[2].height, 30) and \
        np.allclose(areas2_4_bc[2].x_left, 0) and \
        np.allclose(areas2_4_bc[2].y_top, 60) and \
            np.allclose(areas2_4_bc[3].width, 100) and \
        np.allclose(areas2_4_bc[3].height, 30) and \
        np.allclose(areas2_4_bc[3].x_left, 100) and \
        np.allclose(areas2_4_bc[3].y_top, 0), \
        "areas relative to layout incorrectly sized (nrow=3, grobs = 4, bycol)"


    # only nrow input (full column) -------
    l3 = cow.layout(ncol = 4)

    areas3 = l3._element_locations(width_pt=200,
                                   height_pt=90, num_grobs = 4)

    assert np.allclose(areas3[0].width, 50) and \
        np.allclose(areas3[0].height, 90) and \
        np.allclose(areas3[0].x_left, 0) and \
        np.allclose(areas3[0].y_top, 0) and \
            np.allclose(areas3[1].width, 50) and \
        np.allclose(areas3[1].height, 90) and \
        np.allclose(areas3[1].x_left, 50) and \
        np.allclose(areas3[1].y_top, 0) and \
            np.allclose(areas3[2].width, 50) and \
        np.allclose(areas3[2].height, 90) and \
        np.allclose(areas3[2].x_left, 100) and \
        np.allclose(areas3[2].y_top, 0) and \
            np.allclose(areas3[3].width, 50) and \
        np.allclose(areas3[3].height, 90) and \
        np.allclose(areas3[3].x_left, 150) and \
        np.allclose(areas3[3].y_top, 0), \
        "areas relative to layout incorrectly sized (ncol=4, grobs=4)"

    areas3_5 = l3._element_locations(width_pt=200,
                                   height_pt=90, num_grobs = 5)

    assert np.allclose(areas3_5[0].width, 50) and \
        np.allclose(areas3_5[0].height, 45) and \
        np.allclose(areas3_5[0].x_left, 0) and \
        np.allclose(areas3_5[0].y_top, 0) and \
            np.allclose(areas3_5[1].width, 50) and \
        np.allclose(areas3_5[1].height, 45) and \
        np.allclose(areas3_5[1].x_left, 50) and \
        np.allclose(areas3_5[1].y_top, 0) and \
            np.allclose(areas3_5[2].width, 50) and \
        np.allclose(areas3_5[2].height, 45) and \
        np.allclose(areas3_5[2].x_left, 100) and \
        np.allclose(areas3_5[2].y_top, 0) and \
            np.allclose(areas3_5[3].width, 50) and \
        np.allclose(areas3_5[3].height, 45) and \
        np.allclose(areas3_5[3].x_left, 150) and \
        np.allclose(areas3_5[3].y_top, 0) and \
            np.allclose(areas3_5[4].width, 50) and \
        np.allclose(areas3_5[4].height, 45) and \
        np.allclose(areas3_5[4].x_left, 0) and \
        np.allclose(areas3_5[4].y_top, 45), \
        "areas relative to layout incorrectly sized (ncol=4, grobs=5)"

    areas3_6 = l3._element_locations(width_pt=200,
                                   height_pt=90, num_grobs = 6)

    assert np.allclose(areas3_6[0].width, 50) and \
        np.allclose(areas3_6[0].height, 45) and \
        np.allclose(areas3_6[0].x_left, 0) and \
        np.allclose(areas3_6[0].y_top, 0) and \
            np.allclose(areas3_6[1].width, 50) and \
        np.allclose(areas3_6[1].height, 45) and \
        np.allclose(areas3_6[1].x_left, 50) and \
        np.allclose(areas3_6[1].y_top, 0) and \
            np.allclose(areas3_6[2].width, 50) and \
        np.allclose(areas3_6[2].height, 45) and \
        np.allclose(areas3_6[2].x_left, 100) and \
        np.allclose(areas3_6[2].y_top, 0) and \
            np.allclose(areas3_6[3].width, 50) and \
        np.allclose(areas3_6[3].height, 45) and \
        np.allclose(areas3_6[3].x_left, 150) and \
        np.allclose(areas3_6[3].y_top, 0) and \
            np.allclose(areas3_6[4].width, 50) and \
        np.allclose(areas3_6[4].height, 45) and \
        np.allclose(areas3_6[4].x_left, 0) and \
        np.allclose(areas3_6[4].y_top, 45) and \
            np.allclose(areas3_6[5].width, 50) and \
        np.allclose(areas3_6[5].height, 45) and \
        np.allclose(areas3_6[5].x_left, 50) and \
        np.allclose(areas3_6[5].y_top, 45), \
        "areas relative to layout incorrectly sized (ncol=4, grobs=6)"


    l3_bc = cow.layout(ncol = 4, byrow = False)

    areas3_5_bc = l3_bc._element_locations(width_pt=200,
                                   height_pt=90, num_grobs = 5)

    assert np.allclose(areas3_5_bc[0].width, 50) and \
        np.allclose(areas3_5_bc[0].height, 45) and \
        np.allclose(areas3_5_bc[0].x_left, 0) and \
        np.allclose(areas3_5_bc[0].y_top, 0) and \
            np.allclose(areas3_5_bc[1].width, 50) and \
        np.allclose(areas3_5_bc[1].height, 45) and \
        np.allclose(areas3_5_bc[1].x_left, 0) and \
        np.allclose(areas3_5_bc[1].y_top, 45) and \
            np.allclose(areas3_5_bc[2].width, 50) and \
        np.allclose(areas3_5_bc[2].height, 45) and \
        np.allclose(areas3_5_bc[2].x_left, 50) and \
        np.allclose(areas3_5_bc[2].y_top, 0) and \
            np.allclose(areas3_5_bc[3].width, 50) and \
        np.allclose(areas3_5_bc[3].height, 45) and \
        np.allclose(areas3_5_bc[3].x_left, 50) and \
        np.allclose(areas3_5_bc[3].y_top, 45) and \
            np.allclose(areas3_5_bc[4].width, 50) and \
        np.allclose(areas3_5_bc[4].height, 45) and \
        np.allclose(areas3_5_bc[4].x_left, 100) and \
        np.allclose(areas3_5_bc[4].y_top, 0), \
        "areas relative to layout incorrectly sized (ncol=4, grobs=5, bycol)"


    # TODO: too many grobs? (in patch or layout??)

def test_layout__str__(capsys):
    """
    make sure that print(layout_obj) works correctly
    """
    print(cow.layout(design = np.array([[0,0,0,1,1,1],
                                               [0,0,0,2,2,2],
                                               [0,0,0,2,2,2]])))

    captured = capsys.readouterr()
    re_cap = re.search(r"<layout \(-{0,1}[0-9]+\)>\n", captured.out)
    assert re_cap is not None and \
        re_cap.start() == 0 and re_cap.end() == len(captured.out),\
        "expected __str__ expression for layout to be of <layout (num)> format (1)"

    print(cow.layout(design = """
                                     AB
                                     AC
                                     AC
                                     """))

    captured = capsys.readouterr()
    re_cap = re.search(r"<layout \(-{0,1}[0-9]+\)>\n", captured.out)
    assert re_cap is not None and \
        re_cap.start() == 0 and re_cap.end() == len(captured.out),\
        "expected __str__ expression for layout to be of <layout (num)> format (2)"

    print(cow.layout(ncol=3))

    captured = capsys.readouterr()
    re_cap = re.search(r"<layout \(-{0,1}[0-9]+\)>\n", captured.out)
    assert re_cap is not None and \
        re_cap.start() == 0 and re_cap.end() == len(captured.out),\
        "expected __str__ expression for layout to be of <layout (num)> format (3)"

    print(cow.layout(nrow=2))

    captured = capsys.readouterr()
    re_cap = re.search(r"<layout \(-{0,1}[0-9]+\)>\n", captured.out)
    assert re_cap is not None and \
        re_cap.start() == 0 and re_cap.end() == len(captured.out),\
        "expected __str__ expression for layout to be of <layout (num)> format (4)"

    print(cow.layout(nrow=2,ncol=3))

    captured = capsys.readouterr()
    re_cap = re.search(r"<layout \(-{0,1}[0-9]+\)>\n", captured.out)
    assert re_cap is not None and \
        re_cap.start() == 0 and re_cap.end() == len(captured.out),\
        "expected __str__ expression for layout to be of <layout (num)> format (5)"
    print(cow.layout(nrow=1, rel_widths = [1,1,2]))

    captured = capsys.readouterr()
    re_cap = re.search(r"<layout \(-{0,1}[0-9]+\)>\n", captured.out)
    assert re_cap is not None and \
        re_cap.start() == 0 and re_cap.end() == len(captured.out),\
        "expected __str__ expression for layout to be of <layout (num)> format (6)"

    print(cow.layout(nrow=2, rel_widths = [1,2],
                            rel_heights = [1,2]))

    captured = capsys.readouterr()
    re_cap = re.search(r"<layout \(-{0,1}[0-9]+\)>\n", captured.out)
    assert re_cap is not None and \
        re_cap.start() == 0 and re_cap.end() == len(captured.out),\
        "expected __str__ expression for layout to be of <layout (num)> format (1)"

def test_layout__str__(capsys):
    """
    make sure that print(layout_obj) works correctly
    """

    layouts = [cow.layout(design = np.array([[0,0,0,1,1,1],
                                               [0,0,0,2,2,2],
                                               [0,0,0,2,2,2]])),
                cow.layout(design = """
                                     AB
                                     AC
                                     AC
                                     """),
                cow.layout(ncol=3),
                cow.layout(nrow=2),
                cow.layout(nrow=2,ncol=3),
                cow.layout(nrow=1, rel_widths = [1,1,2]),
                cow.layout(nrow=2, rel_widths = [1,2],
                            rel_heights = [1,2])]


    for l_idx, la in enumerate(layouts):
        print(repr(la))
        captured = capsys.readouterr()

        # we're not checking the design info...
        re_cap = re.search(r"^<layout \(-{0,1}[0-9]+\)>\ndesign \(([0-9]+|unk), "+\
                           r"([0-9]+|unk)\):\n\n", captured.out)
        re_cap_end = re.search(r"\n\nwidths:\n(\[([0-9]*\.*[0-9]*\s*)+\]|unk)"+\
                               r"\nheights:\n(\[([0-9]*\.*[0-9]*\s*)+\]|unk)\n$",
                               captured.out)
        assert re_cap is not None and \
            re_cap.start() == 0 and \
            re_cap_end is not None and \
            re_cap_end.end() == len(captured.out), \
            "expected __str__ expression for layout is more descriptive with" +\
            " design info and widths and lengths (%i)" % l_idx



def test_layout_design_versus_relative_sizing():
    """
    this also examines such problems with empty spaces.
    """
    with pytest.raises(Exception) as e_info:
        mylayout = cow.layout(design = """
                                            A#BB
                                            ACC#
                                            """,
                                     rel_heights = [1,2],
                                     rel_widths = [3,1,1])
        # relative widths need to be length 4...

    with pytest.raises(Exception) as e_info:
        mylayout = cow.layout(design = """
                                            A#BB
                                            ACC#
                                            ACC#
                                            """,
                                     rel_heights = [1,2],
                                     rel_widths = [3,1,1,1])
        # relative heights need to be length 3...

    with pytest.raises(Exception) as e_info:
        mylayout = cow.layout(design = """
                                            A.BB
                                            ACC.
                                            """,
                                     rel_heights = [1,2],
                                     rel_widths = [3,1,1])
        # relative widths need to be length 4...
    with pytest.raises(Exception) as e_info:
        mylayout = cow.layout(design = """
                                            A.BB
                                            ACC.
                                            ACC.
                                            """,
                                     rel_heights = [1,2],
                                     rel_widths = [3,1,1,1])
        # relative heights need to be length 3...


    with pytest.raises(Exception) as e_info:
        mylayout = cow.layout(design =np.array([[0,np.nan,1,1],
                                                [0,2,2,np.nan]]),
                                     rel_heights = [1,2],
                                     rel_widths = [3,1,1])
        # relative widths need to be length 4...
    with pytest.raises(Exception) as e_info:
        mylayout = cow.layout(design = np.array([[0,np.nan,1,1],
                                                 [0,2,2,np.nan],
                                                 [0,2,2,np.nan]]),
                                     rel_heights = [1,2],
                                     rel_widths = [3,1,1,1])
        # relative heights need to be length 3...


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
    width_pt = 280
    height_pt = 140

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


    # convert to points (2 ways!) -----------

    # direct to .pt
    loc1_p1 = loc1.pt(rel_widths=rel_widths,
                      rel_heights=rel_heights,
                      width_pt=width_pt,
                      height_pt=height_pt)
    loc2_p1 = loc2.pt(rel_widths=rel_widths,
                      rel_heights=rel_heights,
                      width_pt=width_pt,
                      height_pt=height_pt)
    loc3_p1 = loc3.pt(rel_widths=rel_widths,
                      rel_heights=rel_heights,
                      width_pt=width_pt,
                      height_pt=height_pt)
    loc4_p1 = loc4.pt(rel_widths=rel_widths,
                      rel_heights=rel_heights,
                      width_pt=width_pt,
                      height_pt=height_pt)

    # through internals
    loc1_p2 = loc1_r._relative_to_pt(width_pt=width_pt,
                                      height_pt=height_pt)
    loc2_p2 = loc2_r._relative_to_pt(width_pt=width_pt,
                                      height_pt=height_pt)
    loc3_p2 = loc3_r._relative_to_pt(width_pt=width_pt,
                                      height_pt=height_pt)
    loc4_p2 = loc4_r._relative_to_pt(width_pt=width_pt,
                                      height_pt=height_pt)

    # expected
    loc1_p_e = cow.area(x_left=0,
                y_top=0,
                width=2/7 * 280,
                height=3/4 * 140,
                _type="pt")

    loc2_p_e = cow.area(x_left=0,
                y_top=3/4 * 140,
                width=2/7 * 280,
                height=1/4 * 140,
                _type="pt")

    loc3_p_e = cow.area(x_left=2/7 * 280,
                y_top=0,
                width=5/7 * 280,
                height=1/4 * 140,
                _type="pt")

    loc4_p_e = cow.area(x_left=2/7 * 280,
                y_top=1/4 * 140,
                width=5/7 * 280,
                height=3/4 * 140,
                _type="pt")

    # .pt
    assert loc1_p1 == loc1_p_e, \
        "transform of design to pt (.pt) represent for static example failed (1)"

    assert loc2_p1 == loc2_p_e, \
        "transform of design to pt (.pt) represent for static example failed (2)"

    assert loc3_p1 == loc3_p_e, \
        "transform of design to pt (.pt) represent for static example failed (3)"

    assert loc4_p1 == loc4_p_e, \
        "transform of design to pt (.pt) represent for static example failed (4)"

    #  relative to pt
    assert loc1_p2 == loc1_p_e, \
        "transform of relative to pt represent for static example failed (1)"

    assert loc2_p2 == loc2_p_e, \
        "transform of relative to pt represent for static example failed (2)"

    assert loc3_p2 == loc3_p_e, \
        "transform of relative to pt represent for static example failed (3)"

    assert loc4_p2 == loc4_p_e, \
        "transform of relative to pt represent for static example failed (4)"

    # errors for bad parameter input ------------

    # RELATIVE #

    # relative: pt accidentally described as _type
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
    # # design: pt accidentally described as _type
    # with pytest.raises(Exception) as e_info:
    #     loc_design_error_pt = cow.area(x_left=0,
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

    # PT #

    # pt: 0 width
    with pytest.raises(Exception) as e_info:
        loc_pt_error_0_width = cow.area(x_left=0,
                y_top=0,
                width=0,
                height=3* 280,
                _type="pt")
    # pt: 0 height
    with pytest.raises(Exception) as e_info:
        loc_pt_error_0_width = cow.area(x_left=0,
                y_top=0,
                width=1* 280,
                height=0,
                _type="pt")


    # pt: neg x_left
    with pytest.raises(Exception) as e_info:
        loc_pt_error_neg_x = cow.area(x_left=-1* 280,
                y_top=0,
                width=2* 280,
                height=3* 280,
                _type="pt")
    # pt: 0 height
    with pytest.raises(Exception) as e_info:
        loc_pt_error_neg_y = cow.area(x_left=0,
                y_top=-1* 280,
                width=1/2* 280,
                height=1/2* 280,
                _type="pt")

def test_area__str__(capsys):
    print(cow.area(1,1,1,1, "pt"))

    captured = capsys.readouterr()

    re_cap = re.search(r"<area \(-{0,1}[0-9]+\)>\n", captured.out)
    assert re_cap is not None and \
        re_cap.start() == 0 and re_cap.end() == len(captured.out),\
        "expected __str__ expression for area to be of <area (num)> format (1)"

    print(cow.area(1,1,1,1, "relative"))

    captured = capsys.readouterr()
    re_cap = re.search(r"<area \(-{0,1}[0-9]+\)>\n", captured.out)
    assert re_cap is not None and \
        re_cap.start() == 0 and re_cap.end() == len(captured.out),\
        "expected __str__ expression for area to be of <area (num)> format (1)"

    print(cow.area(1,1,1,1, "design"))

    captured = capsys.readouterr()
    re_cap = re.search(r"<area \(-{0,1}[0-9]+\)>\n", captured.out)
    assert re_cap is not None and \
        re_cap.start() == 0 and re_cap.end() == len(captured.out),\
        "expected __str__ expression for area to be of <area (num)> format (1)"


def test_area__repr__(capsys):

    areas = [cow.area(1,1,1,1, "pt"),
             cow.area(1,1,1,1, "relative"),
             cow.area(1,1,1,1, "design")]
    for a_idx, aa in enumerate(areas):
        print(repr(aa))
        captured = capsys.readouterr()

        re_cap = re.search(r"<area \(-{0,1}[0-9]+\)>\n" +\
                           r"_type: (pt|relative|design)\n\n"+\
                           r"x_left: 1\ny_top: 1\nwidth: 1\nheight: 1\n", captured.out)
        assert re_cap is not None and \
            re_cap.start() == 0 and re_cap.end() == len(captured.out),\
            "expected __str__ expression for area to be of <area (num)> format (1)"

