from pytest_regressions import image_regression
from hypothesis import given, strategies as st, settings

import numpy as np
import cowpatch as cow
from cowpatch.utils import inherits, _flatten_nested_list, \
                            _transform_size_to_pt, to_inches
from cowpatch.config import rcParams

import pytest
import io
import itertools

import plotnine as p9
import plotnine.data as p9_data

import re
import matplotlib.pyplot as plt

import svgutils.transform as sg


# inner functions -----

def test_patch__init__():
    """
    test patch's __init__ function to collecting grobs

    Note:
    this test will likely have to converted to passing in
    plotnine and other patch objects...
    """
    mtcars = p9_data.mpg

    p0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.facet_wrap("cyl") +\
        p9.labs(title = 'Plot 0')

    p1 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 1')

    p2 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 2')

    mypatch = cow.patch(grobs = [p0, p1, p2])
    assert len(mypatch.grobs) == 3, \
        "grobs can be passed through the grobs parameter directly"

    mypatch_args = cow.patch(p0, p1, p2)
    assert len(mypatch_args.grobs) == 3, \
        "grobs can be passed through the grobs parameter indirectly"

    with pytest.raises(Exception) as e_info:
            mypatch_both = cow.patch(p0, p1, p2,
                                     grobs = [p0, p1, p2])
            # can't pass grobs through both the parameter and *args

    # struture allows for nesting
    mypatch2 = cow.patch(grobs = [p0, p1, mypatch])
    assert len(mypatch2.grobs) == 3, \
        "grobs can be passed through the grobs parameter directly"

    mypatch_args2 = cow.patch(p0, p1, mypatch)
    assert len(mypatch_args2.grobs) == 3, \
        "grobs can be passed through the grobs parameter indirectly"

def test_patch_layout():
    """
    tests when default layout appears and that it's correct

    static tests
    """

    p0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.facet_wrap("cyl") +\
        p9.labs(title = 'Plot 0')

    p1 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 1')

    p2 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 2')


    # 3 elements
    base = cow.patch(grobs=[p0,p1,p2])
    out_layout = base.layout

    assert base._layout == "patch" and \
        out_layout == cow.layout(nrow=3, ncol=1), \
        "if only 3 grobs & no layout, expect presented in a single column display"

    base1 = base + cow.layout(nrow=2, ncol=2)
    out_layout1 = base1.layout

    assert base1._layout == out_layout1 and \
        out_layout1 == cow.layout(nrow=2, ncol=2), \
        "layout added to patch should be the one returned (complete layout)"


    base2 = base + cow.layout(nrow=2)
    out_layout2 = base2.layout

    assert base2._layout == out_layout2 and \
        out_layout2 == cow.layout(nrow=2), \
        "layout added to patch should be the one returned (partical layout)"

    # 4 elements
    base = cow.patch(grobs=[p0,p1,p2,p0])
    out_layout = base.layout


    assert base._layout == "patch" and \
        out_layout == cow.layout(nrow=2, ncol=2), \
        "if only 4 grobs & no layout, expect presented in a 2 x 2 display"


    # > 4 elements
    ngrobs = np.random.choice(np.arange(5,31))
    nrow = int(np.ceil(np.sqrt(ngrobs)))
    ncol = int(np.ceil(ngrobs / nrow))
    base_large = cow.patch(grobs=[p0 for i in range(ngrobs)])
    out_layout_large = base_large.layout

    assert base_large._layout == "patch" and \
        out_layout_large == cow.layout(nrow=nrow, ncol=ncol) and \
        nrow*ncol >= ngrobs, \
        ("if only %i grobs & no layout, expect presented in a "+
         "sqrt(n) x sqrt(n)-ish display") % ngrobs

def test_patch_annotation():
    """
    tests when default annotation appears and that it's correct

    static tests
    """

    p0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.facet_wrap("cyl") +\
        p9.labs(title = 'Plot 0')

    p1 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 1')

    p2 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 2')


    # none, 3 grobs
    base = cow.patch(grobs=[p0,p1,p2])
    out_ann = base.annotation

    assert base._annotation == None and \
        out_ann == cow.annotation(tags_inherit="override"), \
        "if no annotation set, basic one defined (base has grobs)"

    # none, no grobs
    base0 = cow.patch()
    out_ann0 = base0.annotation


    assert base0._annotation == None and \
        out_ann0 == cow.annotation(tags_inherit="override"), \
        "if no annotation set, basic one defined (base has no grobs)"


    # with annotation object
    for title, subtitle, caption in \
        itertools.product(["title", cow.text("title"), {"bottom":"title"},
                    {"bottom": cow.text("title")},
                    {"left": 'ltitle', "bottom":"btitle"},
                    {"left": cow.text('ltitle'), "bottom": cow.text("btitle")},
                     None],
                     ["subtitle", cow.text("subtitle"), {"bottom":"subtitle"},
                    {"bottom": cow.text("subtitle")},
                    {"left": 'lsubtitle', "bottom":"bsubtitle"},
                    {"left": cow.text('lsubtitle'), "bottom": cow.text("bsubtitle")},
                     None],
                     [None, "caption", cow.text("caption")]):

        base_full1 = base + cow.annotation(title=title,subtitle=subtitle,
                                      caption=caption)
        out_ann_full1 = base_full1.annotation

        assert base_full1._annotation == out_ann_full1 and \
            out_ann_full1 == cow.annotation(title=title,subtitle=subtitle,
                                      caption=caption), \
            ("annotation properties shouldn't be updated by patch, \n" +
             "title: {title}, subtitle: {subtitle}, caption: {caption}".\
                format(title=title,subtitle=subtitle,caption=caption))

    for tags, tags_loc, tags_inherit in \
        itertools.product(
                     [('1',), ("0", "a"), ["banana", "apple"],
                     (["banana", "apple"], "a") , None],
                     ["top", "bottom", "left", "right", None],
                     ["fix", "override"]):

        base_full2 = base + cow.annotation(tags=tags,
                                      tags_loc=tags_loc,
                                      tags_inherit=tags_inherit)
        out_annotation_full2 = base_full2.annotation

        assert base_full2._annotation == out_annotation_full2 and \
            out_annotation_full2 == cow.annotation(tags=tags,
                                      tags_loc=tags_loc,
                                      tags_inherit=tags_inherit), \
            ("annotation properties shouldn't be updated by patch, \n" +
             "tags: {tags}, tags_loc: {tags_loc}, tags_inherit: {tags_inherit}".\
                format(tags=tags,tags_loc=tags_loc, tags_inherit=tags_inherit))


