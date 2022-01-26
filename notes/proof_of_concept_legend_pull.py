# super basic tests / exploration

import numpy as np
import pandas as pd
import plotnine as p9
import svgutils.transform as sg
import io
import os
import re

import cairosvg

from PIL import Image
import progressbar

from contextlib import suppress # For class text object
import xml.etree.ElementTree as ET #

import progressbar


# for text in svg
import matplotlib.pyplot as plt
plt.rcParams['svg.fonttype'] = 'none'


# Predefined plots
# -----------------
# from https://github.com/thomasp85/patchwork/blob/master/tests/testthat/helper-setup.R
mtcars = pd.read_csv('https://gist.githubusercontent.com/ZeccaLehn/4e06d2575eb9589dbe8c365d61cb056c/raw/64f1660f38ef523b2a1a13be77b002b98665cdfe/mtcars.csv')


p2 = p9.ggplot(mtcars) +\
  p9.geom_point(p9.aes(x="hp", y="wt", color = "mpg")) +\
  p9.labs(title = 'Plot 2')




## grab_legend

#
import copy
import matplotlib


from matplotlib.offsetbox import AnchoredOffsetbox


def grab_legend(gg, width, height, filename):
    """
    this function is just showing we could extra a svg legend representation
    this function can actually give a figure back (so it should act just like
    a matplotlib object or ggplot (allow you to update the gg after the call?))

    should generally think of this object and how people manipulate it & how
    it works with other wrapper objects...

    Arguments
    ---------
    gg : plotnine.ggplot object
    width : float
        width in inches
    height : float
        height in inches
    filename : str

    Details
    -------
    For some reason I'm slightly worried about scaling of the object (I think
    my mind is broken w.r.t. what scaling means again...)

    It is possible we still need to correct the bbox_inches="tight" problem...
    """

    gg2 = copy.deepcopy(gg)

    gg2._build()

    # setup
    figure, axs = gg2._create_figure()
    gg2._setup_parameters()

    #https://github.com/has2k1/plotnine/blob/9fbb5f77c8a8fb8c522eb88d4274cd2fa4f8dd88/plotnine/guides/guides.py
    legend_box = gg2.guides.build(gg2)
    loc = "center"

    anchored_box = AnchoredOffsetbox(
            loc=loc,
            child=legend_box,
            pad=0.,
            frameon=False,
            bbox_to_anchor=(.5, .5),
            bbox_transform=figure.transFigure,
            borderpad=0.)

    anchored_box.set_zorder(90.1)
    gg2.figure._themeable['legend_background'] = anchored_box
    ax = gg2.axs[0]
    ax.add_artist(anchored_box)

    bbox = anchored_box.get_tightbbox(anchored_box.get_figure().canvas.get_renderer())


    # need to do the same thing we did to the text... (in terms of transforming the bbox to a position to reverse)...
    # also need to figure out figure size requests... (how does that work with this?)
    # also how to deal with bbox_inches="tight" coming into play...
    # do we need to alter the figure directly? (and not do it with svg...)

    plt.axis('off')
    #figure.show()
    figure.set_size_inches(width,height) # maybe do this w.r.t. the bbox? (then later it later?)
    # not sure why we wouldn't just give this...
    figure.savefig(filename, bbox_inches="tight")


grab_legend(p2, width=1, height = 2.5, filename = "just_legend.svg")

grab_legend(p2, width=.1, height = .25, filename = "just_legend_small.svg")

grab_legend(p2, width=0, height = 0, filename = "just_legend_non_size.svg")



grab_legend(p2, width=5, height = 5, filename = "just_legend.png")

grab_legend(p2, width=1, height = 2.5, filename = "just_legend.png")

grab_legend(p2, width=.1, height = .25, filename = "just_legend_small.png")

grab_legend(p2, width=0, height = 0, filename = "just_legend_non_size.png")

