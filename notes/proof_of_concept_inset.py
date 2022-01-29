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


p1 = p9.ggplot(mtcars) +\
  p9.geom_boxplot(p9.aes(x="gear",y= "disp", group = "gear")) +\
  p9.labs(title = 'Plot 1')

p2 = p9.ggplot(mtcars) +\
  p9.geom_point(p9.aes(x="hp", y="wt")) +\
  p9.labs(title = 'Plot 2')



# functions ---------


def gg_to_svg(gg, width, height, dpi, limitsize=True):
    """
    Convert plotnine ggplot figure to svgutils object and return it

    Arguments
    ---------
    gg: plotnine.ggplot.ggplot
        object to save as a svg image
    width : float
        width in inches to be passed to the plotnine's ggplot.save function
    height: float
        height in inches to be passed to the plotnine's ggplot.save function
    dpi: int
        dots per inch, to be passed to the plotnine's ggplot.save function
    limitsize: boolean
        logic if plotnine's ggplot.save function should check if the requested
        width and height in inches are greater than 50 (assumes the user
        accidentally entered in these values w.r.t. pixels)

    Returns
    -------
    svgutils.tranform representation of the ggplot object
        (aka an svg representation)

    Details
    -------
    Code idea motified by the stackoverflow question here, https://stackoverflow.com/questions/8598673/how-to-save-a-pylab-figure-into-in-memory-file-which-can-be-read-into-pil-image/8598881
    and truly influenced by svgutils.transform.from_mpl function.
    """

    fid = io.StringIO()

    try:
        gg.save(fid, format= "svg", height = height, width = width,
            dpi=dpi, units = "in", limitsize = limitsize, verbose=False) # TODO check why they have this naming...
    except ValueError:
        rasie(ValueError, "No ggplot SVG backend")
    fid.seek(0)
    img = sg.fromstring(fid.read())

    return img



def transform_size(size_string_tuple):
    """
    takes string with unit and converts it to a float w.r.t pt

    Argument
    --------
    size_string_tuple : string tuple
        tuple of strings with size of svg image

    Return
    ------
    tuple of floats of sizes w.r.t pt
    """
    value = [float(re.search(r'[0-9\.+]+', s).group())
                for s in size_string_tuple]

    if size_string_tuple[0].endswith("pt"):
       return (value[0], value[1])
    elif size_string_tuple[0].endswith("in"):
        return (value[0]/72, value[1]/72)
    elif size_string_tuple[0].endswith("px"):
        return (value[0]*.75, value[1]*.75)
    else:
        raise ValueError("size_string_tuple structure of object not as "+\
                         "expected, new size type")


def proposed_scaling_both(current, desired):
    """
    identify a x and y scaling to make the current size into the desired size

    Arguments
    ---------
    current : tuple
        float tuple of current size of svg object
    desired : tuple
        float tuple of desired size of svg object

    Returns
    -------
    tuple
        float tuple of scalar constants for size change in each dimension
    """
    scale_x = desired[0]/current[0]
    scale_y = desired[1]/current[1]

    return scale_x, scale_y


def real_size_out_svg(gg, height, width, dpi, limitsize=True):
    """
    Calculate the output size for a plotnine.ggplot object saving as an
    svg

    Details
    -------
    This function is useful given default approach for the saving of
    images uses `bbox_inches="tight"`. This appears to be done since to obtain
    desirable containment of all parts in the image (not to overflow the
    provided space) and because matplotlib's `plt.tight_layout()` doesn't
    preform as expected for the `plotnine.ggplot` objects.

    This code leverages ideas that are presented in a blog post by Kavi Gupta
    at https://kavigupta.org/2019/05/18/Setting-the-size-of-figures-in-matplotlib/

    Arguments
    ---------
    gg : plotnine.ggplot.ggplot
        ggplot object to calculate optimal size
    height : float
        desired height of svg output (in inches)
    width : float
        desired width of svg output (in inches)
    dpi : float
        dots per inch of saved object
    limitsize : boolean
        logic if plotnine's ggplot.save function should check if the requested
        width and height in inches are greater than 50 (assumes the user
        accidentally entered in these values w.r.t. pixels)

    Returns
    -------
    tuple
        of the actual height and width (in inches) of the svg image that would
        be created if the above
    """
    fid = io.StringIO()

    try:
        gg.save(fid, format="svg", height=height, width=width,
            dpi=dpi, units="in", limitsize=limitsize, verbose=False) # TODO check why they have this naming...
    except ValueError:
        rasie(ValueError, "No ggplot SVG backend")
    fid.seek(0)
    img = sg.fromstring(fid.read())

    new_width, new_height = transform_size(img.get_size())

    return new_width / 72, new_height / 72 # this does it for inches...


