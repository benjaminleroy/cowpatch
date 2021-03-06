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
height = 6
dpi = 300

info_dict = {}

info_dict[0] = dict(full_size = (5.0,3.0),
                    start = (0.0,3.0))
info_dict[1] = dict(full_size = (2.5,3.0),
                    start = (0.0,0.0))
info_dict[2] = dict(full_size = (5.0,3.0),
                    start = (5.0,3.0))
info_dict[3] = dict(full_size = (2.5,3.0),
                    start = (2.5,0.0))

grobs = [p0,p1,p2,p3]

full_width = width * dpi
full_height = height * dpi

full_width_pt = str(int(width * 72 * 3/4))+"pt"
full_height_pt = str(int(height * 72 * 3/4))+"pt"


# functions -------------

# from proof_of_concept_text_svg.py


# TODO: make sure the cowplot processes autogenerated labels to left and a
# certain size... (maybe worthwhile to make the default be from `legend_text`
# but it's kinda odd that the default will likely not be what we want...)
# does this break the value in using the element_text / theme direction to
# define property attributes?
#
# for labels in plots should we makea "label_text" attribute and populate it
# with some desirable defaults?
#
# could make label_text as subclass...
#
# also would allow for non-default margins of 0
# default margin: https://stackoverflow.com/questions/13127887/how-wide-is-the-default-body-margin

def to_pt(value, units, dpi=96):
    """
    convert length from given units to pt

    Arguments
    ---------
    value : float
        length in measurement units
    units : str
        unit type (e.g. "pt", "px", "in", "cm", "mm")
    dpi : float / int
        dots per inch (conversion between inches and px)

    Return
    ------
    length in pt
    """
    if units == "pt":
        return value

    # metric to inches
    if units == "cm":
        value = value/2.54
        unit = "in"

    if units == "mm":
        value = value/25.4
        units = 'in'

    # inches to pixels
    if units == "in" or units == "inches":
        value = value * dpi
        units = "px"

    # pixel to pt
    if units == "px":
        value = value * .75
        return value

def from_pt(value, units, dpi=96):
    """
    convert length from pt to given units

    Arguments
    ---------
    value : float
        length in measurement units
    units : str
        unit type (e.g. "pt", "px", "in", "cm", "mm")
    dpi : float / int
        dots per inch (conversion between inches and px)

    Return
    ------
    length given units
    """
    if units == "pt":
        return value

    # metric to inches
    if units == "cm":
        value = value * 2.54
        units = "in"

    if units == "mm":
        value = value * 25.4
        units = 'in'

    # inches to pixels
    if units == "in" or units == "inches":
        value = value / dpi
        units = "px"

    # pt to px
    if units == "px":
        value = value * 4/3
        return value

