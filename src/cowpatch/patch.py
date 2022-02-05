import numpy as np
import plotnine as p9
import matplotlib.pyplot as plt
from .image_utils import gg_to_svg
import warnings

# tests for __init__ .grobs element

def test_patch__init__():
    mypatch = myf(grobs = ["banana", [], "ap"]) # .grobs = ["banan", [], "ap"]
    assert np.all(mypatch.grobs == ["banana", [], "ap"]), \
        "grobs passed through grobs parameter incorrectly"

    mypatch2 = myf("banana", [], "ap") # .grobs = ["banan", [], "ap"]
    assert np.all(mypatch2.grobs == ["banana", [], "ap"]), \
        "grobs passed through *args incorrectly"

    error_raised = False
    try:
        myf("banan", [], "ap", grobs = ["banana", [], "ap"]) #error
    except ValueError:
        error_raised = True

    assert error_raised, \
        "patch should raise an error if grobs passed through parameter," +\
        " and *args"

class patch:
    def __init__(self, *args, grobs=None):
        # todo put *args into a list
        args_grobs = [x for x in args]
        if len(args_grobs) > 0
            if grobs is not None:
                raise ValueError("cannot input a grobs list"+\
                                 " as well as individual plots")
            else:
                self.grobs = args_grobs
        else:
            self.grobs = grobs

        self.layout = None
        self.annotation = None
        # """
        # basic processing weight and height
        # """
        # if width is None and height is None:
        #     width, height = plt.rcParams["figure.figsize"]
        # elif width is None:
        #     default_w, default_h = plt.rcParams["figure.figsize"]
        #     width = default_w/default_h * height
        # elif height is None:
        #     default_w, default_h = plt.rcParams["figure.figsize"]
        #     height = default_h/default_w * width

        # return width, height

    def svg(self, width=None, height=None, depth=1):
        """
        create svg from object

        it's here we need to pull out matplotlib's default sizing if width/height are None. What is only 1 is none?
        """
        # need to check if this allows for updating -------
        width, height = self._access_weight_and_height(width, height)

        # base set-up
        width_pt = str(int(width * 72))+"pt" # is this correct... shouldn't it be 4/3?
        height_pt = str(int(height * 72))+"pt"

        pass


    def show(self,width=None,height=None,limitsize=True):
        pass

    def save(self, filename=None, format=None,
             width=None, height=None, units='in',
             dpi=None, limitsize=True, verbose=True,
             **kwargs):

    def __str__(self):
        """
        Print/show the plot
        """
        self.show()
        return ""

    def __repr__(self):
        """
        Print the plot
        """
        return "<patch: (%d)>" % self.__hash__()