def test_patch__get_grob_tag_ordering():
    """
    test patch's internal _get_grob_tag_ordering
    """
    g0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.labs(title = 'Plot 0')

    g1 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 1')

    g2 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 2')

    g3 = p9.ggplot(p9_data.mpg[p9_data.mpg["class"].isin(["compact",
                                                         "suv",
                                                         "pickup"])]) +\
        p9.geom_histogram(p9.aes(x="hwy"),bins=10) +\
        p9.facet_wrap("class")

    # basic option ----------
    vis0 = cow.patch(g1,g0,g2)


    # with layout ------------
    visl1 = vis0 +\
        cow.layout(design = np.array([[1,0],
                                      [1,2]]),
                   rel_heights = [1,2])

    o_l1 = visl1._get_grob_tag_ordering()

    assert np.all(np.array([None]*3) == o_l1), \
        "if no tags, we expect tag ordering to be a array of Nones for "+\
        "each grob (with defined layout - l1)"

    visl2 = visl1 +\
        cow.annotation(title = "Combination")

    o_l2 = visl2._get_grob_tag_ordering()

    assert np.all(np.array([None]*3) == o_l2), \
        "if no tags, we expect tag ordering to be a array of Nones for "+\
        "each grob (with defined layout, some annotation - l2)"

    visl3 = visl2 + cow.annotation(tags = ["Figure 0"]) # tag_order = "auto" (input)

    o_l3 = visl3._get_grob_tag_ordering()

    assert np.all(np.array([0, None, None]) == o_l3), \
        "with tag_order =\"auto\" (leads to input) and a shorter list of "+\
        "tags than the full set observations (and with some early order "+\
        "observations without tags, one should expect some nones and so "+\
        "non-nones in the grob_tag_ordering (with defined layout - l3)"


    visl3_1 = visl2 + cow.annotation(tags = ["Figure 0"], tags_order="input")

    o_l3_1 = visl3_1._get_grob_tag_ordering()


    assert np.all(np.array([0, None, None]) == o_l3_1), \
        "with tag_order =\"input\" and a shorter list of "+\
        "tags than the full set observations (and with some early order "+\
        "observations without tags, one should expect some nones and so "+\
        "non-nones in the grob_tag_ordering (with defined layout - l3_1)"

    visl3_2 = visl2 + cow.annotation(tags = ["Figure 0"], tags_order="yokogaki")

    o_l3_2 = visl3_2._get_grob_tag_ordering()


    assert np.all(np.array([None, 0, None]) == o_l3_2), \
        "with tag_order =\"yokogaki\" and a shorter list of "+\
        "tags than the full set observations (and with some early order "+\
        "observations without tags, one should expect some nones and so "+\
        "non-nones in the grob_tag_ordering (with defined layout - l3_2)"

    visl4 = visl2 + cow.annotation(tags_format = ("Figure {0}",),
                                   tags = ("0", )) # tag_order = "auto" (yokogaki)


    o_l4 = visl4._get_grob_tag_ordering()

    assert np.all(np.array([1,0,2]) == o_l4), \
        "with tag_order =\"auto\" (leads to yokogaki) and tuple for tags, "+\
        "in the grob_tag_ordering (with defined layout - o_l4)"


    visl4_1 = visl2 + cow.annotation(tags_format = ("Figure {0}",),
                                   tags = ("0", ), tags_order="input")

    o_l4_1 = visl4_1._get_grob_tag_ordering()

    assert np.all(np.array([0,1,2]) == o_l4_1), \
        "with tag_order =\"input\" and tuple for tags, "+\
        "in the grob_tag_ordering (with defined layout - o_l4_1)"


    visl4_2 = visl2 + cow.annotation(tags_format = ("Figure {0}",),
                                   tags = ("0", ), tags_order="yokogaki")

    o_l4_2 = visl4_2._get_grob_tag_ordering()

    assert np.all(np.array([1,0,2]) == o_l4_2), \
        "with tag_order =\"yokogaki\" and tuple for tags, "+\
        "in the grob_tag_ordering (with defined layout - o_l4_2)"



    # without layout ------------

    vis_nol_2 = vis0 +\
        cow.annotation(title = "Combination")

    o_nol_2 = vis_nol_2._get_grob_tag_ordering()

    assert np.all(np.array([None]*3) == o_nol_2), \
        "if no tags, we expect tag ordering to be a array of Nones for "+\
        "each grob (with no defined layout - nol_2)"


    vis_nol_3 = vis_nol_2 + cow.annotation(tags = ["Figure 0"]) # tag_order = "auto" (input)

    o_nol_3 = vis_nol_3._get_grob_tag_ordering()


    assert np.all(np.array([0,None,None]) == o_nol_3), \
        "with tag_order =\"auto\" (leads to input) and a shorter list of "+\
        "tags than the full set observations (with no defined layout - nol_3)"

    vis_nol_3_1 = vis_nol_2 + cow.annotation(tags = ["Figure 0"],
                                             tags_order="input")

    o_nol_3_1 = vis_nol_3_1._get_grob_tag_ordering()

    assert np.all(np.array([0,None,None]) == o_nol_3_1), \
        "with tag_order =\"input\" and a shorter list of "+\
        "tags than the full set observations (with no defined layout - nol_3_1)"


    vis_nol_3_2 = vis_nol_2 + cow.annotation(tags = ["Figure 0"],
                                             tags_order="yokogaki")
    o_nol_3_2 = vis_nol_3_2._get_grob_tag_ordering()

    assert np.all(np.array([0,None,None]) == o_nol_3_2), \
        "with tag_order =\"yokogaki\" and a shorter list of "+\
        "tags than the full set observations (with no defined layout - nol_3_2)"



    vis_nol_4 = vis_nol_2 + cow.annotation(tags_format = ("Figure {0}",),
                                   tags = ("0", )) # tag_order = "auto" (yokogaki)

    o_nol_4 = vis_nol_4._get_grob_tag_ordering()

    assert np.all(np.array([0,1,2]) == o_nol_4), \
        "with tag_order =\"auto\" and tuple for tags, "+\
        "in the grob_tag_ordering (with no defined layout - o_nol_4)"


    vis_nol_4_1 = vis_nol_2 + cow.annotation(tags_format = ("Figure {0}",),
                                   tags = ("0", ), tags_order="input")

    o_nol_4_1 = vis_nol_4_1._get_grob_tag_ordering()

    assert np.all(np.array([0,1,2]) == o_l4_1), \
        "with tag_order =\"input\" and tuple for tags, "+\
        "in the grob_tag_ordering (with no defined layout - o_nol_4_1)"

    vis_nol_4_2 = vis_nol_2 + cow.annotation(tags_format = ("Figure {0}",),
                                   tags = ("0", ), tags_order="yokogaki")

    o_nol_4_2 = vis_nol_4_2._get_grob_tag_ordering()

    assert np.all(np.array([0,1,2]) == o_nol_4_2), \
        "with tag_order =\"yokogaki\" and tuple for tags, "+\
        "in the grob_tag_ordering (with no defined layout - o_nol_4_2)"

