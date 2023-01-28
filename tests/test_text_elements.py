import cowpatch as cow
import plotnine as p9

import pytest
import copy
import numpy as np

from pytest_regressions import data_regression, image_regression
from hypothesis import given, strategies as st, settings
from datetime import timedelta

import io
import re
import matplotlib.pyplot as plt

import pdb

# text object ---------------------

def test_text__clean_element_text():
    """
    test that element_text stored inside is always a p9.themes.themeable (static)

    Both through initialization and addition

    tests __init__ and _clean_element_text
    """

    et_simple = p9.element_text(size = 12)


    # initialization
    mytitle2 = cow.text("title", element_text = et_simple)

    assert isinstance(mytitle2.element_text, p9.themes.themeable.text), \
        "internal saving of element_text is expected to be a themable.text "+\
        "(not a element_text) - through initalization"

    # addition
    mytitle = cow.text("title")

    mytitle_simple = mytitle + et_simple

    assert isinstance(mytitle_simple.element_text, p9.themes.themeable.text), \
        "internal saving of element_text is expected to be a themable.text "+\
        "(not a element_text) - updated with addition"

def test_text__add__():
    """
    test addition (static)

    checks
    1. theme cannot be added directly
    2. does not update self, but updates a new creation
    """
    et_simple = p9.element_text(size = 12)
    mytitle = cow.text("title", element_text = et_simple)

    # theme cannot be added
    with pytest.raises(Exception) as e_info:
            mytitle + p9.theme_bw()
            # cannot add theme to text object directly
            # would need to use internal _update_element_text_from_theme

    # addition doesn't update old object

    mytitle2 = mytitle + p9.element_text(size = 9)

    assert mytitle.element_text.properties.get("size") == 12 and \
        mytitle2.element_text.properties.get("size") == 9, \
        "expected that the __add__ updates and creates a new object and " +\
        "doesn't update the previous text object directly"

def test_text__update_element_text_from_theme():
    """
    test of _update_element_text_from_theme (static test)
    """
    mytitle = cow.text("title")
    mytitle2 = mytitle + p9.element_text(size = 13)
    mytitle_c = copy.deepcopy(mytitle)
    mytitle2_c = copy.deepcopy(mytitle2)

    # test error with key
    with pytest.raises(Exception) as e_info:
        mytitle._update_element_text_from_theme(p9.theme_bw(),
                                                key = "new_name")
    with pytest.raises(Exception) as e_info:
        mytitle2._update_element_text_from_theme(p9.theme_bw(),
                                                 key = "new_name")

    # test update
    mytheme = p9.theme_bw() + p9.theme(text = p9.element_text(size = 9))

    mytitle2._update_element_text_from_theme(mytheme, "text")
    mytitle._update_element_text_from_theme(mytheme, "text")

    assert mytitle.element_text.properties.get('size') == 9 and \
        mytitle_c.element_text is None,\
        "expected theme to update element_text of text object "+\
        "(with element_text originally being none)"


    assert mytitle2.element_text.properties.get('size') == 9 and \
        mytitle2_c.element_text.properties.get('size') == 13,\
        "expected theme to update element_text of text object "+\
        "(with element_text default)"

