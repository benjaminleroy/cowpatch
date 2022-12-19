from pytest_regressions import image_regression
from hypothesis import given, strategies as st, settings

import numpy as np
import cowpatch as cow
from cowpatch.utils import inherits, _flatten_nested_list, \
                            _transform_size_to_pt
import pytest
import io

import plotnine as p9
import plotnine.data as p9_data

import re
import matplotlib.pyplot as plt

import pdb

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

def test_patch__estimate_default_min_desired_size_NoAnnotation():
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
        vis1._hierarchical_general_process(approach="default-size")

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
        vis_nested._hierarchical_general_process(approach="default-size")

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

# TODO: test when some plots have tags, others don't
# TODO: this test (below) still needs to be examined
# See "TODO FIX" inside plot
def test_patch__estimate_default_min_desired_size_Annotation():
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
        vis1._hierarchical_general_process(approach="default-size")

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
        vis_nested._hierarchical_general_process(approach="default-size")

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
    
    # tag nested option -----------
    vis_nested_tag = cow.patch(g0,cow.patch(g1,g2)+\
                        cow.layout(ncol=1, rel_heights = [1,2]) +\
                        cow.annotation(tags_inherit="override")) +\
        cow.layout(nrow=1) +\
        cow.annotation(caption = "My caption") +\
        cow.annotation(tags=("0", "a"), tags_format=("Fig {0}", "Fig {0}.{1}"),
                       tags_loc="top")

    sug_width_nt, sug_height_nt = \
        vis_nested_tag._hierarchical_general_process(approach="default-size")

    assert np.allclose(sug_width_nt,
                        (2 * # 1/ rel width of smallest width of images
                         cow.rcParams["base_height"] *
                         cow.rcParams["base_aspect_ratio"])), \
        "suggested width incorrectly sizes the smallest width of the images "+\
        "(v2 - nested + tagged, annotation)"

    # TODO: this looks like the tag structure isn't being correctly taken into acount
    assert np.allclose(sug_height_nt,
                       (3 * # 1/ rel width of smallest width of images (and include the caption and 1 tag)
                        (cow.rcParams["base_height"] +\
                        cow.text("Fig 01ab", _type="cow_tag").\
                            _min_size(to_inches=True)[1]) +\
                        cow.text("My caption", _type="cow_caption").\
                            _min_size(to_inches=True)[1])), \
        "suggested height incorrectly sizes the smallest height of the images "+\
        "(v2 - nested + tagged, annotation)"               

