# libraries ---------------
import plotnine as p9
import io

# additional functions ---------------
# I've only added the functions here that I needed for structure
# you probably will could benefit from copying others from different files

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

# class definition ----------------

class bad_gg_encapsulate():
    def __init__(self, plot):
        """
        this is just a placeholder for a more complex 'cowpatch' object that
        will work for now. One should assume that it has a svg function
        like that below

        Argument
        --------
        plot : plotnine.ggplot object
            plot to encapsulate

        Details
        -------
        2/1: hopefully this object class performs all you need (message me if
        that's not the case)
        """
        self.plot = plot

    def svg(self, width=None, height=None, limitsize=True):
        """
        create an svg object from self...
        """
        return gg_to_svg(self.plot, width, height,
                         dpi=96, limitsize=limitsize)

FILL_IN = None

class inset:
    def __init__(self,plot,
                 x,y,width,height,
                 ha="left",va="bottom"):
        """
        inset a plot into another (or a cowpatch "other")

        Arguments
        ---------
        plot : plotnine.ggplot or cowpatch object
            plot / patch to inset
        x : float
            float between 0 and 1 (inclusive) for the x location new inset
            relative to a 0-1 representation of the underlying base patch /
            plot's y dimension
        y : float
            float between 0 and 1 (inclusive) for the y location new inset
            relative to a 0-1 representation of the underlying base patch /
            plot's y dimension
        width : float
        height : float
        ha : str
            horizational alignment, string options of "left", "center", "right"
        va : str
            vertical alignment, string options of "top", "center", "bottom"

        Details
        -------
        the parameters of this function look similar to that of
        1. https://wilkelab.org/cowplot/reference/draw_image.html

        Note that the ha/va options are relative to plotnine's constraints
        that limit the ggplot standard hjust and vjust.

        2/1: I'm ok without the checks and the ha/va corrections. Later we
        could silently accept hjust and vjust (like plotnine)...

        """
        self.base = None

        if True: # check if plot is a plotnine.ggplot object, if so encapulate
            self.inset = bad_gg_encapsulate(plot)
        else: # else just pass through
            self.inset = plot

        # maybe some checks here too? (maybe a helper function? probably use ha/va)
        self.x = FILL_IN
        self.y = FILL_IN
        self.width = FILL_IN
        self.height = FILL_IN

        # probably some checks here? (maybe a helper function?)
        self.ha = FILL_IN
        self.va = FILL_IN

    def __radd__(self, other):
        """
        right addition for inset

        Argument
        --------
        other : plotnine.ggplot object or patch object

        Return
        ------
        self : self

        Details
        -------
        this method allows for

        `ggplot_obj + inset(...)`

        -and-

        `patch_obj + inset(...)`


        """

        if True: # check if other is a plotnine.ggplot object, if so encapulate
            self.base = bad_gg_encapsulate(other)
        else: # else just pass through
            self.base = other

        return self


    def svg(self, width=None, height=None, limitsize=True):
        """
        create svg of object

        Argument
        --------
        width : float
            width in inches for base image/patch
        height : float
            height in inches for base image/patch
        limitsize : boolean
            checker to make sure width and height aren't input as px,pt (see
            plotnine ggplot's save function). Should raise error if width or
            height is > 50.

        Return
        ------
        svg_representation : svgutils.transform object

        Details
        -------
        2/1: I'm ok without the default corrections (you can just set it as 6,
        4). Also happy if you remove all limitsize paramters
        """
        if width is None:
            # width should become matplotlib defaults
            pass
        if height is None:
            # width should become matplotlib defaults
            pass

        pass

    def show(self, width=None, height=None,limitsize=True):
        """
        shows object in command line

        I recommend looking at "show_image" function in
        "proof_of_concept_combined_svg.py".

        Argument
        --------
        width : float
            width in inches for base image/patch
        height : float
            height in inches for base image/patch
        limitsize : boolean
            checker to make sure width and height aren't input as px,pt (see
            plotnine ggplot's save function). Should raise error if width or
            height is > 50.

        Details
        --------
        2/1: you don't need to impliment this, I just figured it's a helpful
        function to visualize the results, but saving can also help with this

        """
        svg_obj = self.svg(width=width, height =height,limitsize=limitsize)
        # ...

    def __str__(self):
        """
        this is extra, but could think about how to describe it w.r.t. what
        plotnine's ggplot object returns

        Details
        -------
        2/1: I'm ok if you don't work on this
        """
        pass


    def save(self, filename, width=None, height=None, limitsize=True):
        """
        Save inset visual to a file

        Argument
        --------
        width : float
            width in inches for base image/patch
        height : float
            height in inches for base image/patch

        Details
        -------
        2/1: I'm ok without the default corrections (you can just set it as 6,
        4). Also I'm ok if you just assume this is saving as an svg object
        currently, especially since this is likely to be a super class function

        """
        if width is None:
            # width should become matplotlib defaults
            pass
        if height is None:
            # width should become matplotlib defaults
            pass


# example --------------

mtcars = pd.read_csv('https://gist.githubusercontent.com/ZeccaLehn/4e06d2575eb9589dbe8c365d61cb056c/raw/64f1660f38ef523b2a1a13be77b002b98665cdfe/mtcars.csv')


p1 = p9.ggplot(mtcars) +\
  p9.geom_boxplot(p9.aes(x="gear",y= "disp", group = "gear")) +\
  p9.labs(title = 'mallory, please')

p2 = p9.ggplot(mtcars) +\
  p9.geom_point(p9.aes(x="hp", y="wt")) +\
  p9.labs(title = 'inset me!')


mallorys_inset = p1 + inset(p2, x=.35, y=.6, width=.33, height=.33)

mallorys_inset.show()

mallorys_inset.save("mallory_inset.svg", width = 6, height = 4)
#^ I open svg files in chrome

mallorys_inset2 = bad_gg_encapsulate(p1) +\
    inset(p2, x=.35, y=.6, width=.33, height=.33)

mallorys_inset2.show()

mallorys_inset2.save("mallory_inset2.svg", width = 6, height = 4)
#^ I open svg files in chrome