def test_text__update_element_text_from_theme2():
    """
    test _update_element_text_from_theme

    """

    my_ets = [p9.element_text(size = 8),
              p9.element_text(angle = 45, size = 12)]
    my_themes = [# just text size
                p9.theme(cow_tag = my_ets[0],
                              cow_caption = my_ets[0],
                              cow_text = my_ets[0],
                              cow_title = my_ets[0],
                              cow_subtitle = my_ets[0]),
                # new angle
                p9.theme(cow_tag = my_ets[1],
                              cow_caption = my_ets[1],
                              cow_text = my_ets[1],
                              cow_title = my_ets[1],
                              cow_subtitle = my_ets[1]),
                p9.theme_bw() # no update information for cow stuff
                ]


    _mytheme = my_themes[0]
    for _type in ["cow_tag", "cow_caption", "cow_text",
                    "cow_title", "cow_subtitle"]:
        # test if object already has element_text
        # test that override does the correct connection to _type

        a = cow.text("Fig 1", _type = _type)
        a = a + p9.element_text(angle = 100)
        a._update_element_text_from_theme(_mytheme)
        a_et_expected = dict(rotation = 100, size = 8, visible = True)

        assert a.element_text.properties == a_et_expected, \
            "error updating element_text from theme preserving other "+\
            "attributes (a, theme 0)"

        b = cow.text("Fig 1", _type = _type)
        b = b + p9.element_text(size = 8)
        b._update_element_text_from_theme(_mytheme)
        b_et_expected = dict(size = 8, visible = True)

        assert b.element_text.properties == b_et_expected, \
            "error updating element_text from theme preserving other "+\
            "attributes (b, theme 0)"

        c = cow.text("Fig 1", _type = _type)
        c._update_element_text_from_theme(_mytheme)
        c_et_expected = dict(size = 8, visible = True)

        assert c.element_text.properties == c_et_expected, \
            "error updating element_text from theme preserving other "+\
            "attributes (c, theme 0)"

    _mytheme = my_themes[1]
    for _type in ["cow_tag", "cow_caption", "cow_text",
                    "cow_title", "cow_subtitle"]:
        # test if object already has element_text
        # test that override does the correct connection to _type

        a = cow.text("Fig 1", _type = _type)
        a = a + p9.element_text(angle = 90)
        a._update_element_text_from_theme(_mytheme)
        a_et_expected = dict(rotation = 45, size = 12, visible = True)

        assert a.element_text.properties == a_et_expected, \
            "error updating element_text from theme preserving other "+\
            "attributes (a, theme 1)"

        b = cow.text("Fig 1", _type = _type)
        b = b + p9.element_text(size = 8)
        b._update_element_text_from_theme(_mytheme)
        b_et_expected = dict(rotation = 45, size = 12, visible = True)

        assert b.element_text.properties == b_et_expected, \
            "error updating element_text from theme preserving other "+\
            "attributes (b, theme 1)"

        c = cow.text("Fig 1", _type = _type)
        c._update_element_text_from_theme(_mytheme)
        c_et_expected = dict(rotation = 45, size = 12, visible = True)

        assert c.element_text.properties == c_et_expected, \
            "error updating element_text from theme preserving other "+\
            "attributes (c, theme 1)"


    _mytheme = my_themes[2]
    for _type in ["cow_tag", "cow_caption", "cow_text",
                    "cow_title", "cow_subtitle"]:
        # test if object already has element_text
        # test that override does the correct connection to _type

        a = cow.text("Fig 1", _type = _type)
        a = a + p9.element_text(angle = 90)

        with pytest.raises(Exception) as e_info:
            a._update_element_text_from_theme(_mytheme)
        assert e_info.typename == "ValueError" and \
                e_info.value.args[0] == "key parameter in "+\
                "_update_element_text_from_theme function call needs to "+\
                "be a key in the provided theme's themeables.", \
            "if theme doesn't have cow_... attributes cannot be used to update"+\
            "text object, so we expect an error (a, theme 2)"




        b = cow.text("Fig 1", _type = _type)
        b = b + p9.element_text(size = 8)

        with pytest.raises(Exception) as e_info:
            b._update_element_text_from_theme(_mytheme)
        assert e_info.typename == "ValueError" and \
                e_info.value.args[0] == "key parameter in "+\
                "_update_element_text_from_theme function call needs to "+\
                "be a key in the provided theme's themeables.", \
            "if theme doesn't have cow_... attributes cannot be used to update"+\
            "text object, so we expect an error (b, theme 2)"


        c = cow.text("Fig 1", _type = _type)
        with pytest.raises(Exception) as e_info:
            c._update_element_text_from_theme(_mytheme)
        assert e_info.typename == "ValueError" and \
                e_info.value.args[0] == "key parameter in "+\
                "_update_element_text_from_theme function call needs to "+\
                "be a key in the provided theme's themeables.", \
            "if theme doesn't have cow_... attributes cannot be used to update"+\
            "text object, so we expect an error (c, theme 2)"


