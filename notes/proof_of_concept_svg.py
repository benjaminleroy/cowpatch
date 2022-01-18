# super basic tests / exploration

import numpy as np
import pandas as pd
import plotnine as p9
import svgutils.transform as sg
import io
import os
import re

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


def gg_to_svg(gg, width, height, dpi, limitsize=True):
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



def transform_size(size):
    """
    takes string with unit and converts it to a float w.r.t pt

    Argument
    --------
    size : string tuple
        tuple of strings with size of svg image 

    Return
    ------
    tuple of floats of sizes w.r.t pt
    """
    value = [float(re.search(r'[0-9\.+]+', s).group()) for s in size]
    
    if size[0].endswith("pt"):
       return (value[0], value[1])
    elif size[0].endswith("in"):
        return (value[0]/72, value[1]/72)
    else:
        raise ValueError("size structure of object not as expected, "+\
                         "new size type")


def proposed_scaling_both(current, desired):
    """
    identify a single scalar to scale the image by so that
    it is closer to the desired scaling (fills the space as much as possible)

    Arguments
    ---------
    current : tuple
        float tuple of current size of svg object
    desired : tuple
        float tuple of desired size of svg object

    Returns
    -------
    float
        constant scalar for size change
    """
    scale_x = desired[0]/current[0]
    scale_y = desired[1]/current[1]

    return scale_x, scale_y



def find_left_corner(lc_raw, box_size, actual_size,
                     vjust=1,
                     hjust=.5):
    """

    Arguments
    ---------
    lc_raw : tuple
        float tuple of left corner of box
    box_size: tuple
        float tuple of box size for svg object
    actual_size: tuple
        float tuple of actual size of svg object
    vjust: float
        between 0 and 1, amount of shift vertically within box
    hjust: float
        between 0 and 1, amount of shift horizontally within box

    """
    assert np.all(box_size >= actual_size), \
        "actual size is larger than box size, please correct"

    width_diff = box_size[0]-actual_size[0]
    height_diff = box_size[1]-actual_size[1]

    lc_out = (hjust * width_diff + lc_raw[0],
              vjust * height_diff + lc_raw[1])

    return lc_out

def my_get_size_svg(gg, height, width, dpi, limitsize):
    """
    Get actual size of ggplot image saved (with bbox_inches="tight")
    """
    fid = io.StringIO()

    try:
        gg.save(fid, format= "svg", height = height, width = width,
            dpi=dpi, units = "in", limitsize = limitsize, verbose=False) # TODO check why they have this naming...
    except ValueError:
        rasie(ValueError, "No ggplot SVG backend")
    fid.seek(0)
    img = sg.fromstring(fid.read())

    new_width, new_height = transform_size(img.get_size())

    return new_width / 72, new_height / 72 # this does it for inches...


def my_set_size_svg(gg, height, width, dpi, limitsize=True,
                    eps=1e-2, give_up=2, min_size_px = 10):
    """
    interative procudure to find acceptable height & width with bbox_inches='tight'
    """
    # starting at desired values (a reasonsable starting values)
    desired_width, desired_height = width, height
    current_width, current_height = width, height

    deltas = [] # how far we have
    while True:
        actual_width, actual_height = my_get_size_svg(gg = gg,
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
        elif len(deltas) > give_up:#and sorted(deltas[-give_up:]) == deltas[-give_up:]:
            raise StopIteration("unable to get correct size within epsilon and number of interations")
        elif current_width * dpi < min_size_px or current_height * dpi < min_size_px:
            raise ValueError("height or width is too small for acceptable image")
    return width, height, False # if errors are suppressed...

# scaled to fill -----------------

base_image = sg.SVGFigure()
base_image.set_size((full_width_pt, full_height_pt))
#^ TODO: this size is somehow wrong... maybe it's expecting a different size structure or the rest is...
base_image.append(sg.fromstring("<rect width=\"100%\" height=\"100%\" fill=\"#BDBDBD\"/>"))



svg_sizes = []
svg_desired_sizes = []



for p_idx in np.arange(4, dtype = int):
    print(p_idx)
    inner_width_in, inner_height_in = info_dict[p_idx]["full_size"]
    inner_width, inner_height = [int(val*dpi) for val in info_dict[p_idx]["full_size"]]
    c_start, r_start = [int(np.floor(val*dpi)) for val in info_dict[p_idx]["start"]]

    correct_width_in, \
        correct_height_in, _ = my_set_size_svg(gg=grobs[p_idx],
                                               height=inner_height_in,
                                               width=inner_width_in,
                                               dpi=dpi, give_up=4)

    svg = gg_to_svg(grobs[p_idx],
                          width = correct_width_in,
                          height = correct_height_in,
                          dpi = dpi)

    current_size_raw = svg.get_size()
    current_size = transform_size(current_size_raw)
    desired_size_raw = [str(v * 72)+"pt" for v in info_dict[p_idx]["full_size"]]
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

    inner_lc_raw =(info_dict[p_idx]["start"][0] * 72,
                    info_dict[p_idx]["start"][1] * 72)

    # lc_raws.append(inner_lc_raw)

    new_lc = inner_lc_raw

    inner_root.moveto(x=new_lc[0],
                      y=new_lc[1])
    # thought scale to fit desired location, then center?
    base_image.append(inner_root)


base_image.save("size_correction.svg")




