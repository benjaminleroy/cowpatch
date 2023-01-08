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

def test_patch__size_dive():
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


    sug_width, sug_height, max_depth = \
        vis1._size_dive()

    assert np.allclose(sug_width,
                        (2 * # 1/ rel width of smallest width of images
                         cow.rcParams["base_height"] *
                         cow.rcParams["base_aspect_ratio"])), \
        "suggested width incorrectly sizes the smallest width of the images (v1)"

    assert np.allclose(sug_height,
                       (3 * # 1/ rel width of smallest width of images
                        cow.rcParams["base_height"])), \
        "suggested height incorrectly sizes the smallest height of the images (v1)"

    assert max_depth == 1, \
        "expected depth for basic cow.patch (of depth 1) is incorrect (v1)"


    # of note: the internal uses "pt", but they're actually defined relatively...
    image_rel_widths, image_rel_heights, depths = \
        vis1._size_dive(parents_areas=[cow.area(width=1/6,
                                            height=1/6,
                                            x_left=0,
                                            y_top=0,
                                            _type="pt")])

    assert np.allclose(image_rel_widths, [.5*1/6]*3), \
        "expected widths if input into a smaller image incorrect "+\
        "(v1.1, rel width to top 1/6)"

    assert np.allclose(image_rel_heights, [1/6, 1/6*1/3, 1/6*2/3]), \
        "expected heights if input into a smaller image incorrect "+\
        "(v1.1, rel heights to top 1/6)"

    assert np.allclose(depths, [1+1]*3), \
        "expected depths in basic cow.patch (all of depth 1) input into a "+\
        "1 level deep smaller image is incorrect (v1.1)"


    image_rel_widths2, image_rel_heights2, depths2 = \
        vis1._size_dive(parents_areas=[cow.area(width=1/3,
                                            height=1/2,
                                            x_left=0,
                                            y_top=0,
                                            _type="pt"),
                                       cow.area(width=1/2,
                                                height=1/3,
                                                x_left=1/2,
                                                y_top=0,
                                                _type="pt")])

    assert np.allclose(image_rel_widths2, [.5*1/6]*3), \
        "expected widths if input into a smaller image incorrect "+\
        "(v1.2, rel width to top 1/6)"

    assert np.allclose(image_rel_heights2, [1/6, 1/6*1/3, 1/6*2/3]), \
        "expected heights if input into a smaller image incorrect "+\
        "(v1.2, rel heights to top 1/6)"

    assert np.allclose(depths2, [1+2]*3), \
        "expected depths in basic cow.patch (all of depth 1) input into a "+\
        "2 levels deep smaller image is incorrect (v1.2)"



    # nested option --------
    vis_nested = cow.patch(g0,cow.patch(g1,g2)+\
                        cow.layout(ncol=1, rel_heights = [1,2])) +\
        cow.layout(nrow=1)


    sug_width_n, sug_height_n, max_depth_n = \
        vis_nested._size_dive()

    assert np.allclose(sug_width_n,
                        (2 * # 1/ rel width of smallest width of images
                         cow.rcParams["base_height"] *
                         cow.rcParams["base_aspect_ratio"])), \
        "suggested width incorrectly sizes the smallest width of the images "+\
        "(v2 - nested)"

    assert np.allclose(sug_height_n,
                       (3 * # 1/ rel width of smallest width of images
                        cow.rcParams["base_height"])), \
        "suggested height incorrectly sizes the smallest height of the images "+\
        "(v2 - nested)"

    assert max_depth_n == 2, \
        "expected depth for nested cow.patch (of depth 1) is incorrect "+\
        "(v2 - nested)"



    # of note: the internal uses "pt", but they're actually defined relatively...
    image_rel_widths_n, image_rel_heights_n, depths_n = \
        vis_nested._size_dive(parents_areas=[cow.area(width=1/6,
                                            height=1/6,
                                            x_left=0,
                                            y_top=0,
                                            _type="pt")])

    assert np.allclose(image_rel_widths_n, [.5*1/6]*3), \
        "expected widths if input into a smaller image incorrect "+\
        "(v2.1 - nested, rel width to top 1/6)"

    assert np.allclose(image_rel_heights_n, [1/6, 1/6*1/3, 1/6*2/3]), \
        "expected heights if input into a smaller image incorrect "+\
        "(v2.1 - nested, rel heights to top 1/6)"

    assert np.allclose(depths_n, list(np.array([1,2,2])+1)), \
        "expected depths in nested cow.patch (all of depth 1) input into a "+\
        "1 level deep smaller image is incorrect (v2.1 - nested)"


    image_rel_widths2_n, image_rel_heights2_n, depths2_n = \
        vis_nested._size_dive(parents_areas=[cow.area(width=1/3,
                                            height=1/2,
                                            x_left=0,
                                            y_top=0,
                                            _type="pt"),
                                       cow.area(width=1/2,
                                                height=1/3,
                                                x_left=1/2,
                                                y_top=0,
                                                _type="pt")])

    assert np.allclose(image_rel_widths2_n, [.5*1/6]*3), \
        "expected widths if input into a smaller image incorrect "+\
        "(v2.2 - nested, rel width to top 1/6)"

    assert np.allclose(image_rel_heights2_n, [1/6, 1/6*1/3, 1/6*2/3]), \
        "expected heights if input into a smaller image incorrect "+\
        "(v2.2 - nested, rel heights to top 1/6)"

    assert np.allclose(depths2_n, list(np.array([1,2,2])+2)), \
        "expected depths in nested cow.patch (all of depth 1) input into a "+\
        "1 levels deep smaller image is incorrect (v2.2 - nested)"

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

@given(st.floats(min_value=.5, max_value=49),
       st.floats(min_value=.5, max_value=49))
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
    """
    test patch .__repr__, static

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