def test_text__additional_rotation0(image_regression):
    """
    test text's _additional_rotation function

    ensure that 0 angle rotation returns the same object
    """
    # no angle change means that same object
    myt = cow.text(label="Portland",
                   element_text=p9.element_text(size=15,angle=15),
                   _type="cow_text")

    myt2 = myt._additional_rotation()

    assert myt2 == myt, \
        "default rotation of 0 should return the same text element"

    myt2_2 = myt._additional_rotation(angle=0)

    assert myt2_2 == myt, \
        "explicit rotation of 0 should return the same text element"

    # no element text pre-defined (this highlights the function shouldn't
    # be used outside internal functions

    myt_b = cow.text(label="Portland",
                   _type="cow_text")

    myt_b2 = myt_b._additional_rotation()

    assert myt_b2 == myt_b, \
        ("default rotation of 0 should return the same text element, " +
        "initial has non element_text defined")

    myt_b2_2 = myt_b._additional_rotation(angle=0)

    assert myt_b2_2 == myt_b, \
        ("explicit rotation of 0 should return the same text element, " +
        "initial has non element_text defined")

    # image regression for partially rotated object
    with io.BytesIO() as fid2:
        myt.save(filename=fid2, _format = "png")
        image_regression.check(fid2.getvalue(), diff_threshold=.1)

def test_text__additional_rotation(image_regression):
    """
    test text's _additional_rotation function

    ensures correct addition of rotation without overwriting other
    parmeters
    """
    # additional parameters not lost
    myt = cow.text(label="Portland",
               element_text=p9.element_text(size=15,angle=15,color="blue"),
               _type="cow_text")

    myt2 = myt._additional_rotation(angle = 20)

    old = myt.element_text.theme_element.properties
    new_expected = old.copy()
    new_expected["rotation"] = 35

    assert myt2.element_text.theme_element.properties == new_expected, \
        ("_additional_rotation should only impact the angle, not other "+
        "element attributes")

    # beyond 360 only does a max of 360 degrees
    myt2_b = myt._additional_rotation(angle = 350)

    assert np.allclose(myt2_b.element_text.theme_element.properties["rotation"], 5), \
        "_additional_rotation should keep angle betwen [0, 360)"

    myt2_b2 = myt._additional_rotation(angle = 345)

    assert (myt2_b2.element_text.theme_element.properties["rotation"] < 360) and \
        (np.allclose(myt2_b2.element_text.theme_element.properties["rotation"], 0) or
         np.allclose(myt2_b2.element_text.theme_element.properties["rotation"], 360)), \
        "_additional_rotation should keep angle betwen [0, 360), 360 strict"


    # image regression for partially rotated object
    with io.BytesIO() as fid2:
        myt2.save(filename=fid2, _format = "png")
        image_regression.check(fid2.getvalue(), diff_threshold=.1)




def test_text__get_full_element_text():
    """
    test _get_full_element_text (static test - using _type text not cow_text, etc.)
    """
    mytitle = cow.text("title")
    mytitle._define_type("text")

    et_full_base = mytitle._get_full_element_text()

    mytitle_size9 = mytitle + p9.element_text(size = 9)
    et_full_size9 = mytitle_size9._get_full_element_text()

    mytitle_size13 = mytitle + p9.element_text(size = 13)
    et_full_size13 = mytitle_size13._get_full_element_text()

    assert et_full_size9.properties.get("size") == 9 and \
        et_full_size13.properties.get("size") == 13, \
        "expected specified element_text attributes to be perserved (size)"

    for key in et_full_base.properties:
        if key != "size":
            assert (et_full_base.properties.get(key) == \
                et_full_size9.properties.get(key)) and \
                (et_full_base.properties.get(key) == \
                et_full_size13.properties.get(key)), \
                (("expected all properties but key=size (key = %s) to match "+\
                 "if all inherits properties from global theme") % key)

