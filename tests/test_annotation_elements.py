import cowpatch as cow
import numpy as np
import pandas as pd
import copy
import plotnine as p9
import plotnine.data as p9_data

import pytest
from hypothesis import given, strategies as st, settings
import itertools

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

@pytest.mark.parametrize("location", ["title", "subtitle", "caption"])
def test__calculate_margin_sizes_basic(location):
    """
    test _calculate_margin_sizes, static
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
def test__calculate_margin_sizes_non_basic(types, location1, location2):
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

    # TODO this failed...
    assert a0_size_dict["top_left_loc"] == (left_side, top_side), \
        ("expected image starting location doesn't match expectation "+\
        "relative to text on top and left ({t1}:{l1}, {t2}:{l2}").\
            format(t1=types[0], t2=types[1],
                   l1=locations[0], l2=locations[1])

@pytest.mark.parametrize("location", ["top", "bottom", "left", "right"])
def test__calculate_tag_margin_sizes(location):
    """
    test _calculate_tag_margin_sizes
    """
    # test if tag should actually be created
    # nesting

    a0_list = cow.annotation(tags = ["banana", "apple"],
                             tags_loc = location)
    a0_list_nest = cow.annotation(tags = (["young", "old"],
                                          ["harry", "hermione", "ron"]),
                             tags_loc = location)

    a0_tuple_nest = cow.annotation(tags_format = ("Fig {0}", "Fig {0}.{1}"),
                           tags = ("1", "a"),
                           tags_loc = location)

    # check that tags don't impact __calculate_margin_sizes
    a0_all = [a0_list, a0_list_nest, a0_tuple_nest]
    a_info_str = ["list", "nested-list", "nested-tuple"]
    for a_idx, a0 in enumerate(a0_all):
        a0_title = a0 + cow.annotation(title = "Conformal Inference")

        if a0.tags_depth == 1:
            base = a0._calculate_tag_margin_sizes(index = (1,))
            base_plus_title = a0_title._calculate_tag_margin_sizes(index = (1,))
        else:
            base = a0._calculate_tag_margin_sizes(index = (1,0))
            base_plus_title = a0_title._calculate_tag_margin_sizes(index = (1,0))

        assert base == base_plus_title, \
            ("title attributes shouldn't impact the sizing structure for a "+\
            "tag (structure: %s, loc %s)") % (a_info_str[a_idx], location)

        # fundamental
        if a0.tags_depth == 2:
            base_f = a0._calculate_tag_margin_sizes(index = (1,),
                                                  fundamental=True)
            base_plus_title_f = a0_title._calculate_tag_margin_sizes(index = (1,),
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
            base_e = a0._calculate_tag_margin_sizes(index = (1,0))
            base_plus_title_e = a0_title._calculate_tag_margin_sizes(index = (1,0))
        else:
            base_e = a0._calculate_tag_margin_sizes(index = (1,0,1))
            base_plus_title_e = a0_title._calculate_tag_margin_sizes(index = (1,0,1))

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
            base_nf = a0._calculate_tag_margin_sizes(index = (1,),
                                                  fundamental=False)
            base_plus_title_nf = a0_title._calculate_tag_margin_sizes(index = (1,),
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

    base_le = a0._calculate_tag_margin_sizes(index = (1,5))
    base_plus_title_le = a0_title._calculate_tag_margin_sizes(index = (1,5))

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
        base_t = a0._calculate_tag_margin_sizes(index = (1,t_idx))
        base_plus_title_t = a0_title._calculate_tag_margin_sizes(index = (1,t_idx))

        assert base_t == base_plus_title_t and \
            base_t != {'min_inner_width': 0,
                             'min_full_width': 0,
                             'extra_used_width': 0,
                             'min_inner_height': 0,
                             'extra_used_height': 0,
                             'top_left_loc': (0.0, 0)}, \
            ("tags based in auto creation shouldn't have finite length of "+\
            "non-zero tags (structure: %s, loc %s, t_idx: %i)") % (a_info_str[a_idx], location, t_idx)


def test__get_tag_and_location():
    raise ValueError("Not Tested")

def test__get_titles_and_locations():
    raise ValueError("Not Tested")

def test__step_down_tags_info():
    raise ValueError("Not Tested")