class text:
    def __init__(self, label, element_text=None, theme=None):
        """
        create a new text object

        Arguments
        ---------
        label : string
            text label with desirable format (e.g. sympy, etc.)
        element_text : plotnine.themes.elements.element_text
            element object from plotnine, can also be added later
        theme : plotnine.theme object
            theme object from plotnine, can be associated later
            should only provide a theme or element_text (as a theme
            contains an element_text)
        default_margin : boolean



        Details
        -------
        This class leverages matplotlib to create the text (given that
        matplotlib can create path-style objects for text if the individual
        is worried that the svg text visually won't be preserved - this is also
        annoying that this is the default).

        Note the function use the ``text`` attribute - NOT the
        ``plot_title`` attribute if a theme is provided.
        """
        self.label = label

        if element_text is not None and theme is not None:
            raise ValueError("please provide only a theme or element_text, "+\
                             "not both")
        self.element_text = None # prep initialization
        self._init_element_text(element_text)
        self.theme = theme

    def _init_element_text(self, element_text):
        """
        make sure it's a themeable else create one

        updates is place!

        """
        if element_text is None:
            element_text = None

        if isinstance(element_text, p9.themes.elements.element_text):
            et_themeable = p9.theme(text = element_text
                                    ).themeables.get("text")
            element_text = et_themeable
        else:
            element_text = element_text

        if self.element_text is not None:
            self.element_text.merge(element_text)
        else:
            self.element_text = element_text


        return None # just a reminder

    def __add__(self, other):
        """
        add element_text or theme to update format

        Arguments
        ---------
        other : plotnine.themes.elements.element_text or theme
            theme or element_text to define the attributes of the text.

        Details
        -------
        Note the function use the ``text`` attribute - NOT the ``plot_title``
        attribute if a theme is provided.
        """

        if not isinstance(other, p9.themes.themeable.element_text) and \
           not isinstance(other, p9.theme):
            raise ValueError("text objects are only allowed to be combined "+\
                             "with element_text objects.")
        # need to update theme or element_text...
        if isinstance(other, p9.themes.themeable.element_text):
            self._init_element_text(other)

            # update theme if it already exists
            # (if not we'll update it when it's required)
            if self.theme is not None:
                self.theme += p9.theme(text = self.element_text.theme_element)

        if isinstance(other, p9.theme):
            if self.theme is None:
                self.theme = other
            else:
                self.theme.add_theme(other)

                new_element_text = self.theme.themeables.get("text")
                self._init_element_text(new_element_text)
        return self

    def _provide_complete_theme(self):
        """
        It should be here that the current global theme is accessed, and thing are completed...
        """
        if self.theme is None:
            current_theme = p9.theme_get()
            # and update with our element_text
            if self.element_text is not None:
                # problem here... (need to update themeable.get("text") instead)
                current_theme += p9.theme(text=self.element_text.theme_element)
        else:
            current_theme = self.theme

        return current_theme

    def _inner_prep(self):
        """
        Internal function to create matplotlib figure with text and
        provide a bounding box for the location in the plot

        Returns
        -------
        fig : matplotlib.figure.Figure
            figure with text at (0,0), no axes
        bbox : matplotlib.transforms.Bbox
            bbox location of text in figure
        """

        # apply theme/element_text correctly ------

        # mirrors code in p9.ggplot.draw_title() and
        #  p9.themeable.plot_title.apply_figure()
        # code references:
        # - https://github.com/has2k1/plotnine/blob/9fbb5f77c8a8fb8c522eb88d4274cd2fa4f8dd88/plotnine/ggplot.py#L545
        # - https://github.com/has2k1/plotnine/blob/6c82cdc20d6f81c96772da73fc07a672a0a0a6ef/plotnine/themes/themeable.py#L361
        #

        # collect desirable theme and properties --------
        theme = self._provide_complete_theme()

        text_themeable = theme.themeables.get('text')
        properties = text_themeable.properties.copy()


        # create text and apply ----------
        # https://stackoverflow.com/questions/24581194/matplotlib-text-bounding-box-dimensions

        fig, ax = plt.subplots()
        fig.set_dpi(96)
        txt = fig.text(x=0.000, y=0.000, s=self.label)
        with suppress(KeyError):
            del properties['margin']
        with suppress(KeyError):
            txt.set(**properties)

        bbox = txt.get_window_extent(fig.canvas.get_renderer())

        # remove background structure from mpl ----------
        # help from: https://stackoverflow.com/questions/21687571/matplotlib-remove-patches-from-figure
        fig.axes.pop()
        plt.axis('off')

        # bbox aids in cutting all but the desired image

        return fig, bbox


    def _create_svg_object(self, width=None, height=None):
        """
        Internal to create svg object (with text in correct location
        and correct image size)

        Arguments
        ---------
        width : float
            width of desired output (in inches)
        height : float
            height of desired output (in inches)

        Returns
        -------
        svg_obj : svgutils.transform.SVGFigure
            svg representation of text with correct format and image size
        """

        fig, bbox = self._inner_prep()

        if width is not None:
            width = to_pt(width, "in")
        if height is not None:
            height = to_pt(height, "in")


        # get original matplotlib image ------------
        fid = io.StringIO()
        fig.savefig(fid, bbox_inches=fig.bbox_inches, format='svg')
        fid.seek(0)
        image_string = fid.read()
        img = sg.fromstring(image_string)
        img_size = transform_size((img.width, img.height))
        # location correction for alignment and margins -------

        current_theme = self._provide_complete_theme()
        ha_str = current_theme.themeables.get("text").properties.get("ha")
        va_str = current_theme.themeables.get("text").properties.get("va")
        margin_dict = current_theme.themeables.get("text").properties.get("margin")
        margin_dict_pt = {"t": to_pt(margin_dict["t"], margin_dict["units"]),
                          "b": to_pt(margin_dict["b"], margin_dict["units"]),
                          "l": to_pt(margin_dict["l"], margin_dict["units"]),
                          "r": to_pt(margin_dict["r"], margin_dict["units"])}


        if width is None:
            width = to_pt(bbox.width, 'px') + margin_dict_pt["l"] + margin_dict_pt["r"]

        if height is None:
            height = to_pt(bbox.height, 'px') + margin_dict_pt["t"] + margin_dict_pt["b"]

        if ha_str == "center":
            x_shift = width/2 - to_pt(bbox.width, "px") /2
        elif ha_str == "right":
            x_shift = width - to_pt(bbox.width, "px") - margin_dict_pt["r"]
        else: # ha_str == "left"
            x_shift = margin_dict_pt["l"]


        if va_str == "center":
            y_shift = height/2 - to_pt(bbox.height, "px") /2
        elif va_str == "bottom":
            y_shift = height - to_pt(bbox.height, "px") - margin_dict_pt["b"]
        else: # va_str = "top"
            y_shift = margin_dict_pt["t"]

        # prep translated and smaller canvas image ----------
        # note that bbox coordinates are with respect to a bottom left axis
        # (aka cartesian)
        # and then we need to convert it to svg's top left axis
        svg_bb_top_left_corner = (to_pt(bbox.x0,
                                        units = "px"), # x_min
                                  img_size[1] - to_pt(bbox.y1,
                                        units = "px")) # height - y_max

        new_image_size = (str(width)+"pt",
                          str(height)+"pt")

        # need to declare the viewBox for some reason...
        new_image_size_string_val = [re.sub("pt", "", val)
                                        for val in new_image_size]

        new_viewBox = "0 0 %s %s" % (new_image_size_string_val[0],
                                    new_image_size_string_val[1])

        img_root = img.getroot()
        img_root.moveto(x = -1*svg_bb_top_left_corner[0] + x_shift,
                        y = -1*svg_bb_top_left_corner[1] + y_shift)
        img_root_str = img_root.tostr()


        new_image = sg.SVGFigure()
        new_image.set_size(new_image_size)
        new_image.root.set("viewBox", new_viewBox)


        # remove patch (lxml.etree) ----------
        # img_root2_lxml = etree.fromstring(img_root_str)
        # parent = img_root2_lxml.findall(".//{http://www.w3.org/2000/svg}g[@id=\"patch_1\"]")[0]
        # to_remove = parent.getchildren()[0]
        # parent.remove(to_remove)
        # img_root2_str = etree.tostring(img_root2_lxml)
        # img2 = sg.fromstring(img_root2_str.decode("utf-8"))

        # remove path (xml.etree.ElementTree) ---------
        img_root2_xml = ET.fromstring(img_root_str)
        parent = img_root2_xml.findall(".//{http://www.w3.org/2000/svg}g[@id=\"patch_1\"]")[0]
        to_remove =  img_root2_xml.findall(".//{http://www.w3.org/2000/svg}path")[0]
        parent.remove(to_remove)
        img_root2_xml_str = ET.tostring(img_root2_xml)
        img2 = sg.fromstring(img_root2_xml_str.decode("utf-8"))

        new_image.append(img2)


        # closing plot
        plt.close()

        return new_image


    def save(self, filename, width=None, height=None):
        """
        save text object as image in minimal size object

        Argument
        --------
        filename : str
        width : float
            in inches (if None, then tight (w.r.t. to margins))
        height : float
            in inches (if None, then tight (w.r.t. to margins))
        """

        svg_obj = self._create_svg_object(width=width, height=height)

        svg_obj.save(filename)
        plt.close() # do we need this?

