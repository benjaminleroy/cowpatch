import cowpatch.utils

from hypothesis import given, strategies as st
import numpy as np

import pytest

@given(st.floats(min_value=0.1, max_value=1e10),
       st.floats(min_value=0.1, max_value=1e10))
def test__transform_size_to_pt(w,h):
    """
    test _transform_size,

    upper constraints w.r.t. scientific notation in string
    """

    # PT > PT
    input_string_pt = (str(w)+"pt", str(h)+"pt")
    out_pt = cowpatch.utils._transform_size_to_pt(input_string_pt)
    assert np.allclose(out_pt, (w,h)), \
        "px transforms should return same values back"

    # IN > PT
    input_string_in = (str(w)+"in", str(h)+"in")
    out_in = cowpatch.utils._transform_size_to_pt(input_string_in)
    assert np.allclose(out_in, (w*72,h*72)), \
        "inches*72 = pt, error"
        #see https://www.asknumbers.com/inches-to-points.aspx

    # PX > PT
    input_string_in = (str(w)+"px", str(h)+"px")
    out_in = cowpatch.utils._transform_size_to_pt(input_string_in)
    assert np.allclose(out_in, (w*3/4,h*3/4)), \
        "px*3/4 = pt, error"
        #see https://pixelsconverter.com/px-to-pt

@given(st.integers(min_value=1, max_value=1e5),
       st.floats(min_value = -1e10,
                max_value = 1e10),
       st.floats(min_value = -1e10,
                max_value = 1e10) )
def test_val_range(size, _min, _max):
    _temp = 0
    if _min > _max:
        _temp = _min
        _min = _max
        _max = _temp

    num_vec = np.random.uniform(size = size, low = _min, high = _max)

    i_range = cowpatch.utils.val_range(num_vec)
    assert i_range[0] <= i_range[1], \
        "range should be arranged increasingly"

    assert np.all(i_range[0] <= num_vec) and \
        np.all(i_range[1] >= num_vec), \
        "range values should bound the values that define it"

    assert np.any(i_range[0] == num_vec) and \
        np.any(i_range[1] == num_vec), \
        "range values should be included in values that define it"

@given(st.floats(min_value = -1e10,max_value = 1e10))
def test_to_pt(val):
    unit = "pt"#, "px", "in", "cm", "mm"]
    out = cowpatch.utils.to_pt(val, unit, dpi = 96)
    assert out == val, \
        "pt transform should remain the same (to_pt)"

    unit = "px"
    out = cowpatch.utils.to_pt(val, unit, dpi = 96)
    assert np.allclose(out, val*3/4), \
        "px*3/4 = pt, error (to_pt)"

    unit = "in"
    out = cowpatch.utils.to_pt(val, unit, dpi = 96)
    assert np.allclose(out, val*72), \
        "in*72 = pt, error (to_pt)"

    unit = "cm"
    out = cowpatch.utils.to_pt(val, unit, dpi = 96)
    assert np.allclose(out, val*72/2.54), \
        "cm*1/2.54*72 = pt, error (to_pt)"

    unit = "mm"
    out = cowpatch.utils.to_pt(val, unit, dpi = 96)
    assert np.allclose(out, val*72/25.4), \
        "mm*1/25.4*72 = pt, error (to_pt)"

@given(st.floats(min_value = -1e10,max_value = 1e10))
def test_from_pt(val):
    unit = "pt"#, "px", "in", "cm", "mm"]
    out = cowpatch.utils.from_pt(val, unit, dpi = 96)
    assert out == val, \
        "pt transform should remain the same (from_pt)"

    unit = "px"
    out = cowpatch.utils.from_pt(val, unit, dpi = 96)
    assert np.allclose(val, out*3/4), \
        "px*3/4 = pt, error (from_pt)"

    unit = "in"
    out = cowpatch.utils.from_pt(val, unit, dpi = 96)
    assert np.allclose(val, out*72), \
        "in*72 = pt, error (from_pt)"

    unit = "cm"
    out = cowpatch.utils.from_pt(val, unit, dpi = 96)
    assert np.allclose(val, out*72/2.54), \
        "cm*1/2.54*72 = pt, error (from_pt)"

    unit = "mm"
    out = cowpatch.utils.from_pt(val, unit, dpi = 96)
    assert np.allclose(val, out*72/25.4), \
        "mm*1/25.4*72 = pt, error (from_pt)"

