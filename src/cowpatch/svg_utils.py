import io
import plotnine as p9
import cairosvg
import svgutils.transform as sg
from PIL import Image
import warnings
from .exceptions import CowpatchWarning

import re
from IPython.display import SVG, display
import IPython

from .utils import _transform_size_to_pt, _proposed_scaling_both, \
                    to_inches, from_inches

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import numpy as np
import copy

import pdb

def _raw_gg_to_svg(gg, width, height, dpi, limitsize=True):
    """
    Convert plotnine ggplot figure to svg and return it (pass width, height
    directly to p9.save, no correction to incorrect saving)

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

    Notes
    -----
    Code idea motified by the stackoverflow question here, https://stackoverflow.com/questions/8598673/how-to-save-a-pylab-figure-into-in-memory-file-which-can-be-read-into-pil-image/8598881
    and truly influenced by svgutils.transform.from_mpl function.
    """

    fid = io.StringIO()

    try:
        gg.save(fid, format="svg", height=height, width=width,
            dpi=dpi, units="in", limitsize=limitsize, verbose=False)
    except ValueError:
        raise(ValueError, "No ggplot SVG backend")
    fid.seek(0)
    img = sg.fromstring(fid.read())

    return img

def _real_size_out_svg(gg, height, width, dpi, limitsize=True):
    """
    Calculate the output size for a plotnine.ggplot object saving as an
    svg

    Notes
    -----
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
    img = _raw_gg_to_svg(gg,
                         height=height,
                         width=width,
                         dpi=dpi, limitsize=limitsize)
    # TODO: transform this to getting inches right away?
    new_width, new_height = _transform_size_to_pt(img.get_size())

    return to_inches(new_width, "pt", dpi), to_inches(new_height, "pt", dpi)

def _select_correcting_size_svg(gg, height, width, dpi, limitsize=True,
                    eps=1e-2, maxIter=20, min_size_px=10, throw_error=True):
    """
    Obtain the correct input saving size plotnine.ggplot object to actual
    obtain desired height and width (inches)

    Notes
    -----
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
    throw_error : boolean
        logic if an error should be thrown if the convergence fails. If False,
        then this will return ratios of width_requested/width_obtained,
        height_requested/height_obtained, and a boolean = False.

    Returns
    -------
    tuple
        if the process converges successful, it will return a three value
        tuple of a width and height to provide desired measures and a
        boolean value (True). if process fails to converge, either this
        functions raises an error (if throw_error is True), or a three value
        tuple of a scaled width_requested/width_obtained,
        height_requested/height_obtained, and a boolean value (False).
    """
    # starting at desired values (a reasonsable starting values)
    desired_width, desired_height = width, height
    current_width, current_height = width, height

    deltas = [] # how close we've gotten
    while True:
        actual_width, actual_height = _real_size_out_svg(gg=gg,
                                                        height=current_height,
                                                        width=current_width,
                                                        dpi=dpi,
                                                        limitsize=limitsize)
        current_width *= desired_width / actual_width
        current_height *= desired_height / actual_height
        deltas.append(abs(actual_width - desired_width) +
                      abs(actual_height - desired_height))

        # decisions to terminate interation
        if deltas[-1] < eps:
            return current_width, current_height, True
        elif len(deltas) > maxIter:
            error_str = "unable to get correct size within "+\
                                "epsilon and number of interations"
            break
        elif current_width * dpi < min_size_px or \
            current_height * dpi < min_size_px:
            error_str = "height or width is too small for "+\
                             "acceptable image"
            break

    if throw_error:
        raise StopIteration(error_str)
    else:
        actual_width, actual_height = _real_size_out_svg(gg=gg,
                                            height=desired_height,
                                            width=desired_width,
                                            dpi=dpi,
                                            limitsize=limitsize)
        return desired_width/actual_width, \
            desired_height/actual_height, \
            False

def gg_to_svg(gg, width, height, dpi, limitsize=True,
              eps=1e-2, maxIter=20, min_size_px=10):
    """
    Convert plotnine ggplot figure to svg and return it (with close to perfect
    sizing).

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
    svgutils.tranform representation of the ggplot object
        (aka an svg representation)

    Notes
    -----
    Code idea motified by the stackoverflow question here, https://stackoverflow.com/questions/8598673/how-to-save-a-pylab-figure-into-in-memory-file-which-can-be-read-into-pil-image/8598881
    and truly influenced by svgutils.transform.from_mpl function.
    """
    correct_width_in, \
        correct_height_in, _ = _select_correcting_size_svg(gg=gg,
                                                       height=height,
                                                       width=width,
                                                       dpi=dpi,
                                                       limitsize=limitsize,
                                                       maxIter=maxIter,
                                                       eps=eps,
                                                       min_size_px=min_size_px)

    svg = _raw_gg_to_svg(gg,
                    width=correct_width_in,
                    height=correct_height_in,
                    dpi=dpi)

    current_size_raw = svg.get_size()
    current_size = _transform_size_to_pt(current_size_raw)
    desired_size_raw = (str(from_inches(width, "pt",dpi))+"pt",
                        str(from_inches(height, "pt",dpi))+"pt")
    desired_size = _transform_size_to_pt(desired_size_raw)

    scale = _proposed_scaling_both(current_size, desired_size)

    inner_root = svg.getroot()
    inner_root.moveto(x=0,y=0,scale_x=scale[0], scale_y=scale[1])

    scaled_svg = sg.SVGFigure()
    scaled_svg.set_size((str(current_size[0]*scale[0])+"pt",
                      str(current_size[1]*scale[1])+"pt"))

    scaled_svg.append(inner_root)
    scaled_size_raw = scaled_svg.get_size()

    return scaled_svg

def _raw_mpt_to_svg(fig, ax, width, height, dpi):
    """
    ... taken from proof_of_concept_wrapper's fa_encapsulate
    """

    # preserve fig.figsize attribute after processing
    base_figsize = fig.get_size_inches()


    self.fig.set_size_inches((width, height))

    fid = io.StringIO()
    self.fig.savefig(fid, format="svg")
    fid.seek(0)
    image_string = fid.read()
    img = sg.fromstring(image_string)

    # preserve fig.figsize attribute after processing
    if base_figsize is not None:
        self.fig.set_size_inches(base_figsize)

    return img

def mpt_to_svg(gg, width, height, dpi):
    # need to make wrapping to deal with sizing like we did for gg_to_svg...
    #
    # we also need to think about the default figsize and how to incorporate it
    # if width and height aren't defined (does that belong here.)
    raise ValueError("Todo: impliment")

_file_options = ["pdf", "png", "ps", "eps", "jpg", "jpeg", "svg"]

def _save_svg_wrapper(svg, filename, width, height, dpi=300,
                      _format=None, verbose=True):
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
    _format : str
        string of format (error tells options). If provided this is the format
        used, if None, then we'll try to use the filename extension.
    verbose : bool
            If `True`, print the saving information.

    Returns
    -------
    None
        saves to a file
    """

    # format checking
    if _format is None:
        dot_ending = re.findall("\\..+$", filename)[0]
        _format = re.sub("\\.", "", dot_ending)

    _format = _format.lower()

    if _format not in _file_options:
        raise ValueError("format / end of file name must be one of\n{}".format(_file_options))

    # verbosity
    if verbose:
        warnings.warn("Saving {0:,.2g} x {1:,.2g} inch image.".format(
             width, height), CowpatchWarning)
        warnings.warn('Filename: {}'.format(filename), CowpatchWarning)



    if _format == "svg":
        svg.save(filename)
    elif _format == "pdf":
        base_image_string = svg.to_str()
        cairosvg.svg2pdf(bytestring=base_image_string,
                 write_to=filename,
                 output_width=width * 96,
                 output_height=height * 96)
    elif _format == "ps":
        base_image_string = svg.to_str()
        cairosvg.svg2ps(bytestring=base_image_string,
                        write_to=filename,
                        output_width=width * 96,
                        output_height=height * 96)
    elif _format == "eps":
        base_image_string = svg.to_str()
        cairosvg.svg2eps(bytestring=base_image_string,
                         write_to=filename,
                         output_width=width * 96,
                         output_height=height * 96)
    else: # raster
        base_image_string = svg.to_str()

        if dpi != 96:
            scale = dpi / 96
        else:
            scale = 1

        if _format == "png":
            cairosvg.svg2png(bytestring=base_image_string,
                 write_to=filename, scale=scale,
                 output_width=width * 96 * scale,
                 output_height=height * 96 * scale)
        elif _format == "jpeg" or _format == "jpg":
            fid = io.BytesIO()
            out_bytes = cairosvg.svg2png(bytestring=base_image_string,
                                         write_to=fid,
                                         scale=scale,
                                         output_width=width * 96 * scale,
                                         output_height=height * 96 * scale)
            img_png = Image.open(io.BytesIO(fid.getvalue()))
            img_png.save(filename)

