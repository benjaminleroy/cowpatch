import cowpatch as cow
from cowpatch.svg_utils import _save_svg_wrapper, _add_to_base_image
from cowpatch.utils import to_inches, inherits
import numpy as np
import pandas as pd
import copy
import plotnine as p9
import plotnine.data as p9_data

import pytest
from hypothesis import given, strategies as st, settings
from pytest_regressions import image_regression, data_regression
import itertools
import io
import svgutils.transform as sg

def test_annotation__update_tdict_info():
    """
    tests annotation._update_tdict_info function
    """
    random_an = cow.annotation()
    # without a current value --------------------------------------------------
    ## title

    out_dict = random_an._update_tdict_info(t = "banana",
                                            _type = "title")

    el_expected = cow.text("banana")
    el_expected._define_type("cow_title")

    top_title = out_dict.pop("top")

    assert len(out_dict) == 0 and \
        top_title == el_expected, \
        "addition of just a top title does not return a title dictionary as "+\
        "expected (no current value)"

    ## subtitle
    out_dict = random_an._update_tdict_info(t = "banana",
                                                 _type = "subtitle")

    el_expected = cow.text("banana")
    el_expected._define_type("cow_subtitle")

    top_subtitle = out_dict.pop("top")

    assert len(out_dict) == 0 and \
        top_subtitle == el_expected, \
        "addition of just a top subtitle does not return a title dictionary "+\
        "as expected (no current value)"


    # updating with np.nan vs None -------------------------
    current_t = {"top": "banana"}
    bottom_title_start = cow.text("apple")

    ## title -----------
    ### base
    bottom_title_start._define_type("cow_title")
    current_t2 = {"top": "banana", "bottom": bottom_title_start, "left": "left",
                "right": "right"}

    out_dict = random_an._update_tdict_info(t = "pear",
                                                 current_t = current_t,
                                                 _type = "title")
    out_dict2 = random_an._update_tdict_info(t = {"bottom":"pear"},
                                                 current_t = current_t2,
                                                 _type = "title")
    el_expected = cow.text("pear")
    el_expected._define_type("cow_title")

    top_title = out_dict.pop("top")

    assert len(out_dict) == 0 and \
        top_title == el_expected, \
        "addition of just a top title does not return a title dictionary "+\
        "as expected (override current value)"

    bottom_title = out_dict2.pop("bottom")

    assert len(out_dict2) == 3 and \
        bottom_title == el_expected, \
        "addition of just a bottom title does not return a title dictionary "+\
        "as expected (override current value, other dimensions exist)"


    ### None
    out_dict = random_an._update_tdict_info(t = None,
                                                 current_t = current_t,
                                                 _type = "title")

    assert out_dict == current_t, \
        "if t is None, then we should expect no change to current_t"

    out_dict2 = random_an._update_tdict_info(t = {"top": None,
                                                    "bottom":"pear"},
                                                 current_t = current_t2,
                                                 _type = "title")
    current_t2_copy = current_t2.copy()
    bottom_title = out_dict2.pop("bottom")
    top_title = out_dict2.pop("top")
    el_top_expected = current_t2_copy.pop("top")

    assert bottom_title == el_expected and \
        top_title == el_top_expected, \
        "if a title in dictionary is None, then we should expect no change "+\
        "to relative to current_t"

    ### np.nan
    out_dict = random_an._update_tdict_info(t = np.nan,
                                                 current_t = current_t,
                                                 _type = "title")

    assert out_dict is np.nan, \
        "if title is np.nan, we expect the title to be stored as np.nan"


    out_dict2 = random_an._update_tdict_info(t = {"top": np.nan,
                                                    "bottom":"pear"},
                                                 current_t = current_t2,
                                                 _type = "title")
    bottom_title = out_dict2.pop("bottom")
    top_title = out_dict2.get("top")

    assert top_title is None and \
        bottom_title == el_expected and \
        len(out_dict2) == 2,\
        "if title in dictionary is np.nan, we expect the title to be erased "+\
        "(other updates should still happen)"

    ## subtitle -----
    ### base
    bottom_title_start._define_type("cow_subtitle")
    current_t2 = {"top": "banana", "bottom": bottom_title_start, "left": "left",
                "right": "right"}

    out_dict = random_an._update_tdict_info(t = "pear",
                                                 current_t = current_t,
                                                 _type = "subtitle")
    out_dict2 = random_an._update_tdict_info(t = {"bottom":"pear"},
                                                 current_t = current_t2,
                                                 _type = "subtitle")
    el_expected = cow.text("pear")
    el_expected._define_type("cow_subtitle")

    top_title = out_dict.pop("top")

    assert len(out_dict) == 0 and \
        top_title == el_expected, \
        "addition of just a top subtitle does not return a subtitle dictionary "+\
        "as expected (override current value)"

    bottom_title = out_dict2.pop("bottom")

    assert len(out_dict2) == 3 and \
        bottom_title == el_expected, \
        "addition of just a bottom subtitle does not return a subtitle dictionary "+\
        "as expected (override current value, other dimensions exist)"


    ### None
    out_dict = random_an._update_tdict_info(t = None,
                                                 current_t = current_t,
                                                 _type = "subtitle")

    assert out_dict == current_t, \
        "if t is None, then we should expect no change to current_t"

    out_dict2 = random_an._update_tdict_info(t = {"top": None,
                                                    "bottom":"pear"},
                                                 current_t = current_t2,
                                                 _type = "subtitle")
    current_t2_copy = current_t2.copy()
    bottom_title = out_dict2.pop("bottom")
    top_title = out_dict2.pop("top")
    el_top_expected = current_t2_copy.pop("top")

    assert bottom_title == el_expected and \
        top_title == el_top_expected, \
        "if a subtitle in dictionary is None, then we should expect no change "+\
        "to relative to current_t"

    ### np.nan
    out_dict = random_an._update_tdict_info(t = np.nan,
                                                 current_t = current_t,
                                                 _type = "subtitle")
    assert out_dict is np.nan, \
        "if subtitle is np.nan, we expect the subtitle to be np.nan"


    out_dict2 = random_an._update_tdict_info(t = {"top": np.nan,
                                                    "bottom":"pear"},
                                                 current_t = current_t2,
                                                 _type = "subtitle")
    bottom_title = out_dict2.pop("bottom")
    top_title = out_dict2.get("top")

    assert top_title is None and \
        bottom_title == el_expected and \
        len(out_dict2) == 2,\
        "if subtitle in dictionary is np.nan, we expect the subtitle to be erased "+\
        "(other updates should still happen)"

def test_annotation__add__():
    """
    test addition update for annotation objects
    """

    a1_input_full = dict(title = "banana",
                    subtitle = {"bottom":cow.text("apple")},
                    caption = "peeler",
                    tags = ["core", "slice"],
                    tags_format = ("Fig {0}"),
                    tags_order = "auto",
                    tags_loc = "top",
                    tags_inherit="fix")

    a_update_options = dict(title = {"top":"alpha"},
                    subtitle = {"left":cow.text("beta")},
                    caption = "gamma",
                    tags = ["delta", "epsilon"],
                    tags_format = ("Figure {0}"),
                    tags_order = "input",
                    tags_loc = "bottom",
                    tags_inherit="fix")

    a1_full = cow.annotation(**a1_input_full)

    for inner_key in a_update_options.keys():
        if inner_key != "subtitle":
            a2_input = a1_input_full.copy()
            a2_input[inner_key] = a_update_options[inner_key]
        else:
            a2_input = a1_input_full.copy()
            a2_input[inner_key] = {"bottom":cow.text("apple"),
                                   "left":cow.text("beta")}

        update_dict = {inner_key: a_update_options[inner_key]}

        a1_inner = copy.deepcopy(a1_full)

        a2_expected = cow.annotation(**a2_input)

        a1_updated = a1_inner + cow.annotation(**update_dict)

        assert a2_expected == a1_updated, \
            ("updating with addition failed to perform as expected (attribute %s)" % inner_key)