# text objects

label_theme = p9.theme(text =
    p9.element_text(size = 16,
                    margin = {"l":8,
                              "r":8,
                              "b":8,
                              "t":8,
                              "units":"pt"}))

a_text = text(label = "c",
              theme = label_theme)
b_text = text(label = "a",
              theme = label_theme)
c_text = text(label = "d",
              theme = label_theme)
d_text = text(label = "b",
              theme = label_theme)

text_labels = [a_text, b_text, c_text, d_text]
# other functions ------------


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

        # decisions to terminate interation
        if deltas[-1] < eps:
            return current_width, current_height, True
        elif len(deltas) > maxIter:
            raise StopIteration("unable to get correct size within epsilon and number of interations")
        elif current_width * dpi < min_size_px or current_height * dpi < min_size_px:
            raise ValueError("height or width is too small for acceptable image")
    return width, height, False

# scaled to fill -----------------

base_image = sg.SVGFigure()
base_image.set_size((full_width_pt, full_height_pt))
base_image.append(
    sg.fromstring("<rect width=\"100%\" height=\"100%\" fill=\"#FFFFFF\"/>"))
# ^ defining that white is the background



svg_sizes = []
svg_desired_sizes = []


bar = progressbar.ProgressBar()


for p_idx in bar(np.arange(4, dtype = int)):

    # image addition ---------

    inner_width_in, inner_height_in = info_dict[p_idx]["full_size"]
    inner_width, inner_height = [int(val*dpi) for val in info_dict[p_idx]["full_size"]]
    c_start, r_start = [int(np.floor(val*dpi)) for val in info_dict[p_idx]["start"]]

    correct_width_in, \
        correct_height_in, _ = select_correcting_size_svg(gg=grobs[p_idx],
                                                       height=inner_height_in,
                                                       width=inner_width_in,
                                                       dpi=dpi,
                                                       maxIter=4)

    svg = gg_to_svg(grobs[p_idx],
                    width=correct_width_in,
                    height=correct_height_in,
                    dpi=dpi)

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

    # text addition --------
    if True:
        # ^ currently text svg still has patch_1 (which is messing up image)
        # could we just removing it directly?
        # https://stackoverflow.com/questions/49959111/svg-file-remove-element

        inner_text = text_labels[p_idx]

        svg_text = inner_text._create_svg_object()
        svg_text_root = svg_text.getroot()
        svg_text_root.moveto(x=new_lc[0],
                              y=new_lc[1])

        base_image.append(svg_text_root)



