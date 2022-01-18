# super basic tests / exploration

import numpy as np
import pandas as pd
import plotnine as p9
import io
import os
import re
from PIL import Image


# for text in svg
import matplotlib.pyplot as plt
plt.rcParams['svg.fonttype'] = 'none'


# Predefined plots
# -----------------
# from https://github.com/thomasp85/patchwork/blob/master/tests/testthat/helper-setup.R
mtcars = pd.read_csv('https://gist.githubusercontent.com/ZeccaLehn/4e06d2575eb9589dbe8c365d61cb056c/raw/64f1660f38ef523b2a1a13be77b002b98665cdfe/mtcars.csv')

p0 = p9.ggplot(mtcars) +\
  p9.geom_bar(p9.aes(x="gear")) +\
  p9.facet_wrap("cyl") +\
  p9.labs(title = 'Plot 0')

p1 = p9.ggplot(mtcars) +\
  p9.geom_boxplot(p9.aes(x="gear",y= "disp", group = "gear")) +\
  p9.labs(title = 'Plot 1')

p2 = p9.ggplot(mtcars) +\
  p9.geom_point(p9.aes(x="hp", y="wt", color = "mpg")) +\
  p9.labs(title = 'Plot 2')

p3 = (p9.ggplot(mtcars) +\
  p9.geom_point(p9.aes(x = "mpg", y="disp")) +\
  p9.labs(title = 'Plot 3'))



design = np.array([[1,1,3,3,np.nan,np.nan,np.nan,np.nan],
              [1,1,3,3,np.nan,np.nan,np.nan,np.nan],
              [0,0,0,0,2,2,2,2],
              [0,0,0,0,2,2,2,2]])


rel_widths = np.ones(8)/8
rel_heights = np.ones(4)/4

width = 10
height = 8
dpi = 300

info_dict = {}

info_dict[0] = dict(full_size = (5.0,4.0),
                    start = (0.0,4.0))
info_dict[1] = dict(full_size = (2.5,4.0),
                    start = (0.0,0.0))
info_dict[2] = dict(full_size = (5.0,4.0),
                    start = (5.0,4.0))
info_dict[3] = dict(full_size = (2.5,4.0),
                    start = (2.5,0.0))

grobs = [p0,p1,p2,p3]

full_width = width * dpi
full_height = height * dpi

full_width_pt = str(int(width * 72 * 3/4))+"pt"
full_height_pt = str(int(height * 72 * 3/4))+"pt"

# functions -----------


def gg_to_png(gg,
           width,
           height,
           dpi,
           limitsize=True):
    """
    Convert plotnine ggplot figure to PIL Image and return it

    Arguments
    ---------
    gg: plotnine.ggplot.ggplot
        object to save as a png image
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
    PIL.Image coversion of the ggplot object

    Details
    -------
    Associated with the stackoverflow question here: https://stackoverflow.com/questions/8598673/how-to-save-a-pylab-figure-into-in-memory-file-which-can-be-read-into-pil-image/8598881
    """

    buf = io.BytesIO()
    gg.save(buf, format= "png", height = height, width = width,
            dpi=dpi, units = "in", limitsize = limitsize,verbose=False)#, # TODO: figure out how to deal with verbosity....
            #bbox_inches=None, tight_layout=True)
    # https://github.com/has2k1/plotnine/blob/9fbb5f77c8a8fb8c522eb88d4274cd2fa4f8dd88/plotnine/ggplot.py#L684
    buf.seek(0)
    img = Image.open(buf)
    return img


def val_range(x):
    return (np.min(x), np.max(x))

# https://kavigupta.org/2019/05/18/Setting-the-size-of-figures-in-matplotlib/
#^ this is because plotnine is using bbox_inches instead of of tight_layout (I tried to force tight_layout but the way plotnine does titles, etc. is different than base matplotllib so this messes it up)
from matplotlib.image import imread
from tempfile import NamedTemporaryFile