def test_patch__get_grob_tag_ordering2():
    """
    static testing of _get_grob_tag_ordering
    """
    g0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.labs(title = 'Plot 0')

    g1 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 1')

    g2 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 2')

    g3 = p9.ggplot(p9_data.mpg[p9_data.mpg["class"].isin(["compact",
                                                         "suv",
                                                         "pickup"])]) +\
        p9.geom_histogram(p9.aes(x="hwy"), bins=10) +\
        p9.facet_wrap("class")

    my_patch = cow.patch(g0,g1,g2,g3)
    my_layout = cow.layout(design = np.array([[0,0,0,3,3,3],
                                               [0,0,0,2,2,2],
                                               [1,1,1,2,2,2]]))

    my_annotation1 = cow.annotation(tags = ("Fig {0}",), tags_format = ("a",),
                                    tags_order = "auto")
    my_annotation2 = cow.annotation(tags = ["Fig 1", "Fig 2", "Fig 3"], # notice this isn't complete...
                                    tags_order = "auto")
    # yokogaki ----
    my_a_y1 = my_annotation1 + cow.annotation(tags_order = "yokogaki")
    vis_y1 = my_patch + my_layout + my_a_y1

    out_y1 = vis_y1._get_grob_tag_ordering()

    assert np.all(out_y1 == np.array([0,3,2,1])), \
        "yokogaki ordering incorrect (static example 1, tuple tags)"

    my_a_y1_auto = my_annotation1
    vis_y1_auto = my_patch + my_layout + my_a_y1_auto

    out_y1_auto = vis_y1_auto._get_grob_tag_ordering()

    assert np.all(out_y1_auto == np.array([0,3,2,1])), \
        "yokogaki ordering incorrect - auto tags_order (static example "+\
        "1_auto, tuple tags)"

    my_a_y2 = my_annotation2 + cow.annotation(tags_order = "yokogaki")
    vis_y2 = my_patch + my_layout + my_a_y2

    out_y2 = vis_y2._get_grob_tag_ordering()

    assert np.all(out_y2 == np.array([0,None,2,1])), \
        "yokogaki ordering incorrect (static example 2, list tags)"

    # input ----
    my_a_i1 = my_annotation1 + cow.annotation(tags_order = "input")
    vis_i1 = my_patch + my_layout + my_a_i1

    out_i1 = vis_i1._get_grob_tag_ordering()

    assert np.all(out_i1 == np.array([0,1,2,3])), \
        "input ordering incorrect (static example 1, tuple tags)"

    my_a_i2 = my_annotation2 + cow.annotation(tags_order = "input")
    vis_i2 = my_patch + my_layout + my_a_i2

    out_i2 = vis_i2._get_grob_tag_ordering()

    assert np.all(out_i2 == np.array([0,1,2,None])), \
        "input ordering incorrect (static example 2, list tags)"

    my_a_i2_auto = my_annotation2 + cow.annotation(tags_order = "auto")
    vis_i2_auto = my_patch + my_layout + my_a_i2_auto

    out_i2_auto = vis_i2_auto._get_grob_tag_ordering()

    assert np.all(out_i2_auto == np.array([0,1,2,None])), \
        "input ordering incorrect - auto tag ordering (static example 2, list tags)"

    # no tags (different ways) -----

    my_n1_a = my_annotation1 + \
        cow.annotation(tags = np.nan, tags_order = "auto")
    vis_n1_a = my_patch + my_layout + my_n1_a
    out_n1_a = vis_n1_a._get_grob_tag_ordering()

    assert np.all(out_n1_a == np.array([None]*4)), \
        "if tags are missing, we expect the _get_grob_tag_ordering to "+\
        "return an empty array (static example 1 - np.nan override, auto)"

    my_n1_y = my_annotation1 + \
        cow.annotation(tags = np.nan, tags_order = "yokogaki")
    vis_n1_y = my_patch + my_layout + my_n1_y
    out_n1_y = vis_n1_y._get_grob_tag_ordering()

    assert np.all(out_n1_y == np.array([None]*4)), \
        "if tags are missing, we expect the _get_grob_tag_ordering to "+\
        "return an empty array (static example 1 - np.nan override, yokogaki)"

    my_n1_i = my_annotation1 + \
        cow.annotation(tags = np.nan, tags_order = "input")
    vis_n1_i = my_patch + my_layout + my_n1_i
    out_n1_i = vis_n1_i._get_grob_tag_ordering()

    assert np.all(out_n1_i == np.array([None]*4)), \
        "if tags are missing, we expect the _get_grob_tag_ordering to "+\
        "return an empty array (static example 1 - np.nan override, input)"




    my_n2_a = my_annotation2 + \
        cow.annotation(tags = np.nan, tags_order = "auto")
    vis_n2_a = my_patch + my_layout + my_n2_a
    out_n2_a = vis_n2_a._get_grob_tag_ordering()

    assert np.all(out_n2_a == np.array([None]*4)), \
        "if tags are missing, we expect the _get_grob_tag_ordering to "+\
        "return an empty array (static example 2 - np.nan override, auto)"

    my_n2_y = my_annotation2 + \
        cow.annotation(tags = np.nan, tags_order = "yokogaki")
    vis_n2_y = my_patch + my_layout + my_n2_y
    out_n2_y = vis_n2_y._get_grob_tag_ordering()

    assert np.all(out_n2_y == np.array([None]*4)), \
        "if tags are missing, we expect the _get_grob_tag_ordering to "+\
        "return an empty array (static example 2 - np.nan override, yokogaki)"

    my_n2_i = my_annotation2 + \
        cow.annotation(tags = np.nan, tags_order = "input")
    vis_n2_i = my_patch + my_layout + my_n2_i
    out_n2_i = vis_n2_i._get_grob_tag_ordering()

    assert np.all(out_n2_i == np.array([None]*4)), \
        "if tags are missing, we expect the _get_grob_tag_ordering to "+\
        "return an empty array (static example 2 - np.nan override, input)"


    vis_n_n = my_patch + my_layout
    out_n_a = vis_n_n._get_grob_tag_ordering()


    assert np.all(out_n_a == np.array([None]*4)), \
        "if annotation object itelf is missing, we expect the "+\
        "_get_grob_tag_ordering to return an empty array"


def test_patch__default_size_NoAnnotation():
    g0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.labs(title = 'Plot 0')

    g1 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 1')

    g2 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 2')

    g3 = p9.ggplot(p9_data.mpg[p9_data.mpg["class"].isin(["compact",
                                                         "suv",
                                                         "pickup"])]) +\
        p9.geom_histogram(p9.aes(x="hwy"),bins=10) +\
        p9.facet_wrap("class")

    # basic option ----------
    vis1 = cow.patch(g0,g1,g2) +\
        cow.layout(design = np.array([[0,1],
                                      [0,2]]),
                   rel_heights = [1,2])

    sug_width, sug_height = \
        vis1._default_size()

    assert np.allclose(sug_width,
                        (2 * # 1/ rel width of smallest width of images
                         cow.rcParams["base_height"] *
                         cow.rcParams["base_aspect_ratio"])), \
        "suggested width incorrectly sizes the smallest width of the images "+\
        "(v1, no annotation)"

    assert np.allclose(sug_height,
                       (3 * # 1/ rel width of smallest width of images
                        cow.rcParams["base_height"])), \
        "suggested height incorrectly sizes the smallest height of the images "+\
        "- rel_heights example (v1, no annotation)"


    # nested option --------
    vis_nested = cow.patch(g0,cow.patch(g1,g2)+\
                        cow.layout(ncol=1, rel_heights = [1,2])) +\
        cow.layout(nrow=1)


    sug_width_n, sug_height_n = \
        vis_nested._default_size()

    assert np.allclose(sug_width_n,
                        (2 * # 1/ rel width of smallest width of images
                         cow.rcParams["base_height"] *
                         cow.rcParams["base_aspect_ratio"])), \
        "suggested width incorrectly sizes the smallest width of the images "+\
        "(v2 - nested, no annotation)"

    assert np.allclose(sug_height_n,
                       (3 * # 1/ rel width of smallest width of images
                        cow.rcParams["base_height"])), \
        "suggested height incorrectly sizes the smallest height of the images "+\
        "(v2 - nested, no annotation)"