def test_annotation__get_tag_full():
    """
    test annotation's _get_tag_full
    """
    mya = cow.annotation(title = {"top":"my plot", "bottom":"my plot's bottom"},
                     subtitle = {"top":"my very special plot",
                                 "bottom":"below my plot's bottom is the subtitle"},
                     caption = "this is an example figure",
                     tags_format = ("Fig {0}", "Fig {0}.{1}"), tags = ("1", "a"),
                     tags_loc = "top")

    assert mya._get_tag_full(0) == cow.text("Fig 1", _type = "cow_tag"), \
        "expect tag creation to match tags_format structure (level 0), int"
    assert mya._get_tag_full((0,)) == cow.text("Fig 1", _type = "cow_tag"), \
        "expect tag creation to match tags_format structure (level 0), tuple"

    assert mya._get_tag_full((1,2)) == cow.text("Fig 2.c", _type = "cow_tag"), \
        "expect tag creation to match tags_format structure (level 1)"

    with pytest.raises(Exception) as e_info:
        mya._get_tag_full((1,2,3))
        # can't obtain a tag when we don't have formats that far down

def test_annotation__get_tag():
    """
    test annotation's _get_tag function
    """
    mya = cow.annotation(title = {"top":"my plot", "bottom":"my plot's bottom"},
                     subtitle = {"top":"my very special plot",
                                 "bottom":"below my plot's bottom is the subtitle"},
                     caption = "this is an example figure",
                     tags_format = ("Fig {0}", "Fig {0}.{1}"), tags = ("1", "a"),
                     tags_loc = "top")

    assert mya._get_tag(0) == cow.text("Fig 1", _type = "cow_tag"), \
        "expect tag creation to match tags_format structure (level 0), int"

    index = np.random.choice(100)
    assert mya._get_tag(index) == cow.text("Fig %i" % (index+1), _type = "cow_tag"), \
        "expect tag creation to match tags_format structure (level 0), int"


    # can't obtain a tag when we don't have formats that far down
    with pytest.raises(Exception) as e_info:
        mya._get_tag((0,))

    with pytest.raises(Exception) as e_info:
        mya._get_tag((1,2))

    with pytest.raises(Exception) as e_info:
        mya._get_tag((1,2,3))

    # list structure
    mya2 = cow.annotation(title = {"top":"my plot", "bottom":"my plot's bottom"},
                     subtitle = {"top":"my very special plot",
                                 "bottom":"below my plot's bottom is the subtitle"},
                     caption = "this is an example figure",
                     tags = (["banana", "apple"],),
                     tags_loc = "top")

    assert (mya2._get_tag(0) == cow.text("banana", _type = "cow_tag")) & \
            (mya2._get_tag(1) == cow.text("apple", _type = "cow_tag")), \
        "expect tag creation to match list structure (level 0), int"

    assert mya2._get_tag(3) == cow.text("", _type = "cow_tag"), \
        "expected tag of index beyond list length to be an empty tag "+\
        "(but not raise an error)"

    with pytest.raises(Exception) as e_info:
        mya2._get_tag((0,))

    with pytest.raises(Exception) as e_info:
        mya2._get_tag((0,0))


def test_annotation__get_tag_full_rotations():
    """
    test that annotation's _get_tag works correctly with rotation informatin

    """

    mya = cow.annotation(title = {"top":"my plot", "bottom":"my plot's bottom"},
                     subtitle = {"top":"my very special plot",
                                 "bottom":"below my plot's bottom is the subtitle"},
                     caption = "this is an example figure",
                     tags_format = ("Fig {0}", "Fig {0}.{1}"), tags = ("1", "a"),
                     tags_loc = "left")

    assert mya._get_tag_full(0) == \
        cow.text("Fig 1", _type = "cow_tag")._additional_rotation(angle=90), \
        ("expect tag creation to match tags_format structure (level 0), int "+
        "(left rotation)")
    assert mya._get_tag_full((0,)) == \
        cow.text("Fig 1", _type = "cow_tag")._additional_rotation(angle=90), \
        ("expect tag creation to match tags_format structure (level 0), tuple "+
        "(left rotation)")

    assert mya._get_tag_full((1,2)) == \
        cow.text("Fig 2.c", _type = "cow_tag")._additional_rotation(angle=90), \
        ("expect tag creation to match tags_format structure (level 1) "+
        "(left rotation)")

    with pytest.raises(Exception) as e_info:
        mya._get_tag_full((1,2,3))
        # can't obtain a tag when we don't have formats that far down


def test_annotation__get_tag_rotations():
    """
    test that annotation's _get_tag works correctly with rotation informatin
    """

    mya = cow.annotation(title = {"top":"my plot", "bottom":"my plot's bottom"},
                     subtitle = {"top":"my very special plot",
                                 "bottom":"below my plot's bottom is the subtitle"},
                     caption = "this is an example figure",
                     tags_format = ("Fig {0}", "Fig {0}.{1}"), tags = ("1", "a"),
                     tags_loc = "left")

    assert mya._get_tag(0) == \
        cow.text("Fig 1", _type = "cow_tag")._additional_rotation(angle=90), \
        ("expect tag creation to match tags_format structure (level 0), int "+
        "(left rotation)")


    index = np.random.choice(100)
    assert mya._get_tag(index) == \
        cow.text("Fig %i" % (index+1), _type = "cow_tag")._additional_rotation(angle=90), \
        ("expect tag creation to match tags_format structure (level 0), int "+
        "(left rotation)")


    # can't obtain a tag when we don't have formats that far down
    with pytest.raises(Exception) as e_info:
        mya._get_tag((0,))

    with pytest.raises(Exception) as e_info:
        mya._get_tag((1,2))

    with pytest.raises(Exception) as e_info:
        mya._get_tag((1,2,3))

    # list structure
    mya2 = cow.annotation(title = {"top":"my plot", "bottom":"my plot's bottom"},
                     subtitle = {"top":"my very special plot",
                                 "bottom":"below my plot's bottom is the subtitle"},
                     caption = "this is an example figure",
                     tags = (["banana", "apple"],),
                     tags_loc = "left")

    assert (mya2._get_tag(0) ==
            cow.text("banana", _type = "cow_tag")._additional_rotation(angle=90)) & \
            (mya2._get_tag(1) ==
             cow.text("apple", _type = "cow_tag")._additional_rotation(angle=90)), \
        ("expect tag creation to match list structure (level 0), int "+
        "(left rotation)")

    assert mya2._get_tag(3) == \
        cow.text("", _type = "cow_tag"), \
        ("expected tag of index beyond list length to be an empty tag "+
        "(but not raise an error)  "+
        "(left rotation)")

    with pytest.raises(Exception) as e_info:
        mya2._get_tag((0,))

    with pytest.raises(Exception) as e_info:
        mya2._get_tag((0,0))