def my_get_size_png(gg, height, width, dpi, limitsize):
    """
    Get actual size of ggplot image saved (with bbox_inches="tight")
    """
    buf = io.BytesIO()
    gg.save(buf, format= "png", height = height, width = width,
            dpi=dpi, units = "in", limitsize = limitsize,verbose=False,
            bbox_inches="tight")
    buf.seek(0)
    img = Image.open(buf)
    width, height = img.size
    return width / dpi, height / dpi

def get_size(fig, dpi=100):
    with NamedTemporaryFile(suffix='.png') as f:
        fig.savefig(f.name, bbox_inches='tight', dpi=dpi)
        height, width, _channels = imread(f.name).shape
        return width / dpi, height / dpi

def my_set_size_png(gg, height, width, dpi, limitsize=True,
                    eps=1e-2, give_up=2, min_size_px = 10):
    """
    interative procudure to find acceptable height & width with bbox_inches='tight'
    """
    # starting at desired values (a reasonsable starting values)
    desired_width, desired_height = width, height
    current_width, current_height = width, height

    deltas = [] # how far we have

    while True:
        actual_width, actual_height = my_get_size_png(gg = gg,
                                                      height = current_height,
                                                      width = current_width,
                                                      dpi = dpi,
                                                      limitsize = limitsize)
        current_width *= desired_width / actual_width
        current_height *= desired_height / actual_height
        deltas.append(abs(actual_width - desired_width) + \
                      abs(actual_height - desired_height))
        if deltas[-1] < eps:
            return current_width, current_height, True
        if len(deltas) > give_up and sorted(deltas[-give_up:]) == deltas[-give_up:]:
            raise StopIteration("unable to get correct size within epsilon and number of interations")
        if current_width * dpi < min_size_px or current_height * dpi < min_size_px:
            raise ValueError("height or width is too small for acceptable image")
        #pdb.set_trace()
    return width, height, False # if errors are suppressed...

def set_size(fig, size, dpi=100, eps=1e-2, give_up=2, min_size_px=10):
    target_width, target_height = size
    set_width, set_height = target_width, target_height # reasonable starting point
    deltas = [] # how far we have
    while True:
        fig.set_size_inches([set_width, set_height])
        actual_width, actual_height = get_size(fig, dpi=dpi)
        set_width *= target_width / actual_width
        set_height *= target_height / actual_height
        deltas.append(abs(actual_width - target_width) + abs(actual_height - target_height))
        if deltas[-1] < eps:
            return True
        if len(deltas) > give_up and sorted(deltas[-give_up:]) == deltas[-give_up:]:
            return False
        if set_width * dpi < min_size_px or set_height * dpi < min_size_px:
            return False

# scaled to fill -----------------

base_rgba = (0,0,0,0)

base_image = Image.new("RGBA", (full_width, full_height), base_rgba)

sizes = []
expected_sizes = []

for p_idx in np.arange(4, dtype = int):
    #print(p_idx)

    inner_width_in, inner_height_in = info_dict[p_idx]["full_size"]
    inner_width, inner_height = [int(val*dpi) for val in info_dict[p_idx]["full_size"]]
    c_start, r_start = [int(np.floor(val*dpi)) for val in info_dict[p_idx]["start"]]

    correct_width_in, \
        correct_height_in, _ = my_set_size_png(gg=grobs[p_idx],
                                               height=inner_height_in,
                                               width=inner_width_in,
                                               dpi=dpi, give_up=2)
    inner_png = gg_to_png(grobs[p_idx],
                          width = correct_width_in,
                          height = correct_height_in,
                          dpi = dpi,
                          limitsize = True)
    sizes.append(inner_png.size)
    expected_sizes.append((inner_width, inner_height))

    inner_png_scale = inner_png.resize((inner_width, inner_height))
    #inner_png_array = np.array(inner_png)

    #c_end = int(c_start + np.ceil(inner_width))
    #r_end = int(r_start + np.ceil(inner_height))

    #inner_image = Image.froma
    base_image.paste(inner_png_scale, (c_start, r_start))





