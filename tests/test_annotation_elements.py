import cowpatch as cow
import numpy as np
import pandas as pd
import copy
import plotnine as p9
import plotnine.data as p9_data

import pytest

def test__update_tdict_info():
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

def test__add__():
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

def test__get_tag():
    mya = cow.annotation(title = {"top":"my plot", "bottom":"my plot's bottom"},
                     subtitle = {"top":"my very special plot",
                                 "bottom":"below my plot's bottom is the subtitle"},
                     caption = "this is an example figure",
                     tags_format = ("Fig {0}", "Fig {0}.{1}"), tags = ("1", "a"),
                     tags_loc = "top")

    assert mya._get_tag(0) == cow.text("Fig 1", _type = "cow_tag"), \
        "expect tag creation to match tags_format structure (level 0), int"
    assert mya._get_tag((0,)) == cow.text("Fig 1", _type = "cow_tag"), \
        "expect tag creation to match tags_format structure (level 0), tuple"

    assert mya._get_tag((1,2)) == cow.text("Fig 2.c", _type = "cow_tag"), \
        "expect tag creation to match tags_format structure (level 1)"

    with pytest.raises(Exception) as e_info:
        mya._get_tag((1,2,3))
        # can't obtain a tag when we don't have formats that far down

def test__get_tag_rotations():
    """
    test that ._get_tag works correctly with rotation informatin

    """

    mya = cow.annotation(title = {"top":"my plot", "bottom":"my plot's bottom"},
                     subtitle = {"top":"my very special plot",
                                 "bottom":"below my plot's bottom is the subtitle"},
                     caption = "this is an example figure",
                     tags_format = ("Fig {0}", "Fig {0}.{1}"), tags = ("1", "a"),
                     tags_loc = "left")

    assert mya._get_tag(0) == cow.text("Fig 1", _type = "cow_tag"), \
        "expect tag creation to match tags_format structure (level 0), int"
    assert mya._get_tag((0,)) == cow.text("Fig 1", _type = "cow_tag"), \
        "expect tag creation to match tags_format structure (level 0), tuple"

    assert mya._get_tag((1,2)) == cow.text("Fig 2.c", _type = "cow_tag"), \
        "expect tag creation to match tags_format structure (level 1)"

    with pytest.raises(Exception) as e_info:
        mya._get_tag((1,2,3))
        # can't obtain a tag when we don't have formats that far down

def test__step_down_tags_info():
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

def test__clean_up_attributes():
    """
    test _clean_up_attributes
    """


    a = cow.annotation(tags = np.nan, tags_order = "input")
    b = cow.annotation(tags = None, tags_order = "input")

    a._clean_up_attributes()

    assert a == b, \
        "we expect that np.nans are cleaned up after running the "+\
        "_clean_up_attributes function"

    for key in a.__dict__.keys():
        if key not in ["tags_inherit", "tags_order", "tags_depth"]:
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




