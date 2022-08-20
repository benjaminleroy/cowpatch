import cowpatch as cow
import plotnine as p9

import pytest
import copy
import numpy as np

def test__clean_element_text():
    """
    test that element_text stored inside is always a p9.themes.themeable (static)

    Both through initialization and addition
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

def test__add__():
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

def test__update_element_text_from_theme():
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

def test__update_element_text_from_theme2():
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


def test__get_full_element_text():
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

def test__get_full_element_text2():
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


def test__min_size():
    """
    test _min_size (static)

    This function only checks relative sizes reported from _min_size
    """
    pass


# printing ----------