@given(st.floats(min_value = -1e10,
                max_value = 1e10),
       st.text(min_size=2, max_size=2))
def test_to_pt_bad(val, bad_unit):
    if bad_unit not in ["pt", "px", "in", "cm", "mm"]:
        with pytest.raises(Exception) as e_info:
            cowpatch.utils.to_pt(val, bad_unit)

@given(st.floats(min_value = -1e10,
                max_value = 1e10),
       st.text(min_size=2, max_size=2))
def test_from_pt_bad(val, bad_unit):
    if bad_unit not in ["pt", "px", "in", "cm", "mm"]:
        with pytest.raises(Exception) as e_info:
            cowpatch.utils.from_pt(val, bad_unit)

@given(st.floats(min_value = -1e10,max_value = 1e10),
       st.sampled_from(["pt", "px", "in", "cm", "mm"]))
def test_to_inches(val, units):
    val_rev = cowpatch.utils.to_inches(val, units)
    assert np.allclose(cowpatch.utils.from_inches(val_rev,units),
                       val), \
        "converting back and forth (to_inches first) should perserve transform"

    val_rev = cowpatch.utils.from_inches(val, units)
    assert np.allclose(cowpatch.utils.to_inches(val_rev,units),
                       val), \
        "converting back and forth (from _inches first) should perserve transform"


@given(st.floats(min_value = .001, max_value=1e6),
       st.floats(min_value = .001, max_value=1e6),
       st.floats(min_value = .001, max_value=1e6),
       st.floats(min_value = .001, max_value=1e6))
def test__proposed_scaling_both(cx,cy,dx,dy):
    scalings = cowpatch.utils._proposed_scaling_both((cx,cy),(dx,dy))

    assert np.allclose([cx*scalings[0], cy*scalings[1]],
                       [dx,dy]), \
        "expected scaling to correctly scale current values to desired "+\
        "values (in x and y directions individually)"

def test__flatten_nested_list():
    x = [True, [True, False], True, [True]]
    x_flat = cowpatch.utils._flatten_nested_list(x)
    assert x_flat == [True, True, False, True, True], \
        "_flatten_nested_list failed to flatten correctly (v1 - single nesting)"

    x2 = [True, [True, False], True, [True], False, [False, [False, True]]]
    x2_flat = cowpatch.utils._flatten_nested_list(x2)
    assert x2_flat == [True, True, False, True, True, False, False, False, True], \
        "_flatten_nested_list failed to flatten correctly (v2 - double nesting)"

    x3 = [True, False, True]
    x3_flat = cowpatch.utils._flatten_nested_list(x3)
    assert x3_flat == x3, \
        "_flatten_nested_list failed to flatten correctly (v3 - no nesting)"


@given(st.integers(min_value=1, max_value=100000),
       st.floats(min_value = 1.001, max_value=5),
       st.floats(min_value = .2, max_value=.9),
       st.floats(min_value = 5, max_value=25),
       st.floats(min_value = 5, max_value=25))
def test__overall_scale_recommendation_patch_NoAnnotation(seed,
                                                          upscale,
                                                          lesser_upscale,
                                                          width, height):
    """
    basic test _overall_scale_recommendation_patch, without annotation
    """
    np.random.seed(seed)
    size_multiplier = list(np.array([1, upscale, 1,
                        (upscale * lesser_upscale + (1-lesser_upscale))
                        ])[np.random.choice(4,4, replace=False)])
    text_inner_size = (0,0)
    text_extra_size = (0,0)
    original_overall_size = (width, height)

    out = cowpatch.utils._overall_scale_recommendation_patch(size_multiplier,
                                                       text_inner_size,
                                                       text_extra_size,
                                                       original_overall_size)

    assert np.allclose(out[0],
                       np.array([width,height])*upscale) and \
        np.allclose(out[1], upscale) and \
        np.allclose(np.max(size_multiplier), upscale), \
        "overall upscaling matches needs of largest upscale grob"


@given(st.integers(min_value=1, max_value=100000),
       st.floats(min_value = 1.001, max_value=5),
       st.floats(min_value = .2, max_value=.9),
       st.floats(min_value = 5, max_value=25),
       st.floats(min_value = 5, max_value=25),

       st.floats(min_value = .1, max_value=10),
       st.floats(min_value = .1, max_value=10),
       st.floats(min_value = .1, max_value=2),
       st.floats(min_value = .1, max_value=2))