def test_patch__default_size_Annotation():
    g0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.labs(title = 'Plot 0')

    g1 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 1')

    g2 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 2')

    # basic option ----------
    vis1 = cow.patch(g0,g1,g2) +\
        cow.layout(design = np.array([[0,1],
                                      [0,2]]),
                   rel_heights = [1,2]) +\
        cow.annotation(title = "My title")

    sug_width, sug_height = \
        vis1._default_size()

    assert np.allclose(sug_width,
                        (2 * # 1/ rel width of smallest width of images
                         cow.rcParams["base_height"] *
                         cow.rcParams["base_aspect_ratio"])), \
        "suggested width incorrectly sizes the smallest width of the images (v1, annotation)"

    assert np.allclose(sug_height,
                       (3 * # 1/ rel width of smallest width of images
                        cow.rcParams["base_height"] +\
                        cow.text("My title", _type="cow_title").\
                            _min_size(to_inches=True)[1]
                       )
                        ), \
        "suggested height incorrectly sizes the smallest height of the images (v1, annotation)"


    # nested option --------
    vis_nested = cow.patch(g0,cow.patch(g1,g2)+\
                        cow.layout(ncol=1, rel_heights = [1,2])) +\
        cow.layout(nrow=1) +\
        cow.annotation(subtitle = "My subtitle")


    sug_width_n, sug_height_n = \
        vis_nested._default_size()

    assert np.allclose(sug_width_n,
                        (2 * # 1/ rel width of smallest width of images
                         cow.rcParams["base_height"] *
                         cow.rcParams["base_aspect_ratio"])), \
        "suggested width incorrectly sizes the smallest width of the images "+\
        "(v2 - nested, annotation)"

    assert np.allclose(sug_height_n,
                       (3 * # 1/ rel width of smallest width of images
                        cow.rcParams["base_height"] +\
                        cow.text("My subtitle", _type="cow_subtitle").\
                            _min_size(to_inches=True)[1]
                        )), \
        "suggested height incorrectly sizes the smallest height of the images "+\
        "(v2 - nested, annotation)"

    # tag nested option (explicit tags_inherit="override")-----------
    vis_nested_tag = cow.patch(g0,cow.patch(g1,g2)+\
                        cow.layout(ncol=1, rel_heights = [1,2]) +\
                        cow.annotation(tags_inherit="override")) +\
        cow.layout(nrow=1) +\
        cow.annotation(caption = "My caption") +\
        cow.annotation(tags=("0", "a"), tags_format=("Fig {0}", "Fig {0}.{1}"),
                       tags_loc="top")

    sug_width_nt, sug_height_nt = \
        vis_nested_tag._default_size()

    assert np.allclose(sug_width_nt,
                        (2 * # 1/ rel width of smallest width of images
                         cow.rcParams["base_height"] *
                         cow.rcParams["base_aspect_ratio"])), \
        "suggested width incorrectly sizes the smallest width of the images "+\
        "(v2 - nested + tagged, annotation - explicit tags_inherit=\"override\")"

    assert np.allclose(sug_height_nt,
                       (3 * # 1/ rel width of smallest width of images (and include the caption and 1 tag)
                        (cow.rcParams["base_height"] +\
                        cow.text("Fig 01ab", _type="cow_tag").\
                            _min_size(to_inches=True)[1]) +\
                        cow.text("My caption", _type="cow_caption").\
                            _min_size(to_inches=True)[1])), \
        "suggested height incorrectly sizes the smallest height of the images "+\
        "(v2 - nested + tagged, annotation - explicit tags_inherit=\"override\")"

    # tag nested option (implicit tags_inherit="override")-----------
    vis_nested_tag_i = cow.patch(g0,cow.patch(g1,g2)+\
                        cow.layout(ncol=1, rel_heights = [1,2])) +\
        cow.layout(nrow=1) +\
        cow.annotation(caption = "My caption") +\
        cow.annotation(tags=("0", "a"), tags_format=("Fig {0}", "Fig {0}.{1}"),
                       tags_loc="top")

    sug_width_nt_i, sug_height_nt_i = \
        vis_nested_tag_i._default_size()

    assert np.allclose(sug_width_nt_i,
                        (2 * # 1/ rel width of smallest width of images
                         cow.rcParams["base_height"] *
                         cow.rcParams["base_aspect_ratio"])), \
        "suggested width incorrectly sizes the smallest width of the images "+\
        "(v2 - nested + tagged, annotation - implicit tags_inherit=\"override\")"

    assert np.allclose(sug_height_nt_i,
                       (3 * # 1/ rel width of smallest width of images (and include the caption and 1 tag)
                        (cow.rcParams["base_height"] +\
                        cow.text("Fig 01ab", _type="cow_tag").\
                            _min_size(to_inches=True)[1]) +\
                        cow.text("My caption", _type="cow_caption").\
                            _min_size(to_inches=True)[1])), \
        "suggested height incorrectly sizes the smallest height of the images "+\
        "(v2 - nested + tagged, annotation - implicit tags_inherit=\"override\")"

def test_patch_default_size_TextNoAnnotation():
    """
    test of patch's _default_size

    Static test to ensure sizes of text objects minimum sizing correctly
    alter default_size output if needed. Also, actual examples ensure that
    there any error in `_min_size` call relative to `to_inches` parameter
    is not occuring.

    Note:
    this test doesn't combine text objects with annotation (so it fits
    in the NoAnnotation approach). For now we're not going to test that
    option.
    """
    # basic option (text fits in desired box) ----------

    t0 = cow.text("An approximate answer to the right problem\n"+
                  "is worth a good deal more than an exact\n"+
                  "answer to an approximate problem. ~John Tukey") +\
        p9.element_text(size = 15)

    t1 = cow.text("If I can’t picture it,\n"+
                  "I can’t understand it. ~Albert Einstein") +\
        p9.element_text(size = 17, ha="left")

    t2 = cow.text("Tables usually outperform graphics in\n"+
                  "reporting on small data sets of 20\n"+
                  "numbers or less. ~John Tukey") +\
        p9.element_text(size=12, ha="left")

    vis1 = cow.patch(t0, t1, t2) +\
        cow.layout(design = np.array([[0,1],
                                      [0,2]]),
                   rel_heights = [1,2])

    sug_width, sug_height = vis1._default_size()

    assert np.allclose(sug_width,
                        (2 * # 1/ rel width of smallest width of images
                         cow.rcParams["base_height"] *
                         cow.rcParams["base_aspect_ratio"])), \
        ("when text size elements in image *don't require* larger-than rcParams "+
        "sizing, width sizing should match rcParam related expectation "+
        "(no annotation)")

    assert np.allclose(sug_height,
                       (3 * # 1/ rel width of smallest width of images
                        cow.rcParams["base_height"])), \
        ("when text size elements in image *don't require* larger-than rcParams "+
        "sizing, height sizing should match rcParam related expectation "+
        "(no annotation)")

    m_w0, m_h0 = t0._min_size(to_inches=True)
    m_w1, m_h1 = t1._min_size(to_inches=True)
    m_w2, m_h2 = t2._min_size(to_inches=True)

    assert ((sug_height >= m_h0) and
        (2/3 * sug_height >= m_h2) and
        (1/3 * sug_height >= m_h1)) and \
        ((1/2 * sug_width >= m_w0) and
            (1/2 * sug_width >= m_w2) and
            (1/2 * sug_width >= m_w1)), \
        ("when text size elements in image *don't require* larger-than rcParams "+
         "the min size of text objects should be less than or equal to allocated "+
         "sizing for the image (no annotation)")


    # second option (text doesn't fits in desired box) ----------

    t0_2 = cow.text("An approximate answer to the right problem\n"+
                  "is worth a good deal more than an exact\n"+
                  "answer to an approximate problem. ~John Tukey") +\
        p9.element_text(size = 25)

    t1_2 = cow.text("If I can’t picture it,\n"+
                  "I can’t understand it. ~Albert Einstein") +\
        p9.element_text(size = 20, ha="left")

    t2_2 = cow.text("Tables usually outperform graphics in\n"+
                  "reporting on small data sets of 20\n"+
                  "numbers or less. ~John Tukey") +\
        p9.element_text(size=25, ha="left")

    vis2 = cow.patch(t0_2, t1_2, t2_2) +\
        cow.layout(design = np.array([[0,1],
                                      [0,2]]),
                   rel_heights = [1,2])


    sug_width_2, sug_height_2 = vis2._default_size()

    assert (sug_width_2 >=
                        (2 * # 1/ rel width of smallest width of images
                         cow.rcParams["base_height"] *
                         cow.rcParams["base_aspect_ratio"])), \
        ("when text size elements in image *require* larger-than rcParams "+
        "sizing, width sizing be greater or equal to rcParam related expectation "+
        "(no annotation)")

    assert (sug_height_2 >=
                       (3 * # 1/ rel width of smallest width of images
                        cow.rcParams["base_height"])), \
        ("when text size elements in image *require* larger-than rcParams "+
        "sizing, height sizing be greater or equal to rcParam related expectation "+
        "(no annotation)")

    m_w0_2, m_h0_2 = t0_2._min_size(to_inches=True)
    m_w1_2, m_h1_2 = t1_2._min_size(to_inches=True)
    m_w2_2, m_h2_2 = t2_2._min_size(to_inches=True)

    assert ((sug_height_2 >= m_h0_2) and
        (2/3 * sug_height_2 >= m_h2_2) and
        (1/3 * sug_height_2 >= m_h1_2)) and \
        ((1/2 * sug_width_2 >= m_w0_2) and
            (1/2 * sug_width_2 >= m_w2_2) and
            (1/2 * sug_width_2 >= m_w1_2)), \
        ("when text size elements in image *require* larger-than rcParams "+
         "the min size of text objects should be less than or equal to allocated "+
         "sizing for the image (no annotation)")

    assert ((2 * # 1/ rel width of smallest width of images
                         cow.rcParams["base_height"] *
                         cow.rcParams["base_aspect_ratio"]) <
            np.max([2 * m_w0_2, 2 * m_w1_2,  2 * m_w2_2])) or \
            ((3 * # 1/ rel width of smallest width of images
                        cow.rcParams["base_height"]) <
            np.max([m_h0_2, 3/2 * m_h2_2,  3 * m_h1_2])), \
        ("inner test to, ensuring that second example provides case where "+
         "text size element in image *require* larger-than rcParams "+
         "default sizing (specifically width, but code allows for either)")