def _show_image(svg, width, height, dpi=300, verbose=True):
    """
    display svg object for user (either run from command line or jupyter
    notebook)

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
        shows svg object (with provided width + height + dpi)

    Note
    ----
    If run from the command line, the image will be presented using matplotlib's
    plotting tool with a png representation of the object. If run within a
    jupyter notebook, the object will leverage ipython's internal svg presenter
    to present the object as real svg object. Both approaches do not allow for
    resizing of the image and seeing the image correct itself to the new size,
    which is a bummer for command line usage.
    """

    if verbose:
        warnings.warn("Showing {0:,.2g} x {1:,.2g} inch image.".format(
             width, height), CowpatchWarning)

    ipython_info = IPython.get_ipython()

    if ipython_info is None or ipython_info.config.get("IPKernelApp") is None:
        # base python or ipython in the terminal will just show png ----------
        fid = io.BytesIO()
        _save_svg_wrapper(svg, filename = fid,
                          width = width,
                          height = height,
                          dpi = dpi,
                          _format = "png",
                          verbose=False)
        img = mpimg.imread(io.BytesIO(fid.getvalue()))

        fig, ax = plt.subplots(figsize=(width, height))
        ax.imshow(img)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
    else:
        # jupyter notebook ------
        base_image_string = svg.to_str()
        IPython.display.display(IPython.display.SVG(data = base_image_string))



