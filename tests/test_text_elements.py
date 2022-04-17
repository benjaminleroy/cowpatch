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

def test__get_full_element_text():
    """
    test _get_full_element_text (static test)
    """
    mytitle = cow.text("title")

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

def test__min_size():
    """
    test _min_size (static)

    This function only checks relative sizes reported from _min_size
    """





