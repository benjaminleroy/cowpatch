from pytest_regressions import image_regression

import numpy as np
import cowpatch as cow
from cowpatch.utils import inherits
import pytest
import io

import plotnine as p9
import plotnine.data as p9_data

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
                       dpi=96, _format="png")
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
                       dpi=96, _format="png")

        image_regression.check(fid2.getvalue(), diff_threshold=.1)

def test_patch__and__(image_regression):
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
        p9.geom_histogram(p9.aes(x="hwy")) +\
        p9.facet_wrap("class")

    g0p = cow.patch(g0)
    g1p = cow.patch(g1)
    g2p = cow.patch(g2)
    g3p = cow.patch(g3)


    g01 = g0p + g1p
    g02 = g0p + g2p
    g012 = g0p + g1p + g2p
    g012_2 = g01 + g2p

    pass