base_image.save("size_correction_text_added.svg")


# file saving ----------


# use cairosvg to convert to pdf, png, ps
# todo: figure out how to correctly pass inches parameter (also if we allow
# for different measurement types we need to pass everything all the way through)
# plotnine seems to do "to_inches(width, units)" -> could we try something like that?
# https://github.com/has2k1/plotnine/blob/9fbb5f77c8a8fb8c522eb88d4274cd2fa4f8dd88/plotnine/ggplot.py#L701

# use PIL to obtain raster images (jpg, jpeg)...


base_image_string = base_image.to_str()

file_options = ["pdf", "png", "ps", "eps", "jpg", "jpeg"]

# should mirror ideas in https://github.com/has2k1/plotnine/blob/9fbb5f77c8a8fb8c522eb88d4274cd2fa4f8dd88/plotnine/ggplot.py#L646
# ^ plotnine's save function (has a filename,and format information)

# cairosvg direct -------------


cairosvg.svg2pdf(bytestring = base_image_string,
                 write_to = "size_correction_and_text.pdf",
                 output_width = width * 96,
                 output_height = height * 96)



png_dpi = 96 # to alter dpi we need to have a viewbox...
# looks like we don't actually have one (and weirdly units look like they're in
# px not pt... (annoying)
# as such, we need to first add a viewbox like so:
#  width="540pt" height="432pt" viewBox="0 0 718 576"
# then to change size we change the "width" and "height" parameters by
# png_dpi / 96 multiple.

# then save it?





cairosvg.svg2png(bytestring = base_image_string,
                 write_to = "size_correction_and_text.png",
                 output_width = width * 96,
                 output_height = height * 96) # I'm not sure how to make this better... (could we do raster with png and vector with svg?)

cairosvg.svg2png(bytestring = base_image_string,
                 write_to = "size_correction_and_text_scaled.png",
                 scale = 2)

cairosvg.svg2ps(bytestring = base_image_string,
                write_to = "size_correction_and_text.ps",
                output_width = width * 96,
                output_height = height * 96)

cairosvg.svg2eps(bytestring = base_image_string,
                 write_to = "size_correction_and_text.eps")


# cairosvg + PIL ----------------
# png to jpg/ jpeg + others?

# https://github.com/manatools/dnfdragora/blob/0a8a39b85f670207ef1870da63a08e9012dac88e/dnfdragora/updater.py#L178
fid = io.BytesIO()
out_bytes = cairosvg.svg2png(bytestring = base_image_string,
                 write_to = fid,
                 output_width = width * 96,
                 output_height = height * 96)
img_png = Image.open(io.BytesIO(fid.getvalue()))
img_png.save('size_correction_and_text.jpg')
img_png.save('size_correction_and_text.jpeg')



# showing image... -------------

if False:
    fid = io.BytesIO()
    out_bytes = cairosvg.svg2png(bytestring = base_image_string,
                     write_to = fid,
                     output_width = width * 96,
                     output_height = height * 96)
    img_png = Image.open(io.BytesIO(fid.getvalue()))
    img_png.show()





# thinking about transparencies with jpeg, etc.... ---------

# to get transparencies - transparent=True? https://matplotlib.org/2.0.2/api/figure_api.html?highlight=savefig#matplotlib.figure.Figure.savefig

# next steps / things to demo --------------------

## https://wilkelab.org/cowplot/articles/drawing_with_on_plots.html
# insert plots + images all over the place? do we need to think about such things?
# maybe inserts but nothing more?








# image saving wrapper ----------