class layout:
    def __init__(self,
                 ncol=None,
                 nrow=None,
                 byrow=None,
                 rel_widths=None,
                 rel_heights=None,
                 design=None
                 ):
        """
        This class stores information about layouts out the arangement of
        patches.

        Arguments
        ---------
        ncol : integer
            Integer for the number of columns to arrange the the patches in.
            The default is None (which avoids conflicts if a value for
            `design` is provided). If `ncol` is None but `nrow` is not, then
            `ncol` will default to the minimum number of columns to make sure
            that all patches can be visualized.
        nrow : integer
            Integer for the number of rows to arrange the the patches in.
            The default is None (which avoids conflicts if a value for
            `design` is provided). If `nrow` is None but `ncol` is not, then
            `nrow` will default to the minimum number of rows to make sure
            that all patches can be visualized.
        byrow : boolean
            If `ncol` and/or `nrow` is included, then this boolean indicates
            if the patches should be ordered by row (default if byrow is None
            or when parameter is True) or by column (if byrow was False).
        design : np.array (float based) or str
            Specification of the location of each patch in the arrangement.
            Can either be a float numpy array with integers between 0 and
            the number of patches to arrange, or a text string that captures
            similar ideas to the array approach but uses capital alphabetical
            characters (A-Z) to indicate each figure. More information is in
            Details.
        rel_widths : list, np vector or tuple
            Numerical vector of relative columns widths. This not required,
            the default would be `np.ones(ncol)` or `np.ones(design.shape[0])`.
            Note that this is a relative sizing and the values are only
            required to be non-negative, non-zero values, for example
            [1,2] would would make the first column twice as wide as the
            second column.
        rel_heights : list or tuple
            Numerical vector of relative row heights. This not required,
            the default would be `np.ones(nrow)` or `np.ones(design.shape[1])`.
            Note that this is a relative sizing and the values are only
            required to be non-negative, non-zero values, for example
            [1,2] would would make the first row twice as tall as the
            second row.

        Details
        -------
        The `design` parameter expects specific input.

        1. If the `design` is input as a numpy array, we expect it to have
        integers only (0 to # patches -1). It is allowed to have `np.nan` values
        if certain "squares" of the  layout are not covered by others (the
        covering is defined by the value ordering). Note that we won't check
        for overlap and `np.nan` is not enforced if another patches' relative
        (min-x,min-y) and (max-x, max-y) define a box over that `np.nan`'s
        area.

        An example of a design of the numpy array form could look like

        ```python
        my_np_design = np.array([[1,1,2],
                                 [3,3,2],
                                 [3,3,np.nan]])
        ```

        2. if the `design` parameter takes in a string, we expect it to have
        a structure such that each line (pre "\n") contains the same number
        of characters, and these characters must come from the first
        (# patches =1) capital alphabetical characters or the "#" or "." sign to
        indicate an empty square. Similar arguments w.r.t. overlap and the
        lack of real enforcement for empty squares applies (as in #1).

        An example of a design of the string form could look like

        ```python
        my_str_design = \"\"\"
        AAB
        CCB
        CC#
        \"\"\"
        ```
        or
        ```python
        my_str_design = \"\"\"
        AAB
        CCB
        CC.
        \"\"\"
        ```

        Similarities to `R` cousins
        ---------------------------
        This layout function is similar to `patchwork::plot_layout` (with a
        special node to `design` parameter) and helps perform similar ideas to
        `gridExtra::arrangeGrob`'s `layout_matrix` parameter, and
        `cowplot::plot_grid`'s `rel_widths` and `rel_heights` parameters


        """

        # https://patchwork.data-imaginist.com/articles/guides/layout.html

        # compared to cowplot::plot_grid
        # no align / axis (they're duplicated of ncol/nrow)
        # also rel_widths and rel_heights are just width/heights

        if design is not None:
            if ncol is not None or nrow is not None:
                warnings.warn("ncol and nrow are overridden"+\
                              " by the design parameter")

            if isinstance(design, np.ndarray):
                if len(design.shape) == 1:
                    warnings.warn("design matrix is 1d,"+\
                                  " will be seen as a 1-row design")

                    nrow, ncol = 1, design.shape[0]
                    design = design.reshape((1,-1))
                else:
                    nrow, ncol = design.shape
            if isinstance(design, str):
                # convert design to desirable structure matrix structure
                design = self._design_string_to_mat(design)
                nrow, ncol = design.shape

        # TODO: check here that all integers 0-max are included...
        # TODO: also track this number

        if ncol is None:
            if rel_widths is not None:
                if isinstance(rel_widths, np.ndarray):
                    ncol = rel_widths.shape[0]
                if isinstance(rel_widths, list) or \
                        isinstance(rel_widths, tuple):
                    ncol = len(rel_widths)
                    rel_widths = np.array(rel_widths)

        if nrow is None:
            if rel_heights is not None:
                if isinstance(rel_heights, np.ndarray):
                    nrow = rel_heights.shape[0]
                if isinstance(rel_heights, list) or \
                        isinstance(rel_heights, tuple):
                    nrow = len(rel_heights)
                    rel_heights= np.array(rel_heights)

        # this probably could be run a different way (and is there no
        # square default?)
        if rel_widths is None and rel_heights is None:
            assert not (ncol is None and nrow is None), \
                "need some parameters to not be none in design initialization"

        if rel_widths is None:
            rel_widths = np.ones(ncol)
        if rel_heights is None:
            rel_heights = np.ones(nrow)

        if design is None:
            if byrow is None or byrow:
                order_str = "C"
            else:
                order_str = "F"
            design = np.arange(ncol*nrow,dtype = int).reshape((nrow, ncol),
                                                            order = order_str)

        self.ncol = ncol
        self.nrow = nrow
        self.design = design
        self.rel_widths = rel_widths
        self.rel_heights = rel_heights
        self.num_items = self._assess_mat(design)

    def _design_string_to_mat(self, design):
        """
        Internal function to convert design string into a matrix

        Argument
        --------
        design : str
            design in a string format

        Returns
        -------
        design : np.array integer
            design in np.array format
        """
        design_clean = re.sub(" *\t*", "", design) # removing spaces and tabs
        design_clean = re.sub("^\n*", "", design_clean) # remove leading nl
        design_clean = re.sub("\n*$", "", design_clean) # remove following nl

        row_info = re.split("\n", design_clean)

        ncol_lengths = np.unique([len(x) for x in row_info])

        if ncol_lengths.shape != (1,):
            raise ValueError("expect all rows in design to have the same "+\
                             "number of entries, use # for an empty space "+\
                             "if using a string format.")

        ncol = int(ncol_lengths)
        nrow = len(re.findall("\n", design)) + 1

        design = np.array([[ ord(val)-65 if val != "#" else np.nan for val in r]
                            for r in row_info])

        return design

    def _assess_mat(self, design):
        """
        Assesses if the design matrix includes at least 1 box for patches
        indexed 0 to (# patches - 1). This doesn't actually assume to know
        the number of patches.

        Argument
        --------
        design : np.array (integer)
            design in numpy array format

        Returns
        -------
        This function return an error or the number of patches expected in the
        overall matrix.
        """
        unique_vals = np.unique(design)
        unique_vals = np.sort(
            unique_vals[np.logical_not(np.isnan(unique_vals))])

        num_unique = unique_vals.shape[0]
        if not np.allclose(unique_vals, np.arange(num_unique)):
            raise ValueError("design input requires values starting "+\
                             "with 0/A and through integer/alphabetical "+\
                             "value expected for the number of patches "+\
                             "provided")

        return num_unique

    def __hash__(self):
        info_list = list(self.design.ravel()) + \
            list(self.rel_widths) + list(self.rel_heights) +\
            [self.ncol, self.nrow, self.num_items]
        return abs(hash(tuple(info_list)))

    def __str__(self):
        return "<layout (%d)>" % self.__hash__()

    def __repr__(self):
        out = "design (%i, %i):\n\n"% (self.nrow, self.ncol) +\
            self.design.__str__() +\
            "\n\nwidths:\n" +\
            self.rel_widths.__str__() +\
            "\nheights:\n" +\
            self.rel_heights.__str__()
        return self.__str__() + "\n" + out

    def __eq__(self, other):
        if np.allclose(self.design,other.design,equal_nan=True) and \
            self.ncol == other.ncol and \
            self.nrow == other.nrow and \
            np.unique(self.rel_heights/other.rel_heights).shape[0] == 1 and \
            np.unique(self.rel_widths/other.rel_widths).shape[0] == 1:
            return True
        else:
            return False