def test_patch__doable_size_SimpleText():
    """
    testing patch's _doable_size functionality

    test focuses on only text objects that would correctly fit inside
    the suggested size
    """
    # overall tests should deal with (1) annotations (title & tags)
    # (2) nested & not nested (3) vary with too small and acceptably sized
    # figures.

    # 1. test only text attributes (start with default_size)
    # should see sizing directly relate to default_size

    # basic option (text fits in desired box) ----------

    t0 = cow.text("An approximate answer to the right problem\n"+
                  "is worth a good deal more than an exact\n"+
                  "answer to an approximate problem. ~John Tukey") +\
        p9.element_text(size = 15)

    t1 = cow.text("If I can’t picture it,\n"+
                  "I can’t understand it. ~Albert Einstein") +\
        p9.element_text(size = 17, ha="left")

    t2 = cow.text("Tables usually outperform graphics in\n"+
                  "reporting on small data sets of 20\n"+
                  "numbers or less. ~John Tukey") +\
        p9.element_text(size=12, ha="left")

    t3 = cow.text(label="Pardon my French.\n"+
                  "~Non-French speaking person") +\
        p9.element_text(size = 20)

    vis1 = cow.patch(t0, t2, t3) +\
        cow.layout(design = np.array([[0,1],
                                      [0,2]]),
                   rel_heights = [1,2])

    sug_width, sug_height = vis1._default_size()

    sizes_list, doable = vis1._doable_size(width=sug_width, height=sug_height)

    sizes_list_in = np.array([[to_inches(x[0], "pt"), to_inches(x[1], "pt")]
                                for x in sizes_list])

    assert doable, \
        ("if patch's width & height for doable_size is much higher than "+
        "minimum size possible, _doable_size should return doable")

    assert np.allclose([sug_width/2]*3, sizes_list_in[:,0]) and \
        np.allclose(sizes_list_in[:,0].min(),
                    rcParams["base_height"] * rcParams["base_aspect_ratio"]) and \
        ("if static patch uses default size, expected width sizing "+
        "should be met (both relative to rcParams & structure mult)")

    assert np.allclose(sug_height * np.array([1,1/3,2/3]), sizes_list_in[:,1]) and \
        np.allclose(sizes_list_in[:,1].min(),
                    rcParams["base_height"]) and \
        ("if static patch uses default size, expected height sizing "+
        "should be met (both relative to rcParams & structure mult)")


    # non-minimum _default_sizing used:

    sug_width2, sug_height2 = 15,30
    sizes_list2, doable2 = vis1._doable_size(width=sug_width2, height=sug_height2)

    sizes_list_in2 = np.array([[to_inches(x[0], "pt"), to_inches(x[1], "pt")]
                                for x in sizes_list2])

    assert doable2, \
        ("if patch's width & height for doable_size is much higher than "+
        "minimum size possible, size > _doable_size should return doable")

    assert np.allclose([sug_width2/2]*3, sizes_list_in2[:,0]) and \
            (sizes_list_in2[:,0].min() >
             rcParams["base_height"] * rcParams["base_aspect_ratio"]) and \
        ("if static patch uses sizes > default size, expected width sizing "+
        "should be met relative to input sizing")

    assert np.allclose(sug_height2 * np.array([1,1/3,2/3]), sizes_list_in2[:,1]) and \
            (sizes_list_in2[:,1].min() >
                    rcParams["base_height"]) and \
        ("if static patch uses sizes > default size, expected height sizing "+
        "should be met relative to input sizing")



    # nested structure, _default_sizing used:
    vis1_nested = cow.patch(grobs = [t0,
                            cow.patch(t2, t3) + cow.layout(design = np.array([[0],[1],[1]]))]) +\
        cow.layout(design = np.array([[0,1]]))


    sug_width_n, sug_height_n = vis1_nested._default_size()

    sizes_list_n, doable_n = vis1_nested.\
        _doable_size(width=sug_width_n, height=sug_height_n)

    sizes_list_n_in = np.array([[to_inches(x[0], "pt"), to_inches(x[1], "pt")]
                                        for x in sizes_list_n[:1]] +
                            [[to_inches(x[0], "pt"), to_inches(x[1], "pt")]
                                        for x in sizes_list_n[1]])

    assert doable_n, \
        ("if patch's width & height for doable_size is much higher than "+
        "minimum size possible, _doable_size should return doable - nested")

    assert np.allclose([sug_width_n/2]*3, sizes_list_n_in[:,0]) and \
        np.allclose(sizes_list_n_in[:,0].min(),
                    rcParams["base_height"] * rcParams["base_aspect_ratio"]) and \
        ("if static patch uses default size, expected width sizing "+
        "should be met (both relative to rcParams & structure mult) - nested")

    assert np.allclose(sug_height_n * np.array([1,1/3,2/3]),
                       sizes_list_n_in[:,1]) and \
        np.allclose(sizes_list_n_in[:,1].min(),
                    rcParams["base_height"]) and \
        ("if static patch uses default size, expected height sizing "+
        "should be met (both relative to rcParams & structure mult) - nested")


    # nested structure, non-minimum _default_sizing used:


    sug_width2, sug_height2 = 15,30
    sizes_list_n2, doable_n2 = vis1_nested.\
        _doable_size(width=sug_width2, height=sug_height2)

    sizes_list_n_in2 = np.array([[to_inches(x[0], "pt"), to_inches(x[1], "pt")]
                                        for x in sizes_list_n2[:1]] +
                            [[to_inches(x[0], "pt"), to_inches(x[1], "pt")]
                                        for x in sizes_list_n2[1]])

    assert doable_n2, \
        ("if patch's width & height for doable_size is much higher than "+
        "minimum size possible, size > _doable_size should return doable - nested")

    assert np.allclose([sug_width2/2]*3, sizes_list_n_in2[:,0]) and \
            (sizes_list_n_in2[:,0].min() >
             rcParams["base_height"] * rcParams["base_aspect_ratio"]) and \
        ("if static patch uses sizes > default size, expected width sizing "+
        "should be met relative to input sizing - nested")

    assert np.allclose(sug_height2 * np.array([1,1/3,2/3]),
                       sizes_list_n_in2[:,1]) and \
            (sizes_list_n_in2[:,1].min() >
                    rcParams["base_height"]) and \
        ("if static patch uses sizes > default size, expected height sizing "+
        "should be met relative to input sizing - nested")




    # second option (text doesn't fits in desired box) ----------

    t0_2 = cow.text("An approximate answer to the right problem\n"+
                  "is worth a good deal more than an exact\n"+
                  "answer to an approximate problem. ~John Tukey") +\
        p9.element_text(size = 25)

    t1_2 = cow.text("If I can’t picture it,\n"+
                  "I can’t understand it. ~Albert Einstein") +\
        p9.element_text(size = 20, ha="left")

    t2_2 = cow.text("Tables usually outperform graphics in\n"+
                  "reporting on small data sets of 20\n"+
                  "numbers or less. ~John Tukey") +\
        p9.element_text(size=25, ha="left")

    vis_nf = cow.patch(t0_2, t1_2, t2_2) +\
        cow.layout(design = np.array([[0,1],
                                      [0,2]]),
                   rel_heights = [1,2])

    sug_width_nf = 2 * rcParams["base_height"] * rcParams["base_aspect_ratio"]
    sug_height_nf = 3 * rcParams["base_height"]

    sug_width_nf_min, sug_height_nf_min = vis_nf._default_size()

    assert (sug_width_nf < sug_width_nf_min) and \
        (sug_height_nf <= sug_height_nf_min), \
        ("test structure (that rcParams default size is too small for " +
        "figure creation) was incorrectly defined (needed width is larger)")

    sizes_list_nf, doable_nf = vis_nf.\
        _doable_size(width=sug_width_nf, height=sug_height_nf,
                     data_dict = {"size-num-attempts": 1})

    sizes_list_nf_in = np.array([[to_inches(x[0], "pt"), to_inches(x[1], "pt")]
                                for x in sizes_list_nf])

    vis_nf._doable_size(width=sug_width_nf_min, height=sug_height_nf_min)



    # nested