_file_options = ["pdf", "png", "ps", "eps", "jpg", "jpeg", "svg"]


def save_svg_wrapper(svg, filename, width, height, dpi=300, format=None):
    """
    save svg object to a range of different file names

    Arguments
    ---------
    svg: svgutils.transform.SVGFigure
        svg object to save
    filename : str
        local string to save the file to (this can also be at least io.BytesIO)
    width : float
        width of output image in inches (this should actually be associated
        with the svg...)
    height : float
        height of svg in inches (this should actually be associated
        with the svg...)
    dpi : int or float
        dots per square inch, default is 300
    format : str
        string of format (error tells options). If provided this is the format
        used, if None, then we'll try to use the filename extension.

    Returns
    -------
    None
        saves to a file

    TODO: default width and height somewhere? also width and height are in inches (also it's directly associated with the svg object...)
    """

    if format is None:
        dot_ending = re.findall("\\..+$", filename)[0]
        format = re.sub("\\.", "", dot_ending)

    format = format.lower()

    if format not in _file_options:
        raise ValueError("format / end of file name must be one of\n{}".format(_file_options))

    if format == "svg":
        svg.save(filename)
    elif format == "pdf":
        base_image_string = svg.to_str()
        cairosvg.svg2pdf(bytestring = base_image_string,
                 write_to = filename,
                 output_width = width * 96,
                 output_height = height * 96)
    elif format == "ps":
        base_image_string = svg.to_str()
        cairosvg.svg2ps(bytestring = base_image_string,
                        write_to = filename,
                        output_width = width * 96,
                        output_height = height * 96)
    elif format == "eps":
        base_image_string = svg.to_str()
        cairosvg.svg2eps(bytestring = base_image_string,
                         write_to = filename,
                         output_width = width * 96,
                         output_height = height * 96)
    else: # raster
        base_image_string = svg.to_str()

        if dpi != 96:
            scale = dpi / 96
        else:
            scale = 1

        if format == "png":
            cairosvg.svg2png(bytestring = base_image_string,
                 write_to = filename, scale = scale,
                 output_width = width * 96 * scale,
                 output_height = height * 96 * scale)
        elif format == "jpeg" or format == "jpg":
            fid = io.BytesIO()
            out_bytes = cairosvg.svg2png(bytestring = base_image_string,
                                         write_to = fid,
                                         scale = scale,
                                         output_width = width * 96 * scale,
                                         output_height = height * 96 * scale)
            img_png = Image.open(io.BytesIO(fid.getvalue()))
            img_png.save(filename)

# tests of saving_svg_wrapper --------


save_svg_wrapper(base_image,
                 filename = "size_correction_and_text2.svg",
                 width = width,
                 height = height)

save_svg_wrapper(base_image,
                 filename = "size_correction_and_text2.pdf",
                 width = width,
                 height = height)

save_svg_wrapper(base_image,
                 filename = "size_correction_and_text2.ps",
                 width = width,
                 height = height)

save_svg_wrapper(base_image,
                 filename = "size_correction_and_text2.eps",
                 width = width,
                 height = height)

save_svg_wrapper(base_image,
                 filename = "size_correction_and_text2.png",
                 width = width,
                 height = height)


save_svg_wrapper(base_image,
                 filename = "size_correction_and_text2.jpg",
                 width = width,
                 height = height)

save_svg_wrapper(base_image,
                 filename = "size_correction_and_text2.jpeg",
                 width = width,
                 height = height)


from IPython.display import SVG, display
import IPython

def show_image(svg, width, height, dpi = 300):
    """
    display svg object as a png

    Arguments
    ---------
    svg: svgutils.transform.SVGFigure
        svg object to save
    width : float
        width of output image in inches (this should actually be associated
        with the svg...)
    height : float
        height of svg in inches (this should actually be associated
        with the svg...)

    Returns
    -------
    None
        shows svg object as a png (with provided width + height + dpi)
    """

    ipython_info = IPython.get_ipython()

    if ipython_info is None or ipython_info.config.get("IPKernelApp") is None:
        # base python or ipython in the terminal will just show png ----------
        fid = io.BytesIO()
        save_svg_wrapper(svg, filename = fid,
                          width = width,
                          height = height,
                          dpi = dpi,
                          format = "png")
        img_png = Image.open(io.BytesIO(fid.getvalue()))

        img_png.show()
    else:
        # jupyter notebook ------
        base_image_string = svg.to_str()
        IPython.display.display(IPython.display.SVG(data = base_image_string))


if False:
    show_image(base_image,
               width = width,
               height = height)