def test_text__get_full_element_text2():
    """
    test _get_full_element_text, static

    tests that nothing is override but additional attributes are provided
    relative to the _type parameter and default theme structure

    """
    for _type in ["cow_tag", "cow_caption", "cow_text",
                "cow_title", "cow_subtitle"]:
        # test if object already has element_text
        # test that override does the correct connection to _type

        a = cow.text("Fig 1", _type = _type)
        a = a + p9.element_text(angle = 90)

        b = cow.text("Fig 1", _type = _type)
        b = b + p9.element_text(size = 8)

        c = cow.text("Fig 1", _type = _type)

        a_et = a._get_full_element_text()
        a_et_properties_expected = \
            {'visible': True,
            'rotation': 90,
            'size': cow.rcParams[_type].properties["size"]}

        b_et = b._get_full_element_text()
        b_et_properties_expected = \
            {'visible': True,
            'size': 8}

        c_et = c._get_full_element_text()
        c_et_properties_expected = cow.rcParams[_type].properties

        for key, v_expected in a_et_properties_expected.items():
            assert a_et.properties[key] == v_expected, \
                "text element with rotation should preserve rotation " +\
                "but update size relative to default (_type :%s, key: %s)" % (_type, key)

        for key, v_expected in b_et_properties_expected.items():
            assert b_et.properties[key] == v_expected, \
                "text element with size should not be updated with base "+\
                "size information (_type :%s, key: %s)" % (_type, key)

        for key, v_expected in c_et_properties_expected.items():
            assert c_et.properties[key] == v_expected, \
                "text object without element_text attribute should fully update "+\
                "with default size information (_type :%s, key: %s)" % (_type, key)


def test_text__min_size():
    """
    test _min_size (static)

    This function only checks relative sizes reported from _min_size
    """

    for _type in ["cow_tag", "cow_caption", "cow_text",
                "cow_title", "cow_subtitle"]:

        # base option
        a = cow.text("Fig 1", _type = _type)

        out = a._min_size()
        out_in = a._min_size(to_inches=True)

        assert np.all([np.allclose(cow.utils.to_inches(out[i], "pt"), out_in[i])
                      for i in [0,1]]), \
            ("error in _min_size's application of `to_inches` parameter "+
             "type: %s, test 1" % _type)

        a_long = cow.text("Fig 1 Fig 1", _type = _type)
        out_long = a_long._min_size()

        assert (3 * out[0]> out_long[0] > 2 * out[0]) and \
                np.allclose(out_long[1], out[1]), \
            ("if text size 2x+ in length, relative sizes should match, " +
             "type: %s, text 1" % _type)

        a_tall = cow.text("Fig 1\nFig 1", _type = _type)
        out_tall = a_tall._min_size()

        assert (2.5 * out[1] > out_tall[1] > 1.5 * out[1]) and \
                np.allclose(out_tall[0], out[0]), \
            ("if text size ~2x in height, relative sizes should match, " +
             "type: %s, text 1" % _type)

        # rotated text 90 degrees
        a2 = a + p9.element_text(angle = 90)

        out2 = a2._min_size()
        out2_in = a2._min_size(to_inches=True)

        assert np.all([np.allclose(cow.utils.to_inches(out2[i], "pt"), out2_in[i])
                      for i in [0,1]]), \
            ("error in _min_size's application of `to_inches` parameter "+
             "type: %s, test 2" % _type)

        assert np.allclose(out, out2[::-1]), \
            ("expected a rotation of 90 degrees to text to directly flip " +
             "required size, type : %s, test 1+2" % _type)


        a2_long = cow.text("Fig 1 Fig 1", _type = _type) +\
            p9.element_text(angle = 90)
        out2_long = a2_long._min_size()

        assert (3 * out2[1]> out2_long[1] > 2 * out2[1]) and \
                np.allclose(out2_long[0], out2[0]), \
            ("if text size 2x+ in length (and rotated 90 degrees), " +
             "relative sizes should match, type: %s, text 2" % _type)

        a2_tall = cow.text("Fig 1\nFig 1", _type = _type) +\
            p9.element_text(angle = 90)
        out2_tall = a2_tall._min_size()

        assert (2.5 * out2[0] > out2_tall[0] > 1.5 * out2[0]) and \
                np.allclose(out2_tall[1], out2[1]), \
            ("if text size ~2x in height (and rotated 90 degrees), "+
             "relative sizes should match, type: %s, text 2" % _type)