import pytest

def test_layout():
    design1 = np.array([[np.nan, 0, 0],[1,1, np.nan]])
    design2 = "#AA\nBB#"
    design3 = """
    #AA
    BB#
    """
    design4 = """
              #AA
              BB#
              """
    #^ what if this is tabbed?

    l1 = layout(design = design1)
    l2 = layout(design = design2)
    l3 = layout(design = design3)
    l4 = layout(design = design4)


    assert l2 == l1, \
        "expect string and matrix layout structure to create same matrix"
    assert l2 == l3, \
        "expect string inputs in different formats to be the same " +\
        "(trailing and leading extra rows)"
    assert l2 == l4, \
        "expect string inputs in different formats to be the same (tabbed +"+\
        "and trailing and leading extra rows)"

    # nrow + ncol (byrow checks of defaults) ----
    ncol3 = 3
    nrow3 = 4

    l5 = layout(ncol = ncol3, nrow = nrow3)
    l6 = layout(ncol = ncol3, nrow = nrow3, byrow = False)

    l5_1 = layout(design = np.array([[1,2,3],
                                     [4,5,6],
                                     [7,8,9],
                                     [10,11,12]])-1)

    l6_1 = layout(design = np.array([[1,5,9],
                                     [2,6,10],
                                     [3,7,11],
                                     [4,8,12]]) - 1)

    assert l5 == l5_1, \
        "expect default ncol/nrow and byrow (byrow = True) failed to preform"
    assert l6 == l6_1, \
        "expect default ncol/nrow with bycol (byrow = False) failed to preform"


    # error testing -----
    # index started incorrect
    with pytest.raises(Exception) as e_info:
        l7 = layout(design = np.array([[1,2,3],
                                     [4,5,6],
                                     [7,8,9],
                                     [10,11,12]]))
    with pytest.raises(Exception) as e_info:
        l8 = layout(design = np.array([[0,2],
                                       [0,2]]))
    with pytest.raises(Exception) as e_info:
        l9 = layout(design = np.array([[0,2, np.nan],
                                       [0,2, np.nan]]))


class annotation:
    def __init__(self):
        pass

class inset(patch):
    def __init__(self):
        pass

class matplotlib_patch(patch):
    def __init__(self, fig, axes):
        """
        Figure and axes cowpatch encapsulation.

        This encapsulation holds both the figure and axes made
        by the user. The user can still access the true fig and axes
        elements with object.fig and object.axes.

        Arguments
        ---------
        fig : matplotlib.figure
            figure object to be encapsulated
        axes : matplotlib.axes
            assumed to be associated with the fig

        Details
        -------
        you are able to access the self.fig and self.axes to update the plot
        but be careful...

        TODO: probably want to apply same size check as was done for the
        plotnine objects...
        """

        self.fig = fig
        self.axes = axes

    def svg(self, width=None, height=None, depth = 0):
        """
        this needs to be updated...
        """
        depth = 0

        if width is None
        base_figsize = self.fig.get_size_inches()
        if figsize is not None:
            self.fig.set_size_inches(figsize)

        fid = io.StringIO()
        self.fig.savefig(fid, format = "svg")
        fid.seek(0)
        image_string = fid.read()
        img = sg.fromstring(image_string)

        if figsize is not None:
            self.fig.set_size_inches(base_figsize)

        return img
    def __repr__(self):
        return "<matplotlib patch: (%d)>" % self.__hash__()
class seaborn_patch(matplotlib_patch):
    def __repr__(self):
        return "<seaborn patch: (%d)>" % self.__hash__()

class text:
    def __init__(self):
        pass