def test_annotation__step_down_tags_info():
    """
    test for annnotation's _step_down_tags_info functionality
    """
    junk_dict = dict(title = {"top":cow.text("banana", _type = "cow_title")},
                     caption = "minion")
    tag_dict = dict(tags = (["apple", "pear"], "i", "a"),
                    tags_format = ("", "{0}: {1}", "{0}: {1}.{2}"),
                    tags_order="auto", tags_loc="top",
                    tags_inherit="override")

    partial_a = cow.annotation(**tag_dict)
    full_a = cow.annotation(**junk_dict) + partial_a

    stepdown_ann1 = full_a._step_down_tags_info(parent_index = 1)
    stepdown_ann2 = partial_a._step_down_tags_info(parent_index = 1)

    assert stepdown_ann1 == stepdown_ann2, \
        "stepdown should pass only tag information"

    stepdown_tag_dict = dict(tags = ("i", "a"),
                             tags_format = ("pear: {0}", "pear: {0}.{1}"),
                             tags_order = "auto",
                             tags_loc = "top")

    stepdown_tag_expected = cow.annotation(**stepdown_tag_dict)

    assert stepdown_tag_expected == stepdown_ann2, \
        "stepdown with list for first layer incorrect"

    stepdown_ann_second = stepdown_ann2._step_down_tags_info(parent_index=5)

    stepdown_tag_dict_second = dict(tags = ("a",),
                             tags_format = ("pear: vi.{0}",),
                             tags_order = "auto",
                             tags_loc = "top")

    stepdown_tag_second_expected = cow.annotation(**stepdown_tag_dict_second)

    assert stepdown_tag_second_expected == stepdown_ann_second, \
        "stepdown with roman numeral iteration for second layer incorrect"

