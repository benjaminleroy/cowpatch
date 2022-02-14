import cowpatch.utils

from hypothesis import given, strategies as st
import numpy as np

import pytest

@given(st.floats(min_value=0, max_value=1e10),
       st.floats(min_value=0, max_value=1e10))
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

