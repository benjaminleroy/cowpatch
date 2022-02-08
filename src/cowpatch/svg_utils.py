import io
import plotnine as p9
import cairosvg
import svgutils.transform as sg
from PIL import Image

def _transform_size(size_string_tuple):
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
        gg.save(fid, format= "svg", height = height, width = width,
            dpi=dpi, units = "in", limitsize = limitsize)
    except ValueError:
        rasie(ValueError, "No ggplot SVG backend")
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
    img = _raw_gg_to_svg(gg, height, width, dpi, limitsize=True)
    new_width, new_height = _transform_size(img.get_size())

    return new_width / 72, new_height / 72 # this does it for inches...

def _select_correcting_size_svg(gg, height, width, dpi, limitsize=True,
                    eps=1e-2, maxIter=2, min_size_px=10):
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
        actual_width, actual_height = _real_size_out_svg(gg=gg,
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

def gg_to_svg(gg, width, height, dpi, limitsize=True,
              eps=1e-2, maxIter=2, min_size_px=10):
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

    return scaled_svg

def _raw_mpt_to_svg(fig, ax, width, height, dpi):
    """
    ... taken from proof_of_concept_wrapper's fa_encapsulate
    """

    # preserve fig.figsize attribute after processing
    base_figsize = fig.get_size_inches()


    self.fig.set_size_inches((width, height))

    fid = io.StringIO()
    self.fig.savefig(fid, format = "svg")
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

def _save_svg_wrapper(svg, filename, width, height, dpi=300, _format=None):
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

    if _format is None:
        dot_ending = re.findall("\\..+$", filename)[0]
        _format = re.sub("\\.", "", dot_ending)

    _format = _format.lower()

    if _format not in _file_options:
        raise ValueError("format / end of file name must be one of\n{}".format(_file_options))

    if _format == "svg":
        svg.save(filename)
    elif _format == "pdf":
        base_image_string = svg.to_str()
        cairosvg.svg2pdf(bytestring = base_image_string,
                 write_to = filename,
                 output_width = width * 96,
                 output_height = height * 96)
    elif _format == "ps":
        base_image_string = svg.to_str()
        cairosvg.svg2ps(bytestring = base_image_string,
                        write_to = filename,
                        output_width = width * 96,
                        output_height = height * 96)
    elif _format == "eps":
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

        if _format == "png":
            cairosvg.svg2png(bytestring = base_image_string,
                 write_to = filename, scale = scale,
                 output_width = width * 96 * scale,
                 output_height = height * 96 * scale)
        elif _format == "jpeg" or _format == "jpg":
            fid = io.BytesIO()
            out_bytes = cairosvg.svg2png(bytestring = base_image_string,
                                         write_to = fid,
                                         scale = scale,
                                         output_width = width * 96 * scale,
                                         output_height = height * 96 * scale)
            img_png = Image.open(io.BytesIO(fid.getvalue()))
            img_png.save(filename)