def test_annotation_passing():
    """
    tests that annotation tag's pass annotations correctly

    these are stastic test-driven development tests
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

    # vis 0

    vis_inner0 = cow.patch([g2, g3]) +\
        cow.layout(nrow = 1) +\
        cow.annotation(tags = ["banana", "apple"])

    vis0 = cow.patch([g0,g1, vis_inner0]) +\
        cow.layout(design = np.array([[0,1],
                                    [2,2]])) +\
        cow.annotation(tags = ("Fig {0}", "Fig {0}.{1}"),
                       tags_format = ("1", "a"),
                       title = "no passing through")
    # see docs for expectation...

    # vis 1

    vis_inner1 = vis_inner0 + cow.annotation(tags_inherit = "override")

    vis1 = cow.patch([g0,g1, vis_inner1]) +\
        cow.layout(design = np.array([[0,1],
                                    [2,2]])) +\
        cow.annotation(tags = ("Fig {0}", "Fig {0}.{1}"),
                       tags_format = ("1", "a"),
                       title = "passing through")
    # see docs for expectation...

    # vis 2

    vis_inner2 = vis_inner0 + cow.annotation(tags_inherit = "fix",
                                             tags = ("Fig 3.{0}",),
                                             tags_format = ("a",))

    vis2 = cow.patch([g0,g1, vis_inner2]) +\
        cow.layout(design = np.array([[0,1],
                                    [2,2]])) +\
        cow.annotation(tags = ["Fig 1", "Fig 2"],
                       tags_format = ("1", "a"),
                       title = "no pass through, top defined, bottom generated")
    # see docs for expectation...

def test_annotation__clean_up_attributes():
    """
    test annotation's _clean_up_attributes
    """


    a = cow.annotation(tags = np.nan, tags_order = "input")
    b = cow.annotation(tags = None, tags_order = "input")

    a._clean_up_attributes()

    assert a == b, \
        "we expect that np.nans are cleaned up after running the "+\
        "_clean_up_attributes function"

    for key in a.__dict__.keys():
        if key not in ["tags_inherit", "tags_order", "tags_depth",
            "_tags_format"]:

            a2 = cow.annotation(**{key: np.nan})
            b2 = cow.annotation(**{key: None})

            assert a2 != b2 and a2.__dict__[key] != b2.__dict__[key], \
                "before running _clean_up_attributes function, we expect "+\
                "the difference in specific key value to be not equal... " +\
                "(key = %s)" % key

            a2._clean_up_attributes()

            assert a2 == b2, \
                "we expect that np.nans are cleaned up after running the "+\
                "_clean_up_attributes function " +\
                "(key = %s)" % key

        if key == "_tags_format":
            a2 = cow.annotation(**{"tags_format": np.nan})
            b2 = cow.annotation(**{"tags_format": None})

            assert a2 != b2 and a2.__dict__[key] != b2.__dict__[key], \
                "before running _clean_up_attributes function, we expect "+\
                "the difference in specific key value to be not equal... " +\
                "(key = %s)" % key

            a2._clean_up_attributes()

            assert a2 == b2, \
                "we expect that np.nans are cleaned up after running the "+\
                "_clean_up_attributes function " +\
                "(key = %s)" % key

@pytest.mark.parametrize("location", ["top", "left", "right", "bottom"])
@pytest.mark.parametrize("_type", ["title", "subtitle", "caption"])
def test_annotation__get_title(location, _type):
    """
    test annotation's _get_title function
    """
    full_ann = cow.annotation(title = {"top": cow.text(label="top title",
                                                       element_text=p9.element_text(angle=0)),
                                       "bottom": cow.text(label="bottom title",
                                                       element_text=p9.element_text(angle=0)),
                                       "left": cow.text(label="left title",
                                                       element_text=p9.element_text(angle=0)),
                                       "right": cow.text(label="right title",
                                                       element_text=p9.element_text(angle=0))},
                              subtitle = {"top": cow.text(label="top subtitle",
                                                       element_text=p9.element_text(angle=0)),
                                       "bottom": cow.text(label="bottom subtitle",
                                                       element_text=p9.element_text(angle=0)),
                                       "left": cow.text(label="left subtitle",
                                                       element_text=p9.element_text(angle=0)),
                                       "right": cow.text(label="right subtitle",
                                                       element_text=p9.element_text(angle=0))},
                              caption = "caption",
                              tags = ("0",))
    if _type in ["title", "subtitle"]:
        attributes_dict = dict(tags = ("0",))
        attributes_dict[_type] = {"top": "top level",
                               "bottom": "bottom level",
                               "left": "left level",
                               "right": "right level"}
        all_single_level_ann = cow.annotation(**attributes_dict)

        attributes_dict2 = {_type: {location: "current (sub)title"} }
        single_ann = cow.annotation(**attributes_dict2)
    else:
        all_single_level_ann = cow.annotation(caption = "caption",
                                              tags = ("0",))
        single_ann = cow.annotation(caption = "caption")


    # without value ----------
    no_ann = cow.annotation(tags = ("0",))

    if _type in ["title", "subtitle"]:
        n_element = no_ann._get_title(_type=_type, location=location)

        assert n_element is None, \
            "no element returned if none defined, type %s, loc %s" % (_type, location)
    else:
        n_element1 = no_ann._get_title(_type=_type, location=location)

        assert n_element1 is None, \
            "no element returned if none defined, type %s, loc %s" % (_type, location)

        n_element2 = no_ann._get_title(_type=_type)

        assert n_element2 is None, \
            "no element returned if none defined, type %s, loc: default" % (_type)

    # with values ----------
    et_full = full_ann._get_title(_type=_type, location=location)
    et_level_full = all_single_level_ann._get_title(_type=_type, location=location)
    et_single = single_ann._get_title(_type=_type, location=location)

    # label check
    if _type in ["title", "subtitle"]:
        assert et_full.label == ("%s %s" % (location, _type)), \
            "expected %s element's label grabbed doesn't match static type (full)" % _type
        assert et_level_full.label == ("%s level" % (location)), \
            "expected %s element's label grabbed doesn't match static type (level full)" % _type
        assert et_single.label == "current (sub)title", \
            "expected %s element's label grabbed doesn't match static type (single)" % _type
    else:
        assert et_full.label == ("%s" % (_type)), \
            "expected %s element's label grabbed doesn't match static type (full)" % _type
        assert et_level_full.label == ("%s" % (_type)), \
            "expected %s element's label grabbed doesn't match static type (level full)" % _type
        assert et_single.label == ("%s" % (_type)), \
            "expected %s element's label grabbed doesn't match static type (single)" % _type
    # text._type check
    for et_i, et in enumerate([et_full, et_level_full, et_single]):
        assert et._type == "cow_" + _type, \
            ("expected %s element grabbed to inherit "+
             "text _type cow_%s, et_i: %i" % (_type, _type, et_i))

    # rotation angle check
    for et_i, et in enumerate([et_full, et_level_full, et_single]):
        if _type in ["title", "subtitle"]:
            if location in ["left", "right"]:
                assert np.allclose(et.element_text.theme_element.properties["rotation"], 90), \
                    ("if type: %s, expect location %s to "+
                     "have 90 degree rotation (et_i %i)" % (_type, location, et_i))
            else:
                # None if no element_text has been defined
                assert (et.element_text is None) or \
                    np.allclose(et.element_text.theme_element.properties["rotation"], 0), \
                    ("if type: %s, expect location %s to "+
                     "have 90 degree rotation (et_i %i)" % (_type, location, et_i))
        else:
            # None if no element_text has been defined
            assert (et.element_text is None) or \
                np.allclose(et.element_text.theme_element.properties["rotation"], 0), \
                ("if type: caption, expect location %s show not alter "+
                 "rotation as caption is always on bottom (et_i %i)" % (location, et_i))


    # save image

@pytest.mark.parametrize("location", ["top", "left", "right", "bottom"])
@pytest.mark.parametrize("_type", ["title", "subtitle", "caption"])
@pytest.mark.parametrize("et_i", [0,1,2])
def test_annotation__get_title_ir(image_regression, location, _type, et_i):
    """
    test annotation _get_title -- image regression tests
    """

    # data set-up ---

    full_ann = cow.annotation(title = {"top": "top title",
                                       "bottom": "bottom title",
                                       "left": "left title",
                                       "right": "right title"},
                              subtitle = {"top": "top subtitle",
                                       "bottom": "bottom subtitle",
                                       "left": "left subtitle",
                                       "right": "right subtitle"},
                              caption = "caption",
                              tags = ("0",))
    if _type in ["title", "subtitle"]:
        attributes_dict = dict(tags = ("0",))
        attributes_dict[_type] = {"top": "top level",
                               "bottom": "bottom level",
                               "left": "left level",
                               "right": "right level"}
        all_single_level_ann = cow.annotation(**attributes_dict)

        attributes_dict2 = {_type: {location: "current (sub)title"} }
        single_ann = cow.annotation(**attributes_dict2)
    else:
        all_single_level_ann = cow.annotation(caption = "caption",
                                              tags = ("0",))
        single_ann = cow.annotation(caption = "caption")


    ann_options = [full_ann, all_single_level_ann, single_ann]


    # regression test ----------
    ann = ann_options[et_i]
    et = ann._get_title(_type=_type, location=location)

    with io.BytesIO() as fid2:
        et.save(filename=fid2, _format = "png", verbose=False)
        image_regression.check(fid2.getvalue(), diff_threshold=.1)




@pytest.mark.parametrize("location", ["title", "subtitle", "caption"])
def test_annontation__calculate_margin_sizes_basic(location):
    """
    test annotation's _calculate_margin_sizes, static / basic

    Details
    -------
    loops over a single type (title, subtitle, caption) - which means
    everything focuses on *top* functionality. Additionally, not a one
    after actual numberical assessments, more comparisons with different
    sizes for default cow.text types.
    """
    a0 = cow.annotation(**{location:"example title"})
    a0_size_dict = a0._calculate_margin_sizes(to_inches=False)

    # check that tags don't impact __calculate_margin_sizes
    a1 = a0 + cow.annotation(tags = ["banana", "apple"])
    a2 = a0 + cow.annotation(tags_format = ("Fig {0}", "Fig {0}.{1}"),
                           tags = ("1", "a"))
    a1_size_dict = a1._calculate_margin_sizes(to_inches=False)
    a2_size_dict = a2._calculate_margin_sizes(to_inches=False)

    assert a0_size_dict == a1_size_dict and \
        a0_size_dict == a2_size_dict, \
        "tag alterations shouldn't change %s margin sizes" % location


    # top or bottom structure for basic text input:
    assert a0_size_dict["extra_used_width"] == 0 and \
        a0_size_dict["min_inner_height"] == 0 and \
        a0_size_dict["top_left_loc"][0] == 0, \
        ("top or bottom structure text (only) with %s should have a "+\
        "clear set of zeros for margins") % location

    # title/subtitle vs caption sizing structure
    if location in ["title", "subtitle"]:
        assert a0_size_dict["min_full_width"] == 0, \
            ("top or bottom structure text (only) with %s should only " +\
             "population min_inner_width, not min_full_width based as " +\
             "the %s should be directly over the image") % (location, location)
    else:
        assert a0_size_dict["min_inner_width"] == 0, \
            ("top or bottom structure text (only) with %s should only " +\
             "population min_full_width, not min_inner_width based as " +\
             "the %s be able to span all other margins") % (location, location)


    # text height (relative to default rcParams)
    # https://stackoverflow.com/questions/41336177/font-size-vs-line-height-vs-actual-height
    if location in ["title", "subtitle"]:
        # caption doesn't meet this expectation and the world says implimentation like this can happen
        assert a0_size_dict["extra_used_height"]/13.5 == \
            cow.rcParams["cow_%s"%location].properties["size"]/\
                cow.rcParams["cow_title"].properties["size"], \
            ("font size for %s correctly aligns with expection relative to "+\
            "output size for title") % location

    # text width (relative to height)
    if location in ["title", "subtitle"]:
        assert a0_size_dict["min_inner_width"]/a0_size_dict["extra_used_height"] > 5,\
            ("expected the length of the %s text to be > 5x the height of "+\
             "the text") % location
    else:
       assert a0_size_dict["min_full_width"]/a0_size_dict["extra_used_height"] > 5,\
            ("expected the length of the %s text to be > 5x the height of "+\
             "the text") % location

@pytest.mark.parametrize("types, location1, location2",
                         list(itertools.product(
                                list(itertools.combinations(["title", "subtitle", "caption"], r=2)),
                                 ["top", "bottom", "left", "right"],
                                 ["top", "bottom", "left", "right"]))
                         )
def test_annotation__calculate_margin_sizes_non_basic(types, location1, location2):
    """
    test annnotation's _calculate_margin_sizes (non-basic)

    Details
    -------
    types : tuple
        of title, subtitle, caption (no dupplicates)
    location1, location2 : str
        different location decisions, can duplicate.

    The checks across these options don't examine static values but more
    how alterations are reflected into the code
    """
    # lets of left, right, top, bottom + some other option.
    # allow for overrides and combinations

    # force all sizes to be the same (to deal with different structures)
    locations = (location1, location2)
    input_dict = dict()

    for t_idx, _type in enumerate(types):
        if _type != "caption":
            input_dict[_type] = \
                {locations[t_idx]: cow.text("text",
                                        element_text=p9.element_text(size=12))}
        else:
            input_dict[_type] = cow.text("text",
                                        element_text=p9.element_text(size=12))


    a0 = cow.annotation(**input_dict)

    a0_size_dict = a0._calculate_margin_sizes(to_inches=False)

    # check that tags don't impact __calculate_margin_sizes
    a1 = a0 + cow.annotation(tags = ["banana", "apple"])
    a2 = a0 + cow.annotation(tags_format = ("Fig {0}", "Fig {0}.{1}"),
                           tags = ("1", "a"))
    a1_size_dict = a1._calculate_margin_sizes(to_inches=False)
    a2_size_dict = a2._calculate_margin_sizes(to_inches=False)

    assert a0_size_dict == a1_size_dict and \
        a0_size_dict == a2_size_dict, \
        "tag alterations shouldn't change %s margin sizes" % location

    # image location matches left & top shifts
    count_left = np.sum([locations[l_idx] == "left" for l_idx in [0,1]
                            if types[l_idx] != "caption"])
    count_width_plus = np.sum([locations[l_idx] in ["left", "right"]
                              for l_idx in [0,1] if types[l_idx] != "caption"])
    count_top = np.sum([locations[l_idx] == "top" for l_idx in [0,1]
                            if types[l_idx] != "caption"])
    count_height_plus = np.sum([(locations[l_idx] in ["top", "bottom"]) or\
                                 (types[l_idx] == "caption") for l_idx in [0,1]])

    if count_width_plus > 0:
        left_side = a0_size_dict["extra_used_width"] * \
                        count_left/count_width_plus
    else:
        left_side = 0

    if count_height_plus > 0:
        top_side = a0_size_dict["extra_used_height"] *\
                        count_top/count_height_plus
    else:
        top_side = 0

    assert a0_size_dict["top_left_loc"] == (left_side, top_side), \
        ("expected image starting location doesn't match expectation "+\
        "relative to text on top and left ({t1}:{l1}, {t2}:{l2}").\
            format(t1=types[0], t2=types[1],
                   l1=locations[0], l2=locations[1])

@pytest.mark.parametrize("_type", ["title", "subtitle", "caption"])
@pytest.mark.parametrize("location", ["top", "bottom", "left", "right"])
def test_annotation__calculate_margin_sizes_static(data_regression, _type, location):
    """
    test annotation's _calculate_margin_sizes - focuses on locational rotation
    differences by using data_regression

    Details:
    --------
    we also check the relative scaling of all attributes to ensure to_inches
    parameter is working correctly
    """
    if _type in ["title", "subtitle"]:
        parameter_dict = {_type:
            {location: "type: %s, location: %s" % (_type, location)}}
    else:
        parameter_dict = {_type: "type: %s, location: %s" % (_type, location)}

    ann = cow.annotation(**parameter_dict)


    out_info = ann._calculate_margin_sizes(to_inches=False)
    out_info_in =  ann._calculate_margin_sizes(to_inches=True)

    # to_inches comparison ----------
    for key in out_info.keys():
        if key != "top_left_loc":
            if out_info_in[key] == 0:
                assert out_info_in[key] == out_info[key], \
                    ("to_inches =T/F should be a expicit scaling of 72 between "+
                    "inches and pt, type: %s, location %s, key: %s" % (_type, location, key))
            else:
                assert np.allclose(out_info_in[key]*72, out_info[key]), \
                    ("to_inches =T/F should be a expicit scaling of 72 between "+
                    "inches and pt, type: %s, location %s, key: %s" % (_type, location, key))
        else:
            for idx in [0,1]:
                if out_info_in[key] == 0:
                    assert out_info_in[key][idx] == out_info[key][idx], \
                        ("to_inches =T/F should be a expicit scaling of 72 between "+
                        "inches and pt, type: %s, location %s, key: %s, idx: %i" % (_type, location, key, idx))
                else:
                    assert np.allclose(out_info_in[key][idx]*72, out_info[key][idx]), \
                        ("to_inches =T/F should be a expicit scaling of 72 between "+
                        "inches and pt, type: %s, location %s, key: %s, idx: %i" % (_type, location, key, idx))

    data_dict_out = {}
    for key in out_info.keys():
        if key != "top_left_loc":
            data_dict_out[key] = str(out_info[key])
        else:
            data_dict_out[key] = \
                {str(i): str(value) for i, value in enumerate(out_info[key])}

    data_regression.check(data_dict_out)


@pytest.mark.parametrize("location", ["top", "bottom", "left", "right"])
def test_annotation__calculate_tag_margin_sizes(data_regression, location):
    """
    test annotation's_calculate_tag_margin_sizes

    Details
    -------
    Deals with
    (1) if a tag should be created,
    (2) nested versus non-nested
    (3) different location types [TODO] rotation structures
    """

    a0_list = cow.annotation(tags = ["banana", "apple"],
                             tags_loc = location)
    a0_list_nest = cow.annotation(tags = (["young", "old"],
                                          ["harry", "hermione", "ron"]),
                             tags_loc = location,
                             tags_format = ("{0}", "{0}{1}"))

    a0_tuple_nest = cow.annotation(tags_format = ("Fig {0}", "Fig {0}.{1}"),
                           tags = ("1", "a"),
                           tags_loc = location)

    # check that titles don't impact __calculate_tag_margin_sizes
    a0_all = [a0_list, a0_list_nest, a0_tuple_nest]
    a_info_str = ["list", "nested-list", "nested-tuple"]

    data_reg_dict = {}
    for a_idx, a0 in enumerate(a0_all):
        a0_title = a0 + cow.annotation(title = "Conformal Inference")


        base = a0._calculate_tag_margin_sizes(index = 1)
        base_plus_title = a0_title._calculate_tag_margin_sizes(index = 1)

        assert base == base_plus_title, \
            ("title attributes shouldn't impact the sizing structure for a "+\
            "tag (structure: %s, loc %s)") % (a_info_str[a_idx], location)

        # data regression tracking
        data_reg_dict[str(a_idx)+"_base"] = \
            {key:str(value) for key, value in base.items()}

        if a0.tags_depth == 2:
            # not title
            a0_s = a0._step_down_tags_info(1)
            a0_title_s = a0_title._step_down_tags_info(1)

            base_s = a0_s._calculate_tag_margin_sizes(index = 0)
            base_plus_title_s = a0_title_s._calculate_tag_margin_sizes(index = 0)

            assert base_s == base_plus_title_s, \
                ("title attributes shouldn't impact the sizing structure for a "+\
                "tag - stepdown (structure: %s, loc %s)") % (a_info_str[a_idx], location)

            # data regression tracking
            data_reg_dict[str(a_idx)+"_base_s"] = \
                {key:str(value) for key, value in base_s.items()}


            # fundamental
            base_f = a0._calculate_tag_margin_sizes(index = 1,
                                                  fundamental=True)
            base_plus_title_f = a0_title._calculate_tag_margin_sizes(index = 1,
                                                  fundamental=True)

            assert base_f == base_plus_title_f and \
                base_f != {'min_inner_width': 0,
                         'min_full_width': 0,
                         'extra_used_width': 0,
                         'min_inner_height': 0,
                         'extra_used_height': 0,
                         'top_left_loc': (0.0, 0)}, \
                ("title attributes shouldn't impact the sizing structure for "+\
                "a tag (fundamental), and fundamental works correctly... "+\
                "(structure: %s, loc %s)") % (a_info_str[a_idx], location)

        # when a tag shouldn't be created
        if a0.tags_depth == 1:
            a0_s = a0._step_down_tags_info(1)
            a0_title_s = a0_title._step_down_tags_info(1)
            base_e = a0_s._calculate_tag_margin_sizes(index = 0)
            base_plus_title_e = a0_title_s._calculate_tag_margin_sizes(index = 0)
        else:
            a0_s = a0._step_down_tags_info(1)._step_down_tags_info(0)
            a0_title_s = a0_title._step_down_tags_info(1)._step_down_tags_info(0)
            base_e = a0._calculate_tag_margin_sizes(index = 1)
            base_plus_title_e = a0_title._calculate_tag_margin_sizes(index = 1)

        assert base_e == base_plus_title_e and \
                base_e == {'min_inner_width': 0,
                         'min_full_width': 0,
                         'extra_used_width': 0,
                         'min_inner_height': 0,
                         'extra_used_height': 0,
                         'top_left_loc': (0.0, 0)}, \
                ("if requesting tag for depth below max depth, no tag would be "+\
                "created - aka margins == 0, (with and without title) " +\
                "(structure: %s, loc %s)") % (a_info_str[a_idx], location)

        # not fundamental
        if a0.tags_depth == 2:
            base_nf = a0._calculate_tag_margin_sizes(index = 1,
                                                  fundamental=False)
            base_plus_title_nf = a0_title._calculate_tag_margin_sizes(index = 1,
                                                  fundamental=False)

            assert base_nf == base_plus_title_nf and \
                base_nf == {'min_inner_width': 0,
                         'min_full_width': 0,
                         'extra_used_width': 0,
                         'min_inner_height': 0,
                         'extra_used_height': 0,
                         'top_left_loc': (0.0, 0)}, \
                ("if not a fundamental tag, no tag should be created "+\
                "(title or not) "+\
                "(structure: %s, loc %s)") % (a_info_str[a_idx], location)


    # list_nest vs tuple_nest
    a0 = a0_list_nest
    a0_title = a0 + cow.annotation(title = "Conformal Inference")

    a0_s = a0._step_down_tags_info(1)
    a0_title_s = a0_title._step_down_tags_info(1)
    base_le = a0_s._calculate_tag_margin_sizes(index = 5)
    base_plus_title_le = a0_title_s._calculate_tag_margin_sizes(index = 5)

    assert base_le == base_plus_title_le and \
        base_le == {'min_inner_width': 0,
                         'min_full_width': 0,
                         'extra_used_width': 0,
                         'min_inner_height': 0,
                         'extra_used_height': 0,
                         'top_left_loc': (0.0, 0)}, \
        ("tags based in lists should have finite length of non-zero tags " +\
        "(structure: %s, loc %s)") % (a_info_str[a_idx], location)


    a0 = a0_tuple_nest
    a0_title = a0 + cow.annotation(title = "Conformal Inference")

    for t_idx in np.random.choice(100,2):
        a0_s = a0._step_down_tags_info(1)
        a0_title_s = a0_title._step_down_tags_info(1)
        base_t = a0_s._calculate_tag_margin_sizes(index = t_idx)
        base_plus_title_t = a0_title_s._calculate_tag_margin_sizes(index = t_idx)

        assert base_t == base_plus_title_t and \
            base_t != {'min_inner_width': 0,
                             'min_full_width': 0,
                             'extra_used_width': 0,
                             'min_inner_height': 0,
                             'extra_used_height': 0,
                             'top_left_loc': (0.0, 0)}, \
            ("tags based in auto creation shouldn't have finite length of "+\
            "non-zero tags (structure: %s, loc %s, t_idx: %i)") % (a_info_str[a_idx], location, t_idx)

    data_regression.check(data_reg_dict)


def test_annotation__get_tag_and_location():
    """
    test annotation's _get_tag_and_location

    Details
    -------
    This group of tests is static, but examines a range of cases:
    1. nested versus single depth tags
    2. list versus infinite length tags
    3. all 4 location descriptions (and correctly deals with 90 degree rotation)
    4. across fundamental & non-fundamental tags

    We also look at 4 specical cases:
    1. [Non-error] full_index is None (fundamental & not)
    2. [Non-error] full_index type is integer (fundamental & not)

    3. [Error] index != full_index[-1]
    4. [Error] width and/or height is too small

    Additional Notes
    ----------------
    We also check manual regression tests on some min_sizing of text objects
    """

    a0_list_t = cow.text("banana", _type = "cow_tag")
    a0_list_nest_t = cow.text("Age: old, Name: harry", _type = "cow_tag")
    a0_tuple_nest_t = cow.text("Fig 5.b", _type = "cow_tag")

    ms_a0_list_t = a0_list_t._min_size()
    ms_a0_list_nest_t = a0_list_nest_t._min_size()
    ms_a0_tuple_nest_t = a0_tuple_nest_t._min_size()

    # "regression check" for default tag elements
    assert np.allclose(ms_a0_list_t, (49.5, 13.5)) and \
        np.allclose(ms_a0_list_nest_t, (146.25, 13.5)) and \
        np.allclose(ms_a0_tuple_nest_t, (43.96875, 13.5)), \
        ("min_sizes of static examples should be fixed against " +
        "current value (simple regression check)")

    # rotationed objects for left/right structure definition
    a0_list_t_r = a0_list_t._additional_rotation(angle=90)
    a0_list_nest_t_r = a0_list_nest_t._additional_rotation(angle=90)
    a0_tuple_nest_t_r = a0_tuple_nest_t._additional_rotation(angle=90)

    ms_a0_list_t_r = a0_list_t_r._min_size()
    ms_a0_list_nest_t_r = a0_list_nest_t_r._min_size()
    ms_a0_tuple_nest_t_r = a0_tuple_nest_t_r._min_size()

    # another check on rotation sizes
    assert np.allclose(ms_a0_list_t, ms_a0_list_t_r[::-1]) and \
        np.allclose(ms_a0_list_nest_t, ms_a0_list_nest_t_r[::-1]) and \
        np.allclose(ms_a0_tuple_nest_t, ms_a0_tuple_nest_t_r[::-1]), \
        ("static examples sizes post 90 degree rotation should just be" +
        "flipped")


    # actual checks set-up
    standard_width, standard_height = 175, 175

    tag_loc_d = {
        "a0_list_d": {"top": (0,0), "left": (0,0),
                      "right": (standard_width - ms_a0_list_t_r[0],0),
                      "bottom": (0, standard_height - ms_a0_list_t[1])},
        "a0_list_nest_d": {"top": (0,0), "left": (0,0),
                      "right": (standard_width - ms_a0_list_nest_t_r[0],0),
                      "bottom": (0, standard_height - ms_a0_list_nest_t[1])},
        "a0_tuple_nest_d": {"top": (0,0), "left": (0,0),
                      "right": (standard_width - ms_a0_tuple_nest_t_r[0],0),
                      "bottom": (0, standard_height - ms_a0_tuple_nest_t[1])}
        }

    image_loc_d = {
        "a0_list_d": {"bottom": (0,0), "right": (0,0),
                    "left": (ms_a0_list_t_r[0], 0),
                    "top": (0, ms_a0_list_t[1])},
        "a0_list_nest_d": {"bottom": (0,0), "right": (0,0),
                    "left": (ms_a0_list_nest_t_r[0], 0),
                    "top": (0, ms_a0_list_nest_t[1])},
        "a0_tuple_nest_d": {"bottom": (0,0), "right": (0,0),
                    "left": (ms_a0_tuple_nest_t_r[0], 0),
                    "top": (0, ms_a0_tuple_nest_t[1])}
    }

    # real output (tag_loc and image_loc)
    for location in ["top", "bottom", "left", "right"]:
        a0_list = cow.annotation(tags = ["banana", "apple"],
                                 tags_loc = location)
        a0_list_nest = cow.annotation(tags = (["young", "old"],
                                              ["harry", "hermione", "ron"]),
                                 tags_loc = location,
                                 tags_format = ("Age: {0}", "Age: {0}, Name: {1}"))

        a0_tuple_nest = cow.annotation(tags_format = ("Fig {0}", "Fig {0}.{1}"),
                               tags = ("1", "a"),
                               tags_loc = location)

        ann_options = [a0_list, a0_list_nest, a0_tuple_nest]
        ann_strings = ["a0_list_d", "a0_list_nest_d", "a0_tuple_nest_d"]
        full_index_options = [(1,), (1,0), (5,1)]

        # full input is provided (no None)
        for ann_index in [0,1,2]:
            ann = ann_options[ann_index]
            ann_str = ann_strings[ann_index]
            full_index = full_index_options[ann_index]
            index = full_index[-1]

            tag_loc, image_loc, _ = ann._get_tag_and_location(index=index,
                                                     full_index=full_index,
                                                     width=standard_width,
                                                     height=standard_height,
                                                     fundamental=False)

            assert np.allclose(tag_loc, tag_loc_d[ann_str][location]), \
                ("tag loc (%s, %s) doesn't match expected as a function " +
                "of location and tag min_size") % (ann_str, location)

            assert np.allclose(image_loc, image_loc_d[ann_str][location]), \
                ("image loc (%s, %s) doesn't match expected as a function " +
                "of location and tag min_size") % (ann_str, location)

        # full_index = None (no error),
        # would be seen as non-fundamental for nested items (why we only look at case 0)
        for ann_index in [0]:
            ann = ann_options[ann_index]
            ann_str = ann_strings[ann_index]
            index = full_index_options[ann_index][-1]

            tag_loc, image_loc, _ = ann._get_tag_and_location(index=index,
                                                     full_index=None,
                                                     width=standard_width,
                                                     height=standard_height,
                                                     fundamental=False)

            assert np.allclose(tag_loc, tag_loc_d[ann_str][location]), \
                ("tag loc (%s, %s) doesn't match expected as a function " +
                "of location and tag min_size, "+
                "even when full_index is None") % (ann_str, location)

            assert np.allclose(image_loc, image_loc_d[ann_str][location]), \
                ("image loc (%s, %s) doesn't match expected as a function " +
                "of location and tag min_size, "+
                "even when full_index is None") % (ann_str, location)

        # type(full_index) = integer (no error),
        # would be seen as non-fundamental for nested items (why we only look at case 0)
        for ann_index in [0]:
            ann = ann_options[ann_index]
            ann_str = ann_strings[ann_index]
            index = full_index_options[ann_index][-1]
            full_index = index

            tag_loc, image_loc, _ = ann._get_tag_and_location(index=index,
                                                     full_index=full_index,
                                                     width=standard_width,
                                                     height=standard_height,
                                                     fundamental=False)

            assert np.allclose(tag_loc, tag_loc_d[ann_str][location]), \
                ("tag loc (%s, %s) doesn't match expected as a function " +
                "of location and tag min_size, "+
                "even when full_index is None") % (ann_str, location)

            assert np.allclose(image_loc, image_loc_d[ann_str][location]), \
                ("image loc (%s, %s) doesn't match expected as a function " +
                "of location and tag min_size, "+
                "even when full_index is None") % (ann_str, location)


    # special cases - no real output
    for location in ["top", "bottom", "left", "right"]:

        a0_list = cow.annotation(tags = ["banana", "apple"],
                                 tags_loc = location)
        a0_list_nest = cow.annotation(tags = (["young", "old"],
                                              ["harry", "hermione", "ron"]),
                                 tags_loc = location,
                                 tags_format = ("Age: {0}", "Age: {0}, Name: {1}"))

        a0_tuple_nest = cow.annotation(tags_format = ("Fig {0}", "Fig {0}.{1}"),
                               tags = ("1", "a"),
                               tags_loc = location)

        # returns (None)^3 ---------------
        # fundamental = False
        out_list_fF = a0_list_nest._get_tag_and_location(index=0,
                                                 full_index=(0,),
                                                 width=100, # really large
                                                 height=100, # really large
                                                 fundamental=False)

        assert np.all(out_list_fF == (None,None,None)), \
            ("if fundamental is False, return None^3 is expected from " +
             "_get_tag_and_location, loc: %s, type = list" % location)

        out_tuple_fF = a0_tuple_nest._get_tag_and_location(index =0,
                                                   full_index = (0,),
                                                   width=100, # really large
                                                   height=100, # really large
                                                   fundamental=False)
        assert np.all(out_tuple_fF == (None,None,None)), \
            ("if fundamental is False, return None^3 is expected from " +
             "_get_tag_and_location, loc: %s, type = tuple"  % location)


        # outside list size
        out_list_l1 = a0_list_nest._get_tag_and_location(index=3,
                                                 full_index=(3,),
                                                 width=100, # really large
                                                 height=100) # really large
        assert np.all(out_tuple_fF == (None,None,None)), \
            ("if index > list length, return None^3 is expected from " +
             "_get_tag_and_location, loc: %s, type = list, level 1"  % location)

        out_list_l2 = a0_list_nest._get_tag_and_location(index=5,
                                                 full_index=(0,5),
                                                 width=100, # really large
                                                 height=100) # really large

        assert np.all(out_tuple_fF == (None,None,None)), \
            ("if index > list length, return None^3 is expected from " +
             "_get_tag_and_location, loc: %s, type = list, level 2"  % location)

        # None for full index + fundamental=False with nested structure
        # leads to (None)^2 output
        for ann_index in [1,2]:
            ann = ann_options[ann_index]
            ann_str = ann_strings[ann_index]
            index = full_index_options[ann_index][-1]

            info_out = ann._get_tag_and_location(index=index,
                                                     full_index=None,
                                                     width=standard_width,
                                                     height=standard_height,
                                                     fundamental=False)

            assert np.all(info_out == (None,None,None)), \
                ("tag loc (%s, %s) with full_index=None, fundamental=False" +
                "should not produce any tags, leading to all output of "+
                "_get_tag_and_location being None") % (ann_str, location)

        # type(full_index) = integer + fundamental=False with nested structure
        # leads to (None)^2 output
        for ann_index in [1,2]:
            ann = ann_options[ann_index]
            ann_str = ann_strings[ann_index]
            index = full_index_options[ann_index][-1]
            full_index = index

            info_out = ann._get_tag_and_location(index=index,
                                                     full_index=full_index,
                                                     width=standard_width,
                                                     height=standard_height,
                                                     fundamental=False)
            assert np.all(info_out == (None,None,None)), \
                ("tag loc (%s, %s) with type(full_index)=int, fundamental=False" +
                "should not produce any tags, leading to all output of "+
                "_get_tag_and_location being None") % (ann_str, location)

        # errors -----------
        # index != full_index[-1] (error)
        with pytest.raises(Exception) as e_info:
            a0_list._get_tag_and_location(index=5,
                                                 full_index=(4),
                                                 width=100, # really large
                                                 height=100)
        with pytest.raises(Exception) as e_info:
            a0_list_nest._get_tag_and_location(index=5,
                                                 full_index=(0,4),
                                                 width=100, # really large
                                                 height=100)
        with pytest.raises(Exception) as e_info:
            a0_tuple_nest._get_tag_and_location(index=5,
                                                 full_index=(0,4),
                                                 width=100, # really large
                                                 height=100)

        # width or height too small (error)

        with pytest.raises(Exception) as e_info:
            a0_list._get_tag_and_location(index=0,
                                                 full_index=(0),
                                                 width=1, # really small
                                                 height=1)
        with pytest.raises(Exception) as e_info:
            a0_list_nest._get_tag_and_location(index=0,
                                                 full_index=(0,0),
                                                 width=1, # really small
                                                 height=1)
        with pytest.raises(Exception) as e_info:
            a0_tuple_nest._get_tag_and_location(index=0,
                                                 full_index=(0,0),
                                                 width=1, # really small
                                                 height=1)



@pytest.mark.parametrize("location", ["top", "bottom", "left", "right"])
@pytest.mark.parametrize("ann_index", [0,1,2])
def test_annotation__get_tag_and_location2(image_regression, location, ann_index):
    """
    regression tests for tag images for annotation's _get_tag_and_location

    Details
    -------
    Includes implicit rotations, different nesting, different types
    of tags (lists or types)
    """

    a0_list = cow.annotation(tags = ["banana", "apple"],
                             tags_loc = location)
    a0_list_nest = cow.annotation(tags = (["young", "old"],
                                          ["harry", "hermione", "ron"]),
                             tags_loc = location,
                             tags_format = ("Age: {0}", "Age: {0}, Name: {1}"))

    a0_tuple_nest = cow.annotation(tags_format = ("Fig {0}", "Fig {0}.{1}"),
                           tags = ("1", "a"),
                           tags_loc = location)

    # tag names for manual checks
    tag_names = ["banana", "Age: old, Name: harry", "Fig 5.b"]


    ann_options = [a0_list, a0_list_nest, a0_tuple_nest]
    full_index_options = [(1,), (1,0), (5,1)]

    # actual assessment
    ann = ann_options[ann_index]
    full_index = full_index_options[ann_index]
    index = full_index[-1]

    _,_,tag_image = ann._get_tag_and_location(width=175,
                                      height=175,
                                      index=index,
                                      full_index = full_index)


    with io.BytesIO() as fid2:
        _save_svg_wrapper(tag_image, fid2,
                          width=to_inches(175, "pt"),
                          height=to_inches(175, "pt"),
                          _format="png", verbose=False)
        image_regression.check(fid2.getvalue(), diff_threshold=.1)




def _create_blank_image_with_titles_helper(out, width, height):
    """
    takes in list from annotation's _get_titles_and_locations and
    creates an image

    Arguments
    ---------
    out : list
        list of output from annotation's _get_titles_and_locations
    width : float
        width (in pt) used to generate `out`
    height : float
        height (in pt) used to generate `out`

    Returns
    -------
    svg object with titles/subtitles/captions inserted
    """
    base_image = sg.SVGFigure()
    base_image.set_size((str(width)+"pt", str(height)+"pt"))
    # add a view box... (set_size doesn't correctly update this...)
    base_image.root.set("viewBox", "0 0 %s %s" % (str(width), str(height)))

    for loc_tuple, (svg_obj, _) in out:
        _add_to_base_image(base_image, svg_obj, loc_tuple)

    return base_image


def test_annotation__get_titles_and_locations_basic_full(image_regression):


    full_ann = cow.annotation(title = {"top": "top title",
                                       "bottom": "bottom title",
                                       "left": "left title",
                                       "right": "right title"},
                              subtitle = {"top": "top subtitle",
                                       "bottom": "bottom subtitle",
                                       "left": "left subtitle",
                                       "right": "right subtitle"},
                              caption = "caption",
                              tags = ("0",))

    width_pt = 400
    height_pt = 400

    out_full = full_ann._get_titles_and_locations(width=width_pt,
                                                  height=height_pt)

    # basic correct outcome sizes ----------
    assert (len(out_full) == 9) and \
        np.all([len(x) == 2 for x in out_full]) and \
        np.all([len(x[1]) == 2 for x in out_full]) and \
        np.all([inherits(x[1][0], sg.SVGFigure) for x in out_full]) and \
        np.all([inherits(x[1][1], tuple) for x in out_full]) and \
        np.all([inherits(x[0], tuple) for x in out_full]), \
        ("if all title/subtitle/caption element is used " +
         "outcome of _get_titles_and_locations structure " +
         "should be length 9, tuples of correct structure")

    full_svg = _create_blank_image_with_titles_helper(out_full,
                                                      width=width_pt,
                                                      height=height_pt)

    with io.BytesIO() as fid2:
        _save_svg_wrapper(full_svg, fid2,
                          width=to_inches(width_pt, "pt"),
                          height=to_inches(height_pt, "pt"),
                          _format="png", verbose=False)
        image_regression.check(fid2.getvalue(), diff_threshold=.1)



@pytest.mark.parametrize("_type", ["title", "subtitle", "caption"])
def test_annotation__get_titles_and_locations_basic_level(image_regression,_type):
    # create a set of static combinations of
    # titles, subtitles, captions (in different locations)
    # identify expected locations and potentially try to create
    # svg objects of the image themselves to compare the output too

    if _type in ["title", "subtitle"]:
        attributes_dict = dict(tags = ("0",))
        attributes_dict[_type] = {"top": "top level",
                               "bottom": "bottom level",
                               "left": "left level",
                               "right": "right level"}
        all_single_level_ann = cow.annotation(**attributes_dict)
    else:
        all_single_level_ann = cow.annotation(caption = "caption",
                                              tags = ("0",))


    width_pt = 400
    height_pt = 400

    out_level = all_single_level_ann._get_titles_and_locations(width=width_pt,
                                                              height=height_pt)


    # basic correct outcome sizes ----------
    if _type in ["title", "subtitle"]:
        assert (len(out_level) == 4) and \
            np.all([len(x) == 2 for x in out_level]) and \
            np.all([len(x[1]) == 2 for x in out_level]) and \
            np.all([inherits(x[1][0], sg.SVGFigure) for x in out_level]) and \
            np.all([inherits(x[1][1], tuple) for x in out_level]) and \
            np.all([inherits(x[0], tuple) for x in out_level]), \
            ("if all %s element is used " +
             "outcome of _get_titles_and_locations structure " +
             "should be length 9, tuples of correct structure") % (_type)
    else:
        assert (len(out_level) == 1) and \
            np.all([len(x) == 2 for x in out_level]) and \
            np.all([len(x[1]) == 2 for x in out_level]) and \
            np.all([inherits(x[1][0], sg.SVGFigure) for x in out_level]) and \
            np.all([inherits(x[1][1], tuple) for x in out_level]) and \
            np.all([inherits(x[0], tuple) for x in out_level]), \
            ("if only %s element is used " +
             "outcome of _get_titles_and_locations structure " +
             "should be length 9, tuples of correct structure") % (_type)


    level_svg = _create_blank_image_with_titles_helper(out_level,
                                                      width=width_pt,
                                                      height=height_pt)

    with io.BytesIO() as fid2:
        _save_svg_wrapper(level_svg, fid2,
                          width=to_inches(width_pt, "pt"),
                          height=to_inches(height_pt, "pt"),
                          _format="png", verbose=False)
        image_regression.check(fid2.getvalue(), diff_threshold=.1)


@pytest.mark.parametrize("location", ["top", "left", "right", "bottom"])
@pytest.mark.parametrize("_type", ["title", "subtitle", "caption"])
def test_annotation__get_titles_and_locations_basic_single(image_regression,
                                                           location, _type):
    # create a set of static combinations of
    # titles, subtitles, captions (in different locations)
    # identify expected locations and potentially try to create
    # svg objects of the image themselves to compare the output too

    if _type in ["title", "subtitle"]:
        attributes_dict2 = {_type: {location: "current (sub)title"} }
        single_ann = cow.annotation(**attributes_dict2)
    else:
        single_ann = cow.annotation(caption = "caption")


    width_pt = 400
    height_pt = 400

    out_single = single_ann._get_titles_and_locations(width = width_pt,
                                                      height = height_pt)


    # basic correct outcome sizes ----------
    if _type in ["title", "subtitle"]:
        assert (len(out_single) == 1) and \
            np.all([len(x) == 2 for x in out_single]) and \
            np.all([len(x[1]) == 2 for x in out_single]) and \
            np.all([inherits(x[1][0], sg.SVGFigure) for x in out_single]) and \
            np.all([inherits(x[1][1], tuple) for x in out_single]) and \
            np.all([inherits(x[0], tuple) for x in out_single]), \
            ("if single %s, %s element is used " +
             "outcome of _get_titles_and_locations structure " +
             "should be length 9, tuples of correct structure") % (_type, location)
    else:
        assert (len(out_single) == 1) and \
            np.all([len(x) == 2 for x in out_single]) and \
            np.all([len(x[1]) == 2 for x in out_single]) and \
            np.all([inherits(x[1][0], sg.SVGFigure) for x in out_single]) and \
            np.all([inherits(x[1][1], tuple) for x in out_single]) and \
            np.all([inherits(x[0], tuple) for x in out_single]), \
            ("if only %s, (pointless location: %s) element is used " +
             "outcome of _get_titles_and_locations structure " +
             "should be length 9, tuples of correct structure") % (_type, location)


    single_svg = _create_blank_image_with_titles_helper(out_single,
                                                      width=width_pt,
                                                      height=height_pt)

    with io.BytesIO() as fid2:
        _save_svg_wrapper(single_svg, fid2,
                          width=to_inches(width_pt, "pt"),
                          height=to_inches(height_pt, "pt"),
                          _format="png", verbose=False)
        image_regression.check(fid2.getvalue(), diff_threshold=.1)