def test_text__min_size2(data_regression):
    """
    _min_size data regression test on sizing for different base types

    Notes
    -----
    the usage of data_regression requires ensuring the saved
    dictionary is "yaml"-ifable (which is why we do things like
    converting the values to strings).
    """
    static_min_size_data = {}

    for _type in ["cow_tag", "cow_caption", "cow_text",
                "cow_title", "cow_subtitle"]:

        a = cow.text("Fig 1", _type = _type)
        out = a._min_size()
        inner_dict_list = [str(x) for x in out]
        static_min_size_data[_type] = inner_dict_list

    data_regression.check(static_min_size_data)


@pytest.mark.parametrize("_type", ["cow_tag", "cow_caption", "cow_text",
                "cow_title", "cow_subtitle"])
def test_text__base_text_image(image_regression, _type):
    """
    tests for _base_text_image (regression for image,
        and bbox versus _min_size check)
    """
    # base option
    a = cow.text("Fig 1", _type = _type)
    fig, bbox = a._base_text_image()

    # matchin with min_size
    ms_out = a._min_size()
    assert (bbox.width > ms_out[0] > .5 * bbox.width) and \
            (bbox.height > ms_out[1] > .5 * bbox.height), \
        ("expect that bbox is slightly bigger than min_sizing, " +
         "type = %s, test 1" % _type)

    with io.BytesIO() as fid2:
        fig.savefig(fname=fid2, format = "png")
        image_regression.check(fid2.getvalue(), diff_threshold=.1)


@pytest.mark.parametrize("_type", ["cow_tag", "cow_caption", "cow_text",
                "cow_title", "cow_subtitle"])
def test_text__base_text_image2(image_regression, _type):
    """
    tests for _base_text_image (regression for image,
        and bbox versus _min_size check)

    test rotated 90 degrees
    """
    # rotated option
    a = cow.text("Fig 1", _type = _type) +\
        p9.element_text(angle = 90)
    fig, bbox = a._base_text_image()

    # matchin with min_size
    ms_out = a._min_size()
    assert (bbox.width > ms_out[0] > .5 * bbox.width) and \
            (bbox.height > ms_out[1] > .5 * bbox.height), \
        ("expect that bbox is slightly bigger than min_sizing, " +
         "type = %s, test 1" % _type)

    with io.BytesIO() as fid2:
        fig.savefig(fname=fid2, format = "png")
        image_regression.check(fid2.getvalue(), diff_threshold=.1)

@pytest.mark.parametrize("_type", ["cow_tag", "cow_caption", "cow_text",
                "cow_title", "cow_subtitle"])
@given(st.floats(min_value=.5, max_value=49),
    st.floats(min_value=.5, max_value=49))