def test_patch_doable_size_StaticNonSimple():
    """
    testing patch's _doable_size functionality

    test focuses on varability in acutal requested size
    based on plotnine's varying correct input size required
    """
    # overall tests should deal with (1) annotations (title & tags)
    # (2) nested & not nested (3) vary with too small and acceptably sized
    # figures.

    # 2. write a second test with ggplot images and save the size
    # for a regression test (data_regression)





# def test_patch__svg_get_sizes():
#     g0 = p9.ggplot(p9_data.mpg) +\
#         p9.geom_bar(p9.aes(x="hwy")) +\
#         p9.labs(title = 'Plot 0')

#     g1 = p9.ggplot(p9_data.mpg) +\
#         p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
#         p9.labs(title = 'Plot 1')

#     g2 = p9.ggplot(p9_data.mpg) +\
#         p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
#         p9.labs(title = 'Plot 2')

#     g3 = p9.ggplot(p9_data.mpg[p9_data.mpg["class"].isin(["compact",
#                                                          "suv",
#                                                          "pickup"])]) +\
#         p9.geom_histogram(p9.aes(x="hwy"),bins=10) +\
#         p9.facet_wrap("class")


#     # basic option ----------
#     vis1 = cow.patch(g0,g1,g2) +\
#         cow.layout(design = np.array([[0,1],
#                                       [0,2]]),
#                    rel_heights = [4,1])

#     # successful sizings ----
#     sizes, logics = vis1._svg_get_sizes(width_pt = 20 * 72,
#                                         height_pt = 20 * 72)

#     requested_sizes = [(10,20), (10,16), (10,4)]

#     assert np.all(logics), \
#         "expected all plotnine objects to be able to be sized correctly "+\
#         "in very large output (v1)"

#     assert type(sizes) is list and \
#         np.all([len(s) == 2 and type(s) is tuple for s in sizes]), \
#         "expected structure of sizes list is incorrect (v1)"

#     assert np.all([2/3 < (sizes[s_idx][0]/requested_sizes[s_idx][0]) < 1.5 and \
#                     2/3 < (sizes[s_idx][1]/requested_sizes[s_idx][1]) < 1.5
#                     for s_idx in [0,1,2]]), \
#         "suggested sizing in sizes isn't too extreme relative to true "+\
#         "requested sizes- this is just a sanity check, "+\
#         "not a robust test (v1)"

#     # failed sizings ------
#     sizes_f, logics_f = vis1._svg_get_sizes(width_pt = 10 * 72,
#                                         height_pt = 10 * 72)

#     requested_sizes_f = [(5,10), (5,8), (5,2)] # final one should fail...

#     assert not np.all(logics_f) and (logics_f == [True, True, False]), \
#         "expected not all plotnine objects to be able to be sized correctly "+\
#         "in small output (v1.1 - failed)"

#     assert type(sizes_f) is list and \
#         np.all([len(s) == 2 and type(s) is tuple for s in sizes_f]), \
#         "expected structure of sizes list is incorrect (v1.1 - failed)"

#     assert np.all([2/3 < (sizes_f[s_idx][0]/requested_sizes_f[s_idx][0]) < 1.5 and \
#                     2/3 < (sizes_f[s_idx][1]/requested_sizes_f[s_idx][1]) < 1.5
#                     for s_idx in [0,1]]), \
#         "suggested sizing in sizes (that didn't fail) isn't too extreme "+\
#         "relative to true "+\
#         "requested sizes- this is just a sanity check, "+\
#         "not a robust test (v1.1 - failed)"

#     assert sizes_f[2][0] < 1 and sizes_f[2][1] < 1, \
#         "expected failed sizing (due to being too small, to return a scaling" +\
#         "below 1 (note the correction to scaling should be 1/suggested scaling))," +\
#         "(v1.1 - failed)"

#     # nested option --------
#     vis_nested = cow.patch(g0,cow.patch(g1, g2)+\
#                         cow.layout(ncol=1, rel_heights = [4,1])) +\
#         cow.layout(nrow=1)

#     # successful sizings ----
#     sizes_n, logics_n = vis_nested._svg_get_sizes(width_pt = 20 * 72,
#                                                   height_pt = 20 * 72)
#     requested_sizes_n = [(10,20), (10,16), (10,4)]

#     assert np.all(_flatten_nested_list(logics_n)), \
#         "expected all plotnine objects to be able to be sized correctly "+\
#         "in very large output (v2 - nested)"


#     assert type(sizes_n) is list and len(sizes_n) == 2 and \
#             type(sizes_n[0]) is tuple and type(sizes_n[1]) is list and \
#             len(sizes_n[0]) == 2 and len(sizes_n[1]) == 2 and \
#             np.all([len(s) == 2 and type(s) is tuple for s in sizes_n[1]]), \
#         "expected structure of sizes list is incorrect (v2 - nested)"

#     sizes_n_flattened = _flatten_nested_list(sizes_n)

#     assert np.all([2/3 < (sizes_n_flattened[s_idx][0]/requested_sizes[s_idx][0]) < 1.5 and \
#                     2/3 < (sizes_n_flattened[s_idx][1]/requested_sizes[s_idx][1]) < 1.5
#                     for s_idx in [0,1,2]]), \
#         "suggested sizing in sizes isn't too extreme relative to true "+\
#         "requested sizes- this is just a sanity check, "+\
#         "not a robust test (v2 - nested)"

#     assert np.allclose(sizes_n_flattened, sizes), \
#         "expected nested and non-nested suggested sizes to be equal (v1 vs v2)"

#     # failed sizings ------
#     sizes_f_n, logics_f_n = vis_nested._svg_get_sizes(width_pt = 10 * 72,
#                                         height_pt = 10 * 72)

#     requested_sizes_f = [(5,10), (5,8), (5,2)] # final one should fail ...

#     logic_f_n_flat = _flatten_nested_list(logics_f_n)
#     sizes_f_n_flat = _flatten_nested_list(sizes_f_n)

#     assert not np.all(logic_f_n_flat) and \
#             (logic_f_n_flat == [True, True, False]), \
#         "expected not all plotnine objects to be able to be sized correctly "+\
#         "in smaller output (v2.1 - nested, failed)"