def _uniquify_svg_safe(svg_obj, str_update):
    """
    Update svg code to 'uniquify' svg but by making sure 'url(#___)'

    Arguments
    ---------
    svg_obj : svg object
        svg object, svgutils.transform.SVGFigure
    str_update : str
        string addition for ids (required to include '_' if desired it)

    Return
    ------
    svg_obj : svg object
        updated svg object, svgutils.transform.SVGFigure


    Details
    -------
    Internally this function calls "_uniquify_svg_str_safe" for
    the vast majority of the heavy lifting
    """

    # string collection
    inner_svg = copy.deepcopy(svg_obj)
    svg_str = str(inner_svg.to_str())

    # updating string
    updated_svg_str = _uniquify_svg_str_safe(svg_str, str_update=str_update)

    # need to identify start and end of svg to re-convert it to and svg_object
    start = re.search("<svg", updated_svg_str)
    end = re.search("</svg>", updated_svg_str)

    updated_end_svg = sg.fromstring(updated_svg_str[start.start():end.end()])

    return updated_end_svg

def _uniquify_svg_str_safe(svg_str, str_update):
    """
    Update svg code to 'uniquify' svg but by making sure 'url(#___)'

    Arguments
    ---------
    svg_str : str
        svg string presentation
    str_update : str
        string addition for ids (required to include '_' if desired it)

    Return
    ------
    svg_str : str
        updated svg code
    """

    # identify which ids are linked to "url(#___)" and must be extended
    ids_to_extend = \
        np.unique(
            [re.sub("(url\(\#)|(\))", "", x)
             for x in re.findall("url\(\#[A-Za-z0-9\_]+\)", svg_str)])


    for old_id_name in ids_to_extend:
        new_id_name = old_id_name + str_update
        # id
        svg_str = re.sub("id=\"{0}\"".format(old_id_name),
                       "id=\"{0}\"".format(new_id_name),
                       svg_str)

        # url(#)
        svg_str = re.sub("url\(\#{0}\)".format(old_id_name),
                      "url(#{0})".format(new_id_name),
                       svg_str)

    return svg_str