def test_patch__default_size__both_none():
    """
    this test passes none for both parameters
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
    vis1 = cow.patch(g0,g1,g2) +\
        cow.layout(design = np.array([[0,1],
                                      [0,2]]),
                   rel_heights = [1,2])

    out_w, out_h = vis1._default_size(height=None,width=None)

    assert np.allclose(out_w,
                        (2 * # 1/ rel width of smallest width of images
                         cow.rcParams["base_height"] *
                         cow.rcParams["base_aspect_ratio"])), \
        "_default_size incorrectly connects with _size_dive output - width (v1)"

    assert np.allclose(out_h,
                       (3 * # 1/ rel width of smallest width of images
                        cow.rcParams["base_height"])), \
        "_default_size incorrectly connects with _size_dive output - height (v1)"


    # nested option --------
    vis_nested = cow.patch(g0,cow.patch(g1,g2)+\
                        cow.layout(ncol=1, rel_heights = [1,2])) +\
        cow.layout(nrow=1)

    out_w_n, out_h_n = vis_nested._default_size(height=None,width=None)

    assert np.allclose(out_w_n,
                        (2 * # 1/ rel width of smallest width of images
                         cow.rcParams["base_height"] *
                         cow.rcParams["base_aspect_ratio"])), \
        "_default_size incorrectly connects with _size_dive output - width (v2-nested)"

    assert np.allclose(out_h_n,
                       (3 * # 1/ rel width of smallest width of images
                        cow.rcParams["base_height"])), \
        "_default_size incorrectly connects with _size_dive output - height (v2-nested)"

def test_patch__default_size__both_not_none(height,width):
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

    out_w, out_h = vis1._default_size(height=height,width=width)
    assert out_w == width and out_h == height, \
        "if height and width are provided, they shouldn't be changed by "+\
        "default size function (v1 - no nesting)"

    # nested option --------
    vis_nested = cow.patch(g0,cow.patch(g1,g2)+\
                        cow.layout(ncol=1, rel_heights = [1,2])) +\
        cow.layout(nrow=1)

    out_w_n, out_h_n = vis_nested._default_size(height=height,width=width)
    assert out_w_n == width and out_h_n == height, \
        "if height and width are provided, they shouldn't be changed by "+\
        "default size function (v2 - nesting)"

@given(st.floats(min_value=.5, max_value=49))
def test_patch__default_size__one_none(height_or_width):
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

    default_w, default_h = vis1._default_size(None,None)
    static_aspect_ratio = default_h / default_w

    # provide width ----
    out_w, out_h = vis1._default_size(height=None,width=height_or_width)
    assert np.allclose(out_w, height_or_width) and \
        np.allclose(out_h, height_or_width * static_aspect_ratio), \
        "if *only width* is provided, suggested height is relative to aspect "+\
        "ratio that would be suggested if neither provided (v1)"

    # provide height ----
    out_w, out_h = vis1._default_size(height=height_or_width,width=None)
    assert np.allclose(out_h, height_or_width) and \
        np.allclose(out_w, height_or_width / static_aspect_ratio), \
        "if *only height* is provided, suggested width is relative to aspect "+\
        "ratio that would be suggested if neither provided (v1)"

    # nested option --------
    vis_nested = cow.patch(g0,cow.patch(g1,g2)+\
                        cow.layout(ncol=1, rel_heights = [1,2])) +\
        cow.layout(nrow=1)

    default_w_n, default_h_n = vis_nested._default_size(None,None)
    static_aspect_ratio_n = default_h_n / default_w_n

    # provide width ----
    out_w, out_h = vis_nested._default_size(height=None,width=height_or_width)
    assert np.allclose(out_w, height_or_width) and \
        np.allclose(out_h, height_or_width * static_aspect_ratio_n), \
        "if *only width* is provided, suggested height is relative to aspect "+\
        "ratio that would be suggested if neither provided (v1)"

    # provide height ----
    out_w, out_h = vis_nested._default_size(height=height_or_width,width=None)
    assert np.allclose(out_h, height_or_width) and \
        np.allclose(out_w, height_or_width / static_aspect_ratio_n), \
        "if *only height* is provided, suggested width is relative to aspect "+\
        "ratio that would be suggested if neither provided (v1)"

def test_patch__svg_get_sizes():
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
                   rel_heights = [4,1])

    # successful sizings ----
    sizes, logics = vis1._svg_get_sizes(width_pt = 20 * 72,
                                        height_pt = 20 * 72)

    requested_sizes = [(10,20), (10,16), (10,4)]

    assert np.all(logics), \
        "expected all plotnine objects to be able to be sized correctly "+\
        "in very large output (v1)"

    assert type(sizes) is list and \
        np.all([len(s) == 2 and type(s) is tuple for s in sizes]), \
        "expected structure of sizes list is incorrect (v1)"

    assert np.all([2/3 < (sizes[s_idx][0]/requested_sizes[s_idx][0]) < 1.5 and \
                    2/3 < (sizes[s_idx][1]/requested_sizes[s_idx][1]) < 1.5
                    for s_idx in [0,1,2]]), \
        "suggested sizing in sizes isn't too extreme relative to true "+\
        "requested sizes- this is just a sanity check, "+\
        "not a robust test (v1)"

    # failed sizings ------
    sizes_f, logics_f = vis1._svg_get_sizes(width_pt = 10 * 72,
                                        height_pt = 10 * 72)

    requested_sizes_f = [(5,10), (5,8), (5,2)] # final one should fail...

    assert not np.all(logics_f) and (logics_f == [True, True, False]), \
        "expected not all plotnine objects to be able to be sized correctly "+\
        "in small output (v1.1 - failed)"

    assert type(sizes_f) is list and \
        np.all([len(s) == 2 and type(s) is tuple for s in sizes_f]), \
        "expected structure of sizes list is incorrect (v1.1 - failed)"

    assert np.all([2/3 < (sizes_f[s_idx][0]/requested_sizes_f[s_idx][0]) < 1.5 and \
                    2/3 < (sizes_f[s_idx][1]/requested_sizes_f[s_idx][1]) < 1.5
                    for s_idx in [0,1]]), \
        "suggested sizing in sizes (that didn't fail) isn't too extreme "+\
        "relative to true "+\
        "requested sizes- this is just a sanity check, "+\
        "not a robust test (v1.1 - failed)"

    assert sizes_f[2][0] < 1 and sizes_f[2][1] < 1, \
        "expected failed sizing (due to being too small, to return a scaling" +\
        "below 1 (note the correction to scaling should be 1/suggested scaling))," +\
        "(v1.1 - failed)"

    # nested option --------
    vis_nested = cow.patch(g0,cow.patch(g1, g2)+\
                        cow.layout(ncol=1, rel_heights = [4,1])) +\
        cow.layout(nrow=1)

    # successful sizings ----
    sizes_n, logics_n = vis_nested._svg_get_sizes(width_pt = 20 * 72,
                                                  height_pt = 20 * 72)
    requested_sizes_n = [(10,20), (10,16), (10,4)]

    assert np.all(_flatten_nested_list(logics_n)), \
        "expected all plotnine objects to be able to be sized correctly "+\
        "in very large output (v2 - nested)"


    assert type(sizes_n) is list and len(sizes_n) == 2 and \
            type(sizes_n[0]) is tuple and type(sizes_n[1]) is list and \
            len(sizes_n[0]) == 2 and len(sizes_n[1]) == 2 and \
            np.all([len(s) == 2 and type(s) is tuple for s in sizes_n[1]]), \
        "expected structure of sizes list is incorrect (v2 - nested)"

    sizes_n_flattened = _flatten_nested_list(sizes_n)

    assert np.all([2/3 < (sizes_n_flattened[s_idx][0]/requested_sizes[s_idx][0]) < 1.5 and \
                    2/3 < (sizes_n_flattened[s_idx][1]/requested_sizes[s_idx][1]) < 1.5
                    for s_idx in [0,1,2]]), \
        "suggested sizing in sizes isn't too extreme relative to true "+\
        "requested sizes- this is just a sanity check, "+\
        "not a robust test (v2 - nested)"

    assert np.allclose(sizes_n_flattened, sizes), \
        "expected nested and non-nested suggested sizes to be equal (v1 vs v2)"

    # failed sizings ------
    sizes_f_n, logics_f_n = vis_nested._svg_get_sizes(width_pt = 10 * 72,
                                        height_pt = 10 * 72)

    requested_sizes_f = [(5,10), (5,8), (5,2)] # final one should fail ...

    logic_f_n_flat = _flatten_nested_list(logics_f_n)
    sizes_f_n_flat = _flatten_nested_list(sizes_f_n)

    assert not np.all(logic_f_n_flat) and \
            (logic_f_n_flat == [True, True, False]), \
        "expected not all plotnine objects to be able to be sized correctly "+\
        "in smaller output (v2.1 - nested, failed)"

    assert type(sizes_f_n) is list and len(sizes_f_n) == 2 and \
            type(sizes_f_n[0]) is tuple and type(sizes_f_n[1]) is list and \
            len(sizes_f_n[0]) == 2 and len(sizes_f_n[1]) == 2 and \
            np.all([len(s) == 2 and type(s) is tuple for s in sizes_f_n[1]]), \
        "expected structure of sizes list is incorrect (v2.1 - nested, failed)"

    assert np.all([2/3 < (sizes_f_n_flat[s_idx][0]/requested_sizes_f[s_idx][0]) < 1.5 and \
                    2/3 < (sizes_f_n_flat[s_idx][1]/requested_sizes_f[s_idx][1]) < 1.5
                    for s_idx in [0,1]]), \
        "suggested sizing in sizes (that didn't fail) isn't too extreme "+\
        "relative to true "+\
        "requested sizes- this is just a sanity check, "+\
        "not a robust test (v2.1 - nested, failed)"

    assert sizes_f_n_flat[2][0] < 1 and sizes_f_n_flat[2][1] < 1, \
        "expected failed sizing (due to being too small, to return a scaling" +\
        "below 1 (note the correction to scaling should be 1/suggested scaling))," +\
        "(v2.1 - nested, failed)"

    assert np.allclose(sizes_f_n_flat, sizes_f), \
        "expected nested and non-nested suggested sizes to be equal (v1.1 vs v2.1 - failed)"

@given(st.floats(min_value=.5, max_value=49),
       st.floats(min_value=.5, max_value=49),
       st.floats(min_value=.5, max_value=49),
       st.floats(min_value=.5, max_value=49),
       st.floats(min_value=.5, max_value=49),
       st.floats(min_value=.5, max_value=49))
def test_patch__process_sizes(w1,h1,w2,h2,w3,h3):
    # default patch (not needed)
    empty_patch = cow.patch()

    # not nested -------
    sizes = [(w1,h1),(w2,h2),(w3,h3)]

    # all true ---
    logics = [True, True, True]

    out_s = empty_patch._process_sizes(sizes = sizes, logics = logics)
    assert out_s == sizes, \
        "expected sizes to return if all logics true"

    # not all true ----
    logics_f = [True, True, False]
    out_s1 = empty_patch._process_sizes(sizes = sizes, logics = logics_f)

    assert np.allclose(out_s1, 1/np.min(sizes[2])), \
        "expected max_scaling should be the max of 1/width_scale and "+\
        "1/height_scale assoicated with failed plot(s) (v1.1 - 1 plot failed)"

    logics_f2 = [True, False, False]
    out_s2 = empty_patch._process_sizes(sizes = sizes, logics = logics_f2)

    assert np.allclose(out_s2, 1/np.min([w2,h2,w3,h3])), \
        "expected max_scaling should be the max of 1/width_scale and "+\
        "1/height_scale assoicated with failed plot(s) (v1.2 - 2 plot failed)"

    # nested ---------
    sizes_n = [(w1,h1),[(w2,h2),(w3,h3)]]

    # all true ---
    logics_n = [True, [True, True]]
    out_s_n = empty_patch._process_sizes(sizes = sizes_n, logics = logics_n)
    assert out_s_n == sizes_n, \
        "expected unflatted sizes to return if all logics true (v2 - nested)"

    # not all true ----
    logics_n_f = [True, [True, False]]
    out_s1 = empty_patch._process_sizes(sizes = sizes_n, logics = logics_n_f)

    assert np.allclose(out_s1, 1/np.min(sizes_n[1][1])), \
        "expected max_scaling should be the max of 1/width_scale and "+\
        "1/height_scale assoicated with failed plot(s) (v2.1 - 1 plot failed)"

    logics_f2 = [True, [False, False]]
    out_s2 = empty_patch._process_sizes(sizes = sizes, logics = logics_f2)

    assert np.allclose(out_s2, 1/np.min([w2,h2,w3,h3])), \
        "expected max_scaling should be the max of 1/width_scale and "+\
        "1/height_scale assoicated with failed plot(s) (v2.2 - 2 plot failed)"


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

def test_patch__repr__(monkeypatch,capsys):
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

def test_patch__str__(capsys):

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


# grammar -----------

def test_patch__and__(image_regression):
    # # creation of some some ggplot objects
    # g0 = p9.ggplot(p9_data.mpg) +\
    #     p9.geom_bar(p9.aes(x="hwy")) +\
    #     p9.labs(title = 'Plot 0')

    # g1 = p9.ggplot(p9_data.mpg) +\
    #     p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
    #     p9.labs(title = 'Plot 1')

    # g2 = p9.ggplot(p9_data.mpg) +\
    #     p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
    #     p9.labs(title = 'Plot 2')

    # g3 = p9.ggplot(p9_data.mpg[p9_data.mpg["class"].isin(["compact",
    #                                                      "suv",
    #                                                      "pickup"])]) +\
    #     p9.geom_histogram(p9.aes(x="hwy")) +\
    #     p9.facet_wrap("class")

    # g0p = cow.patch(g0)
    # g1p = cow.patch(g1)
    # g2p = cow.patch(g2)
    # g3p = cow.patch(g3)


    # g01 = g0p + g1p
    # g02 = g0p + g2p
    # g012 = g0p + g1p + g2p
    # g012_2 = g01 + g2p
    pass