#     assert type(sizes_f_n) is list and len(sizes_f_n) == 2 and \
#             type(sizes_f_n[0]) is tuple and type(sizes_f_n[1]) is list and \
#             len(sizes_f_n[0]) == 2 and len(sizes_f_n[1]) == 2 and \
#             np.all([len(s) == 2 and type(s) is tuple for s in sizes_f_n[1]]), \
#         "expected structure of sizes list is incorrect (v2.1 - nested, failed)"

#     assert np.all([2/3 < (sizes_f_n_flat[s_idx][0]/requested_sizes_f[s_idx][0]) < 1.5 and \
#                     2/3 < (sizes_f_n_flat[s_idx][1]/requested_sizes_f[s_idx][1]) < 1.5
#                     for s_idx in [0,1]]), \
#         "suggested sizing in sizes (that didn't fail) isn't too extreme "+\
#         "relative to true "+\
#         "requested sizes- this is just a sanity check, "+\
#         "not a robust test (v2.1 - nested, failed)"

#     assert sizes_f_n_flat[2][0] < 1 and sizes_f_n_flat[2][1] < 1, \
#         "expected failed sizing (due to being too small, to return a scaling" +\
#         "below 1 (note the correction to scaling should be 1/suggested scaling))," +\
#         "(v2.1 - nested, failed)"

#     assert np.allclose(sizes_f_n_flat, sizes_f), \
#         "expected nested and non-nested suggested sizes to be equal (v1.1 vs v2.1 - failed)"

# @given(st.floats(min_value=.5, max_value=49),
#        st.floats(min_value=.5, max_value=49),
#        st.floats(min_value=.5, max_value=49),
#        st.floats(min_value=.5, max_value=49),
#        st.floats(min_value=.5, max_value=49),
#        st.floats(min_value=.5, max_value=49))
# def test_patch__process_sizes(w1,h1,w2,h2,w3,h3):
#     # default patch (not needed)
#     empty_patch = cow.patch()

#     # not nested -------
#     sizes = [(w1,h1),(w2,h2),(w3,h3)]

#     # all true ---
#     logics = [True, True, True]

#     out_s = empty_patch._process_sizes(sizes = sizes, logics = logics)
#     assert out_s == sizes, \
#         "expected sizes to return if all logics true"

#     # not all true ----
#     logics_f = [True, True, False]
#     out_s1 = empty_patch._process_sizes(sizes = sizes, logics = logics_f)

#     assert np.allclose(out_s1, 1/np.min(sizes[2])), \
#         "expected max_scaling should be the max of 1/width_scale and "+\
#         "1/height_scale assoicated with failed plot(s) (v1.1 - 1 plot failed)"

#     logics_f2 = [True, False, False]
#     out_s2 = empty_patch._process_sizes(sizes = sizes, logics = logics_f2)

#     assert np.allclose(out_s2, 1/np.min([w2,h2,w3,h3])), \
#         "expected max_scaling should be the max of 1/width_scale and "+\
#         "1/height_scale assoicated with failed plot(s) (v1.2 - 2 plot failed)"

#     # nested ---------
#     sizes_n = [(w1,h1),[(w2,h2),(w3,h3)]]

#     # all true ---
#     logics_n = [True, [True, True]]
#     out_s_n = empty_patch._process_sizes(sizes = sizes_n, logics = logics_n)
#     assert out_s_n == sizes_n, \
#         "expected unflatted sizes to return if all logics true (v2 - nested)"

#     # not all true ----
#     logics_n_f = [True, [True, False]]
#     out_s1 = empty_patch._process_sizes(sizes = sizes_n, logics = logics_n_f)

#     assert np.allclose(out_s1, 1/np.min(sizes_n[1][1])), \
#         "expected max_scaling should be the max of 1/width_scale and "+\
#         "1/height_scale assoicated with failed plot(s) (v2.1 - 1 plot failed)"

#     logics_f2 = [True, [False, False]]
#     out_s2 = empty_patch._process_sizes(sizes = sizes, logics = logics_f2)

#     assert np.allclose(out_s2, 1/np.min([w2,h2,w3,h3])), \
#         "expected max_scaling should be the max of 1/width_scale and "+\
#         "1/height_scale assoicated with failed plot(s) (v2.2 - 2 plot failed)"


# global savings and showing and creating ------
def _layouts_and_patches_patch_plus_layout(idx):
    # creation of some some ggplot objects
    g0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.labs(title = 'Plot 0')

    g1 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 1')

    g2 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 2')

    g3 = p9.ggplot(p9_data.mpg[p9_data.mpg["class"].isin(["compact",
                                                         "suv",
                                                         "pickup"])]) +\
        p9.geom_histogram(p9.aes(x="hwy"), bins=10) +\
        p9.facet_wrap("class")


    if idx == 0:
        patch_obj = cow.patch(g0,g1,g2)
        layout_obj = cow.layout(design = np.array([[0,0,0,1,1,1],
                                                   [0,0,0,2,2,2],
                                                   [0,0,0,2,2,2]]))
    elif idx == 1:
        patch_obj = cow.patch(g0,g1,g2)
        layout_obj = cow.layout(design = """
                                         AB
                                         AC
                                         AC
                                         """)
    elif idx == 2:
        patch_obj = cow.patch(g0,g1,g2,g3)
        layout_obj = cow.layout(ncol=3)
    elif idx == 3:
        patch_obj = cow.patch(g0,g1,g2,g3)
        layout_obj = cow.layout(nrow=2)
    elif idx == 4:
        patch_obj = cow.patch(g0,g1,g2,g3)
        layout_obj = cow.layout(nrow=2,ncol=3)
    elif idx == 5:
        patch_obj = cow.patch(g0,g1,g2)
        layout_obj = cow.layout(nrow=1, rel_widths = [1,1,2])
    elif idx == 6:
        patch_obj = cow.patch(g0,g1,g2)
        layout_obj = cow.layout(nrow=2, rel_widths = [1,2],
                                rel_heights = [1,2])

    return patch_obj, layout_obj

@pytest.mark.parametrize("idx", np.arange(7,dtype=int))
def test_patch_plus_layout_second(image_regression, idx):
    """
    test patch + layout (varying)
    """
    patch_obj, layout_obj = _layouts_and_patches_patch_plus_layout(idx)

    vis_patch = patch_obj + layout_obj

    with io.BytesIO() as fid2:
        vis_patch.save(filename=fid2, width=12, height=10,
                       dpi=96, _format="png", verbose=False)
        image_regression.check(fid2.getvalue(), diff_threshold=.1)

def test_patch_plus_layout(image_regression):
    """
    test patch + layout
    """

    # creation of some some ggplot objects
    g0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.labs(title = 'Plot 0')

    g1_no_legend = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 1 no color')

    g1_legend = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 1 color')

    vis_patch = cow.patch(g0,g1_no_legend,g1_legend)
    vis_patch += cow.layout(design = np.array([[0,0,0,1,1,1],
                                               [0,0,0,2,2,2],
                                               [0,0,0,2,2,2]]))

    assert inherits(vis_patch, cow.patch), \
        "check patch addition correctly returns patch object"

    assert vis_patch._patch__layout == \
        cow.layout(design = np.array([[0,0,0,1,1,1],
                                      [0,0,0,2,2,2],
                                      [0,0,0,2,2,2]])) and \
        vis_patch.layout == \
        cow.layout(design = np.array([[0,0,0,1,1,1],
                                       [0,0,0,2,2,2],
                                       [0,0,0,2,2,2]])), \
        "layout incorrectly saved internally"

    with io.BytesIO() as fid2:
        vis_patch.save(filename=fid2, width=12, height=10,
                       dpi=96, _format="png", verbose=False)

        image_regression.check(fid2.getvalue(), diff_threshold=.1)

