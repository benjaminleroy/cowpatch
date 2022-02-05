import io

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