@settings(max_examples=4, deadline=timedelta(milliseconds=1000))
def test_text__default_size(_type, height, width):
    """
    test for _default_size function
    """
    # base option
    a = cow.text("Fig 1", _type = _type)
    ms_out = a._min_size(to_inches = True)

    assert np.allclose(a._default_size(), ms_out), \
        ("if width & height input are none, expect to return " +
         "_min_size(to_inches=True), type = %s, test 1" % _type)

    ds_out = a._default_size(width=width)

    assert np.allclose(ds_out, (width, ms_out[1])), \
        ("if width is non-none, height none, expected return " +
         "(width, min_size(to_inches=True)[1]), type = %s, test 1" % _type)

    ds_out2 = a._default_size(height=height)

    assert np.allclose(ds_out2, (ms_out[0], height)), \
        ("if height is non-none, width none, expected return " +
         "(min_size(to_inches=True)[0], height), type = %s, test 1" % _type)

    ds_out3 = a._default_size(height=height, width=width)

    assert np.allclose(ds_out3, (width, height)), \
        ("if height is non-none, width non-none, expected return " +
         "(width, height), type = %s, test 1" % _type)


    # long option
    a_long = cow.text("Fig 1 Fig 1", _type = _type)
    ms_out_long = a_long._min_size(to_inches = True)

    assert np.allclose(a_long._default_size(), ms_out_long), \
        ("if width & height input are none, expect to return " +
         "_min_size(to_inches=True), type = %s, test 2" % _type)

    assert np.allclose(a_long._default_size(), ms_out_long), \
        ("if width & height input are none, expect to return " +
         "_min_size(to_inches=True), type = %s, test 2" % _type)

    ds_out_long = a_long._default_size(width=width)

    assert np.allclose(ds_out_long, (width, ms_out_long[1])), \
        ("if width is non-none, height none, expected return " +
         "(width, min_size(to_inches=True)[1]), type = %s, test 2" % _type)

    ds_out2_long = a_long._default_size(height=height)

    assert np.allclose(ds_out2_long, (ms_out_long[0], height)), \
        ("if height is non-none, width none, expected return " +
         "(min_size(to_inches=True)[0], height), type = %s, test 2" % _type)

    ds_out3_long = a_long._default_size(height=height, width=width)

    assert np.allclose(ds_out3_long, (width, height)), \
        ("if height is non-none, width non-none, expected return " +
         "(width, height), type = %s, test 2" % _type)




    # 2x height option
    a_tall = cow.text("Fig 1\nFig 1", _type = _type)
    ms_out_tall = a_tall._min_size(to_inches = True)

    assert np.allclose(a_tall._default_size(), ms_out_tall), \
        ("if width & height input are none, expect to return " +
         "_min_size(to_inches=True), type = %s, test 3" % _type)

    ds_out_tall = a_tall._default_size(width=width)

    assert np.allclose(ds_out_tall, (width, ms_out_tall[1])), \
        ("if width is non-none, height none, expected return " +
         "(width, min_size(to_inches=True)[1]), type = %s, test 3" % _type)

    ds_out2_tall = a_tall._default_size(height=height)

    assert np.allclose(ds_out2_tall, (ms_out_tall[0], height)), \
        ("if height is non-none, width none, expected return " +
         "(min_size(to_inches=True)[0], height), type = %s, test 3" % _type)

    ds_out3_tall = a_tall._default_size(height=height, width=width)

    assert np.allclose(ds_out3_tall, (width, height)), \
        ("if height is non-none, width non-none, expected return " +
         "(width, height), type = %s, test 3" % _type)


def test_text__svg():
    raise ValueError("Not Tested")


def test_text_save():
    raise ValueError("Not Tested")


def test_text_show():
    raise ValueError("Not Tested")


# printing -------------
@pytest.mark.parametrize("_type", ["cow_tag", "cow_caption", "cow_text",
                "cow_title", "cow_subtitle"])
def test_text__str__(monkeypatch, capsys, _type):
    """
    test text.__str__, static

    print(.) also creates the figure
    """
    monkeypatch.setattr(plt, "show", lambda:None)

    a = cow.text("Fig 1", _type = _type)

    print(a)
    captured = capsys.readouterr()

    re_cap = re.search("<text \(-{0,1}[0-9]+\)>\\n", captured.out)
    assert re_cap is not None and \
        re_cap.start() == 0 and re_cap.end() == len(captured.out),\
        "expected __str__ expression for text to be of <text (num)> format"


@pytest.mark.parametrize("_type", ["cow_tag", "cow_caption", "cow_text",
                "cow_title", "cow_subtitle"])
def test_text__repr__(monkeypatch, capsys, _type):
    """
    test text.__repr__, static
    """
    monkeypatch.setattr(plt, "show", lambda:None)

    a = cow.text("Fig 1", _type = _type)

    print(repr(a))
    captured = capsys.readouterr()
    lines = re.split("\\n", captured.out)

    re_cap = re.search("<text \(-{0,1}[0-9]+\)>\\n", captured.out)
    assert re_cap is not None and \
        re_cap.start() == 0 and re_cap.end() == (len(lines[0]) + 1),\
        "expected __repr__ first line expression for text to be "+\
        "of <text (num)> format"


    assert ((lines[1] == "label:") and
        (lines[2] == "  |" + a.label) and
        (lines[3] == "element_text:") and
        (lines[5] == "_type:") and
        (lines[6] == "  |\"%s\"" % _type)), \
        "expected overall __repr__ expression to follow a specific format"