def test__overall_scale_recommendation_patch_Annotation(seed,
                                                          upscale,
                                                          lesser_upscale,
                                                          width, height,
                                                          text_inner_w,
                                                          text_inner_h,
                                                          text_extra_w,
                                                          text_extra_h):
    """
    basic test _overall_scale_recommendation_patch, with annotation

    solid checks with/without extra_size, with/without inner_size
    not really any checks on both non-zero
    """
    np.random.seed(seed)
    size_multiplier = list(np.array([1, upscale, 1,
                        (upscale * lesser_upscale + (1-lesser_upscale))
                        ])[np.random.choice(4,4, replace=False)])
    text_inner_size = (text_inner_w,text_inner_h)
    text_extra_size = (text_extra_w,text_extra_h)
    original_overall_size = (width, height)

    out_no_ann = cowpatch.utils._overall_scale_recommendation_patch(size_multiplier,
                                                       (0,0),
                                                       (0,0),
                                                       original_overall_size)


    # both non-zero ---------------

    out = cowpatch.utils._overall_scale_recommendation_patch(size_multiplier,
                                                       text_inner_size,
                                                       text_extra_size,
                                                       original_overall_size)


    # no extra size ------------------

    out_no_extra_size = cowpatch.utils._overall_scale_recommendation_patch(size_multiplier,
                                                       text_inner_size,
                                                       (0,0),
                                                       original_overall_size)

    # text_inner_size < original_overall_size, and text_extra_size = (0,0))
    if (text_inner_size[0] < width) and (text_inner_size[1] < height):
        assert np.allclose(out_no_extra_size[0], np.array([width,height])*upscale) and \
            np.allclose(out_no_extra_size[1], upscale) and \
            np.allclose(np.max(size_multiplier), upscale), \
            ("overall upscaling matches needs of largest upscale grob " +
             "(text_inner_size < original_overall_size, and " +
             "text_extra_size = (0,0))")
    elif (text_inner_size[0] > out_no_ann[0][0]) or \
        (text_inner_size[1] > out_no_ann[0][1]):
        # text inner size is larger than normal upscale required
        assert out_no_extra_size[1] > np.max(size_multiplier), \
            ("if text_inner_size is larger than the base scale-up sizing " +
             "the scaling will be larger then for just the default")

        if text_inner_size[0] > out_no_ann[0][0]:
            assert np.allclose(text_inner_size[0], out_no_extra_size[0][0]), \
                ("if text_inner_size is larger than the base scale-up sizing " +
                "outputted sizing should be relative to it (width)")

        if text_inner_size[1] > out_no_ann[0][1]:
            assert np.allclose(text_inner_size[1], out_no_extra_size[0][1]), \
                ("if text_inner_size is larger than the base scale-up sizing " +
                "outputted sizing should be relative to it (height)")

    # no inner size ------------------

    # TODO: see comments
    # Comment: TODO: look at the equation on overleaf (page 2 & 3) and
    # inspect the ipad notes on why we thought it was $<$ not $>$ for the
    # logic.)

    out_no_inner_size = cowpatch.utils._overall_scale_recommendation_patch(size_multiplier,
                                                       (0,0),
                                                       text_extra_size,
                                                       original_overall_size)

    # minimum size of height and width
    expected_size_out_no_inner_size_no_ratio = \
        (np.array(original_overall_size) - np.array(text_extra_size)) *\
        np.max(size_multiplier) + np.array(text_extra_size)

    scaling = np.max([expected_size_out_no_inner_size_no_ratio[i]/original_overall_size[i]
                        for i in [0,1]])

    # calculation to get height and width that obey min sizing and keep height/width ratio
    # TODO: the idea that you can use an argmin isn't correct - this is relative ratio even now.
    min_val = np.argmin(expected_size_out_no_inner_size_no_ratio)
    expected_size_out_no_inner_size =\
        expected_size_out_no_inner_size_no_ratio[min_val] *\
            [np.array([1, height/width]), np.array([width,height,1])][min_val]


    assert np.allclose(expected_size_out_no_inner_size, out_no_inner_size[0]) and \
        np.allclose(scaling,  out_no_inner_size[1]), \
        ("expected (with inner_size = 0), that extra size impacted both the "+
        "initial scaling estimate and the final estimated size")