def test_patch_nesting(image_regression):
    """
    check that nesting does work as expected
    """
    g0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.labs(title = 'Plot 0')

    g1 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 1')

    g2 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 2')

    vis_left = cow.patch(g1,g2) + cow.layout(ncol = 1, rel_heights = [1,2])
    vis_patch = cow.patch(g0, vis_left) + cow.layout(nrow = 1)
    with io.BytesIO() as fid2:
        vis_patch.save(filename=fid2, width=12, height=7,
                       dpi=96, _format="png", verbose = False)

        image_regression.check(fid2.getvalue(), diff_threshold=.1)

def test_patch__svg():
    """
    static due to time it takes to run this test :(
    """
    height_in, width_in = 10, 10

    g0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.labs(title = 'Plot 0')

    g1 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 1')

    g2 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 2')

    vis_left = cow.patch(g1,g2) + cow.layout(ncol = 1, rel_heights = [4,1])
    vis_patch = cow.patch(g0, vis_left) + cow.layout(nrow = 1)

    svg_out, size = vis_patch._svg(width_pt = width_in*76,
                                   height_pt = height_in*76,
                                   num_attempts = 2)

    assert np.allclose(_transform_size_to_pt(svg_out.get_size()),
                       size), \
        "returned svg's size should match what was returned by _svg"

    assert np.allclose(size[0]/size[1], width_in/height_in) and \
        size[0] > width_in*76 and size[1] > height_in*76, \
        "if _svg has attempts to correct the size of the image, then " +\
        "it will change the size relative to requested, but keep aspect ratio"

    with pytest.raises(Exception) as e_info:
        svg_out, size = vis_patch._svg(width_pt = width_in*76,
                                       height_pt = height_in*76,
                                       num_attempts = 1) # no attempts to adjust

    assert e_info.typename == "StopIteration" and \
            e_info.value.args[0] == "Attempts to find the correct sizing of "+\
                                "innerplots failed with provided parameters", \
        "expected failure to create correct size image to be a certain "+\
        "class of error"

# printing ----------

def test_patch__str__(monkeypatch,capsys):
    """
    test patch .__str__, static

    print(.) also creates the figure
    """
    monkeypatch.setattr(plt, "show", lambda:None)

    g0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.labs(title = 'Plot 0')

    g1 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 1')

    g2 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 2')

    vis_left = cow.patch(g1,g2) + cow.layout(ncol = 1, rel_heights = [1,1])
    vis_patch = cow.patch(g0, vis_left) + cow.layout(nrow = 1)


    print(vis_patch)
    captured = capsys.readouterr()

    re_cap = re.search("<patch \(-{0,1}[0-9]+\)>\\n", captured.out)
    assert re_cap is not None and \
        re_cap.start() == 0 and re_cap.end() == len(captured.out),\
        "expected __str__ expression for patch to be of <patch (num)> format"

def test_patch__repr__(capsys):

    g0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.labs(title = 'Plot 0')

    g1 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 1')

    g2 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 2')

    vis_left = cow.patch(g1,g2) + cow.layout(ncol = 1, rel_heights = [1,1])
    vis_patch = cow.patch(g0, vis_left) + cow.layout(nrow = 1)

    print(repr(vis_patch))
    captured = capsys.readouterr()
    re_cap = re.search("^<patch \(-{0,1}[0-9]+\)>\\nnum_grobs: 2"+\
          "\\n---\\nlayout:\\n<layout \(-{0,1}[0-9]+\)>\\n", captured.out)

    assert re_cap is not None and \
        re_cap.start() == 0,\
        "expected __repr__ expression for patch more descriptive w.r.t."+\
        " # grobs and layout"


# uniquify -----------

def test_patch_svg_uniquify1(image_regression):
    """
    test 1: patch _svg creation use of svg_utils._unquify_svg_str

    1 x 2 direct use of cowpatch example
    """
    mtcars = p9_data.mtcars

    a = (p9.ggplot(mtcars)
        + p9.aes('wt', 'mpg', color='hp')
        + p9.geom_point()
        + p9.theme(figure_size=(3, 2))
        )

    b = (p9.ggplot(mtcars)
        + p9.aes('wt', 'mpg', color='hp')
        + p9.geom_point()
        + p9.scale_color_continuous('inferno')
        + p9.theme(figure_size=(3, 2))
        )

    combi_plot = cow.patch(a, b) + cow.layout(ncol=2)

    with io.BytesIO() as fid:
        combi_plot.save(filename=fid, width=8, height=3,
                       dpi=96, _format="png", verbose = False)

        image_regression.check(fid.getvalue(), diff_threshold=.1)


def test_patch_svg_uniquify2(image_regression):
    """
    test 2: patch _svg creation use of svg_utils._unquify_svg_str

    2 x 2 nested cowpatch example
    """
    mtcars = p9_data.mtcars

    a = (p9.ggplot(mtcars)
        + p9.aes('wt', 'mpg', color='hp')
        + p9.geom_point()
        + p9.theme(figure_size=(3, 2))
        )

    b = (p9.ggplot(mtcars)
        + p9.aes('wt', 'mpg', color='hp')
        + p9.geom_point()
        + p9.scale_color_continuous('inferno')
        + p9.theme(figure_size=(3, 2))
        )

    combi_plot = cow.patch(a, b) + cow.layout(ncol=2)

    combi_plot2 = combi_plot + cow.layout(design = np.array([[1,0]]))

    combo_combi = cow.patch(combi_plot, combi_plot2) + cow.layout(nrow = 2)

    with io.BytesIO() as fid:
        combo_combi.save(filename=fid, width=8, height=6,
                       dpi=96, _format="png", verbose = False)

        image_regression.check(fid.getvalue(), diff_threshold=.1)


def test_patch_svg_uniquify3(image_regression):
    """
    test 3: patch _svg creation use of svg_utils._unquify_svg_str

    2 x 2 manual cowpatch example
    """
    mtcars = p9_data.mtcars

    a = (p9.ggplot(mtcars)
        + p9.aes('wt', 'mpg', color='hp')
        + p9.geom_point()
        + p9.theme(figure_size=(3, 2))
        )

    b = (p9.ggplot(mtcars)
        + p9.aes('wt', 'mpg', color='hp')
        + p9.geom_point()
        + p9.scale_color_continuous('inferno')
        + p9.theme(figure_size=(3, 2))
        )

    base_image = sg.SVGFigure()
    base_image.set_size((str(8*72)+"pt", str(6*72)+"pt"))
    # add a view box... (set_size doesn't correctly update this...)
    # maybe should have used px instead of px....
    base_image.root.set("viewBox", "0 0 %s %s" % (str(8*72), str(6*72)))

    # TODO: way to make decisions about the base image...
    base_image.append(
        sg.fromstring("<rect width=\"100%\" height=\"100%\" fill=\"#FFFFFF\"/>"))


    combi_plot = cow.patch(a, b) + cow.layout(ncol=2)
    svg_obj, _ = combi_plot._svg(width_pt=8*72,
                              height_pt=3*72)

    svg_root = svg_obj.getroot()
    svg_root.moveto(x=0,
                    y=0)
    base_image.append(svg_root)

    combi_plot2 = combi_plot + cow.layout(design = np.array([[1,0]]))
    svg_obj2, _ = combi_plot2._svg(width_pt=8*72,
                               height_pt=3*72)

    svg_root2 = svg_obj2.getroot()
    svg_root2.moveto(x=0,
                    y=3*72)
    base_image.append(svg_root2)

    with io.BytesIO() as fid:
        cow.svg_utils._save_svg_wrapper(base_image,
                           filename=fid,
                           width=8,
                           height=6,
                           dpi=96,
                           _format="png",
                           verbose=False)

        image_regression.check(fid.getvalue(), diff_threshold=.1)



