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
        p9.labs(title = 'Plot 3 color')

    g1_legend = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 3 color')

    vis_patch = cow.patch(g0,g1_no_legend,g1_legend)
    vis_patch += cow.layout(design = np.array([[0,0,0,1,1,1],
                                               [0,0,0,2,2,2],
                                               [0,0,0,2,2,2]]))

    assert inherits(vis_patch, cow.patch), \
        "check patch addition correctly returns patch object"

    assert vis_patch._layout() == \
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