def select_correcting_size_svg(gg, height, width, dpi, limitsize=True,
                    eps=1e-2, maxIter=2, min_size_px=10):
    """
    Obtain the correct input saving size plotnine.ggplot object to actual
    obtain desired height and width (inches)

    Details
    -------
    This function is useful given default approach for the saving of
    images uses `bbox_inches="tight"`. This appears to be done since to obtain
    desirable containment of all parts in the image (not to overflow the
    provided space) and because matplotlib's `plt.tight_layout()` doesn't
    preform as expected for the `plotnine.ggplot` objects.

    This code leverages ideas that are presented in a blog post by Kavi Gupta
    at https://kavigupta.org/2019/05/18/Setting-the-size-of-figures-in-matplotlib/.
    It is iterative procedure in nature (the reason for eps and maxIter), eps
    looks at the difference between the desired and obtained height and width.

    Arguments
    ---------
    gg : plotnine.ggplot.ggplot
        ggplot object to calculate optimal size
    height : float
        desired height of svg output (in inches)
    width : float
        desired width of svg output (in inches)
    dpi : float
        dots per inch of saved object
    limitsize : boolean
        logic if plotnine's ggplot.save function should check if the requested
        width and height in inches are greater than 50 (assumes the user
        accidentally entered in these values w.r.t. pixels)
    eps : float
        maximum allowed difference between height and width output versus the
        desired output
    maxIter : int
        maximum number of steps that can be used to the difference
        between desired and output height and width within minimum distance
    min_size_px : int
        early stopping rule if converging height or width has a pixel size
        smaller than or equal to this value (assumes process will not converge)

    Returns
    -------
    tuple
        three value tuple of width, height to provide desired measures and a
        boolean value (true if iteration was successful, false otherwise -
        just returns original width and height)
    """
    # starting at desired values (a reasonsable starting values)
    desired_width, desired_height = width, height
    current_width, current_height = width, height

    deltas = [] # how close we've gotten
    current_sizes = []
    while True:
        actual_width, actual_height = real_size_out_svg(gg=gg,
                                                        height=current_height,
                                                        width=current_width,
                                                        dpi=dpi,
                                                        limitsize=limitsize)

        current_width *= desired_width / actual_width
        current_height *= desired_height / actual_height
        deltas.append(abs(actual_width - desired_width) + \
                      abs(actual_height - desired_height))
        current_sizes.append((current_width, current_height))

        # decisions to terminate interation
        if deltas[-1] < eps:
            return current_width, current_height, True
        elif len(deltas) > maxIter:
            raise StopIteration("unable to get correct size within epsilon and number of interations")
        elif current_width * dpi < min_size_px or current_height * dpi < min_size_px:
            raise ValueError("height or width is too small for acceptable image")
    # return width, height, False, deltas




# code ---------


relate_inset_info = dict(x=.35,
                         y=.60,
                         width = .33,
                         height = .33)

width = 8
height = 6
dpi = 300



base_image = sg.SVGFigure()
base_image.set_size((str(width*72)+"pt", str(height*72)+"pt"))

correct_width_in, \
    correct_height_in, _ = select_correcting_size_svg(gg=p1,
                                                   height=height,
                                                   width=width,
                                                   dpi=dpi,
                                                   maxIter=4)

svg = gg_to_svg(p1,
                width=correct_width_in,
                height=correct_height_in,
                dpi=dpi)


current_size_raw = svg.get_size()
current_size = transform_size(current_size_raw)
desired_size_raw = [str(v * 72)+"pt" for v in [width, height]]
desired_size = transform_size(desired_size_raw)

scale = proposed_scaling_both(current_size, desired_size)

inner_root = svg.getroot()
inner_root.moveto(x=0,y=0,scale_x=scale[0], scale_y=scale[1])

scaled_svg = sg.SVGFigure()
scaled_svg.set_size((str(current_size[0]*scale[0])+"pt",
                  str(current_size[1]*scale[1])+"pt"))

scaled_svg.append(inner_root)
scaled_size_raw = scaled_svg.get_size()
scaled_size = transform_size(scaled_size_raw)

inner_root = scaled_svg.getroot()

# thought scale to fit desired location, then center?
base_image.append(inner_root)




# inset info:
inset_width = relate_inset_info.get("width")*width
inset_height = relate_inset_info.get("height")*height

correct_width_inset, \
    correct_height_inset, _ = select_correcting_size_svg(gg=p2,
                                                   height=inset_height,
                                                   width=inset_width,
                                                   dpi=dpi,eps = 1e-1,
                                                   maxIter=10)
svg_inset = gg_to_svg(p2,
                width=correct_width_inset,
                height=correct_height_inset,
                dpi=dpi)


current_size_raw = svg_inset.get_size()
current_size = transform_size(current_size_raw)
desired_size_raw = [str(v * 72)+"pt" for v in [inset_width, inset_height]]
desired_size = transform_size(desired_size_raw)

scale = proposed_scaling_both(current_size, desired_size)

inner_root = svg_inset.getroot()
inner_root.moveto(x=0,y=0,scale_x=scale[0], scale_y=scale[1])

scaled_svg = sg.SVGFigure()
scaled_svg.set_size((str(current_size[0]*scale[0])+"pt",
                  str(current_size[1]*scale[1])+"pt"))

scaled_svg.append(inner_root)
scaled_size_raw = scaled_svg.get_size()
scaled_size = transform_size(scaled_size_raw)

inner_root = scaled_svg.getroot()

#
inner_lc_raw =((width * relate_inset_info.get("x")) * 72,
                (height * (1-relate_inset_info.get("y")-relate_inset_info.get("height"))) * 72)

# lc_raws.append(inner_lc_raw)

new_lc = inner_lc_raw

inner_root.moveto(x=new_lc[0],
                  y=new_lc[1])
# thought scale to fit desired location, then center?
base_image.append(inner_root)


base_image.save("inset.svg")

