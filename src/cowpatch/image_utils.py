import io
from PIL import Image
import copy


# def scalelabeltext(gg, scale):
#     """
#     Scale all text attributes of plotnine ggplot object

#     Arguments
#     ---------
#     gg: plotnine.ggplot.ggplot
#         ggplot object to be copied and altered
#     scale : float
#         scalar to text labels font sizes relative to

#     Returns
#     -------
#     a new copy of the ggplot object
#     """
#     gg_inner = copy.deepcopy(gg)



#     return gg_inner

# def scalegeomsizes(gg, scale):
#     """
#     Scale all geom and stat size attributes of plotnine ggplot object

#     Arguments
#     ---------
#     gg: plotnine.ggplot.ggplot
#         ggplot object to be copied and altered
#     scale : float
#         scalar to scale geom and stat size attributes relative to

#     Returns
#     -------
#     a new copy of the ggplot object
#     """
#     gg_inner = copy.deepcopy(gg)

#     return gg_inner

def gg_to_png(gg,
           width,
           height,
           dpi,
           limitsize):
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
            dpi=dpi, units = "in", limitsize = limitsize)
    buf.seek(0)
    img = Image.open(buf)
    return img




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
            dpi=dpi, units = "in", limitsize = limitsize)
    except ValueError:
        rasie(ValueError, "No ggplot SVG backend")
    fid.seek(0)
    img = sg.fromstring(fid.read())

    return img

def def_test_gg_to_svg():
    """
    this test is just testing consistency
    """
