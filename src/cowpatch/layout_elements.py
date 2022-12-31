import re
import numpy as np
import warnings
import copy
from .utils import is_pos_int, is_non_neg_int, \
                is_proportion, is_positive, is_non_negative, \
                inherits

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
        layout class to store information about arangement of patches found
        in `cow.patch`.

        Arguments
        ---------
        ncol : integer
            Integer for the number of columns to arrange the the patches in.
            The default is None (which avoids conflicts if a value for
            `design` is provided). If ``ncol`` is None but ``nrow`` is not,
            then ``ncol`` will default to the minimum number of columns to
            make sure that all patches can be visualized.
        nrow : integer
            Integer for the number of rows to arrange the the patches in.
            The default is None (which avoids conflicts if a value for
            ``design`` is provided). If ``nrow`` is None but ``ncol`` is not,
            then ``nrow`` will default to the minimum number of rows to make
            sure that all patches can be visualized.
        byrow : boolean
            If ``ncol`` and/or ``nrow`` is included, then this boolean
            indicates if the patches should be ordered by row (default if
            ``byrow`` is None or when parameter is ``True``) or by column (if
            ``byrow`` was ``False``).
        design : np.array (float based) or str
            Specification of the location of each patch in the arrangement.
            Can either be a float numpy array with integers between 0 and
            the number of patches to arrange, or a text string that captures
            similar ideas to the array approach but uses capital alphabetical
            characters (A-Z) to indicate each figure. More information is in
            Notes.
        rel_widths : list, np vector or tuple
            Numerical vector of relative columns widths. This not required,
            the default would be ``np.ones(ncol)`` or
            ``np.ones(design.shape[0])``. Note that this is a relative sizing
            and the values are only required to be non-negative, non-zero
            values, for example ``[1,2]`` would would make the first column
            twice as wide as the second column.
        rel_heights : list or tuple
            Numerical vector of relative row heights. This not required,
            the default would be ``np.ones(nrow)`` or
            ``np.ones(design.shape[1])``. Note that this is a relative sizing
            and the values are only required to be non-negative, non-zero
            values, for example ``[1,2]`` would would make the first row twice
            as tall as the second row.


        Notes
        -----

        *Design*

        The ``design`` parameter expects specific input.

        1. If the ``design`` is input as a numpy array, we expect it to have
        integers only (0 to # patches-1). It is allowed to have ``np.nan``
        values if certain "squares" of the  layout are not covered by others
        (the covering is defined by the value ordering). Note that we won't
        check for overlap and ``np.nan`` is not enforced if another patches'
        relative (min-x,min-y) and (max-x, max-y) define a box over that
        ``np.nan``'s area.

        An example of a design of the numpy array form could look like

        >>> my_np_design = np.array([[1,1,2],
        ...                          [3,3,2],
        ...                          [3,3,np.nan]])


        2. if the ``design`` parameter takes in a string, we expect it to have
        a structure such that each line (pre ``\\\\n``) contains the same number
        of characters, and these characters must come from the first
        (number of patches) capital alphabetical characters or the ``\#`` or
        ``.`` sign to indicate an empty square. Similar arguments w.r.t.
        overlap and the lack of real enforcement for empty squares applies
        (as in 1.).

        An example of a design of the string form could look like

        >>> my_str_design = \"\"\"
        ... AAB
        ... CCB
        ... CC\#
        ... \"\"\"

        or

        >>> my_str_design = \"\"\"
        ... AAB
        ... CCB
        ... CC.
        ... \"\"\"

        See the `Layout guide`_ for more detailed examples of functionality.

        .. _Layout guide: https://benjaminleroy.github.io/cowpatch/guides/Layout.html

        *Similarities to our `R` cousins:*

        This layout function is similar to `patchwork\:\:plot_layout <https://patchwork.data-imaginist.com/reference/plot_layout.html>`_
        (with a special node to ``design`` parameter) and helps perform similar
        ideas to `gridExtra\:\:arrangeGrob <https://cran.r-project.org/web/packages/gridExtra/vignettes/arrangeGrob.html>`_'s
        ``layout_matrix`` parameter, and `cowplot\:\:plot_grid <https://wilkelab.org/cowplot/reference/plot_grid.html>`_'s
        ``rel_widths`` and ``rel_heights`` parameters.

        Examples
        --------
        >>> # Necessary libraries for example
        >>> import numpy as np
        >>> import cowpatch as cow
        >>> import plotnine as p9
        >>> import plotnine.data as p9_data

        >>> g0 = p9.ggplot(p9_data.mpg) +\\
        ...     p9.geom_bar(p9.aes(x="hwy")) +\\
        ...     p9.labs(title = 'Plot 0')
        >>> g1 = p9.ggplot(p9_data.mpg) +\\
        ...     p9.geom_point(p9.aes(x="hwy", y = "displ")) +\\
        ...     p9.labs(title = 'Plot 1')
        >>> g2 = p9.ggplot(p9_data.mpg) +\\
        ...     p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\\
        ...     p9.labs(title = 'Plot 2')
        >>> g3 = p9.ggplot(p9_data.mpg[p9_data.mpg["class"].isin(["compact",
        ...                                                      "suv",
        ...                                                      "pickup"])]) +\\
        ...     p9.geom_histogram(p9.aes(x="hwy"),bins=10) +\\
        ...     p9.facet_wrap("class")

        >>> # design matrix
        >>> vis_obj = cow.patch(g1,g2,g3)
        >>> vis_obj += cow.layout(design = np.array([[0,1],
        ...                                          [2,2]]))
        >>> vis_obj.show()

        >>> # design string
        >>> vis_obj2 = cow.patch(g1,g2,g3)
        >>> vis_obj2 += cow.layout(design = \"\"\"
        ...                                 AB
        ...                                 CC
        ...                                 \"\"\")
        >>> vis_obj2.show()

        >>> # nrow, ncol, byrow
        >>> vis_obj3 = cow.patch(g0,g1,g2,g3)
        >>> vis_obj3 += cow.layout(nrow=2, byrow=False)
        >>> vis_obj3.show()

        >>> # rel_widths/heights
        >>> vis_obj = cow.patch(g1,g2,g3)
        >>> vis_obj += cow.layout(design = np.array([[0,1],
        ...                                          [2,2]]),
        ...                       rel_widths = np.array([1,2]))
        >>> vis_obj.show()

        See also
        --------
        area : object class that helps ``layout`` define where plots will go
            in the arangement
        patch : fundamental object class which is combined with ``layout`` to
            defin the overall arangement of plots

        """
        if design is not None:
            if ncol is not None or nrow is not None:
                warnings.warn("ncol and nrow are overridden"+
                              " by the design parameter")

            if isinstance(design, np.ndarray):
                if len(design.shape) == 1:
                    warnings.warn("design matrix is 1d,"+
                                  " will be seen as a 1-row design")

                    nrow, ncol = 1, design.shape[0]
                    design = design.reshape((1,-1))
                else:
                    nrow, ncol = design.shape
            if isinstance(design, str):
                # convert design to desirable structure matrix structure
                design = self._design_string_to_mat(design)
                nrow, ncol = design.shape

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

        if rel_widths is None and rel_heights is None:
            assert not (ncol is None and nrow is None), \
                "need some parameters to not be none in design initialization"

        if rel_widths is None and ncol is not None:
            rel_widths = np.ones(ncol)
        if rel_heights is None and nrow is not None:
            rel_heights = np.ones(nrow)

        if rel_heights is not None:
            rel_heights = np.array(rel_heights)
        if rel_widths is not None:
            rel_widths = np.array(rel_widths)
        # if design is None:
        #     if byrow is None or byrow:
        #         order_str = "C"
        #     else:
        #         order_str = "F"
        #     design = np.arange(ncol*nrow,dtype = int).reshape((nrow, ncol),
        #                                                     order = order_str)

        if design is not None:
            byrow = None

        # ncol/nrow and rel_widths/rel_heights correct alignment
        if ncol is not None and rel_widths is not None:
            if ncol != rel_widths.shape[0]:
                raise ValueError("ncol (potentially from the design) and "+
                                 "rel_widths disagree on size of layout")
        if nrow is not None and rel_heights is not None:
            if nrow != rel_heights.shape[0]:
                raise ValueError("nrow (potentially from the design) and "+
                                 "rel_heights disagree on size of layout")

        self.ncol = ncol
        self.nrow = nrow
        self.__design = design
        self.byrow = byrow
        self.rel_widths = rel_widths
        self.rel_heights = rel_heights
        self.num_grobs = self._assess_mat(design)

    def _design_string_to_mat(self, design):
        """
        Internal function to convert design string into a matrix

        Arguments
        ---------
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
            raise ValueError("expect all rows in design to have the same "+
                             "number of entries, use # for an empty space "+
                             "if using a string format.")

        ncol = int(ncol_lengths)
        nrow = len(re.findall("\n", design)) + 1

        design = np.array([[ ord(val)-65
                            if not np.any([val == x for x in ["#","."]])
                            else np.nan
                            for val in r]
                                for r in row_info])

        return design

    def _get_design(self, num_grobs=None):
        """
        create a design matrix if not explicit design has been provided
        """

        if self.__design is not None:
            return self.__design

        if num_grobs is None:
            if self.num_grobs is None:
                raise ValueError("unclear number of grobs in layout...")
            else:
                num_grobs = self.num_grobs

        if self.byrow is None or self.byrow:
            order_str = "C"
        else:
            order_str = "F"

        # if only ncol or nrow is defined...
        ncol = self.ncol
        nrow = self.nrow
        if ncol is None:
            ncol = int(np.ceil(num_grobs / nrow))
        if nrow is None:
            nrow = int(np.ceil(num_grobs / ncol))

        inner_design = np.arange(ncol*nrow,
                                  dtype = float).reshape((nrow, ncol),
                                                        order = order_str)
        inner_design[inner_design >= num_grobs] = np.nan

        _ = self._assess_mat(inner_design) # should pass since we just built it...

        return inner_design

    # property
    design = property(_get_design)
    """
    defines underlying ``design`` attribute (potentially defined relative to a
    ``cow.patch`` object if certain structure are not extremely specific.
    """

    def _assess_mat(self, design):
        """
        Assesses if the design matrix includes at least 1 box for patches
        indexed 0 to (number of patches - 1). This doesn't actually assume to know
        the number of patches.

        Arguments
        ---------
        design : np.array (integer)
            design in numpy array format

        Returns
        -------
        int
            number of patches expected in the overall matrix.

        Raises
        ------
        ValueError
            if design matrix doesn't include at least at least 1 box for all
            indices between 0 to (number of patches - 1)
        """
        if design is None:
            return None # to identify later that we don't have a design matrix

        unique_vals = np.unique(design)
        unique_vals = np.sort(
            unique_vals[np.logical_not(np.isnan(unique_vals))])

        num_unique = unique_vals.shape[0]
        if not np.allclose(unique_vals, np.arange(num_unique)):
            raise ValueError("design input requires values starting "+
                             "with 0/A and through integer/alphabetical "+
                             "value expected for the number of patches "+
                             "provided")

        return num_unique

    def _rel_structure(self, num_grobs=None):
        """
        provide rel_structure (rel_widths, rel_heights) if missing

        Arguments
        ---------
        num_grobs : int
            if not None, then this value will be used to understand the number
            of grobs to be laid out

        Returns
        -------
        rel_widths : np.array vector
            a vector of relative widths of the columns of the layout design
        rel_heights : np.array vector
            a vector of relative heights of the rows of the layout design
        """
        if num_grobs is None:
            if not (self.ncol is not None and
                    self.nrow is not None) and \
               not (self.rel_widths is not None and
                    self.rel_heights is not None):
                raise ValueError("unclear number of grobs in layout -> "+
                                "unable to identify relative width and height")

        rel_widths = self.rel_widths
        rel_heights = self.rel_heights
        ncol = self.ncol
        nrow = self.nrow

        if rel_widths is not None and ncol is None:
            ncol = rel_widths.shape[0]
        if rel_heights is not None and nrow is None:
            nrow = rel_heights.shape[0]

        if ncol is None:
                ncol = int(np.ceil(num_grobs/nrow))
        if rel_widths is None:
            rel_widths = np.ones(ncol)


        if nrow is None:
            nrow = int(np.ceil(num_grobs/ncol))
        if rel_heights is None:
            rel_heights = np.ones(nrow)

        return rel_widths, rel_heights

    def _element_locations(self, width_pt, height_pt, num_grobs=None):
        """
        create a list of ``area`` objects associated with the location of
        each of the layout's grobs w.r.t. a given points width and height

        Arguments
        ---------
        width_pt : float
            global width (in points) of the full arangement of patches
        height_pt : float
            global height (in points) of the full arangement of patches
        num_grobs : integer
            if not ``None``, then this value will be used to understand the
            number of grobs to be laid out

        Returns
        -------
        list
            list of ``area`` objects describing the location for each of the
            layout's grobs (in the order of the index in the self.design)
        """

        if self.num_grobs is None and num_grobs is None:
            raise ValueError("unclear number of grobs in layout...")
        if self.num_grobs is not None:
            if num_grobs is not None and num_grobs != self.num_grobs:
                warnings.warn("_element_locations overrides num_grobs "+
                              "with self.num_grobs")
            num_grobs = self.num_grobs

        rel_widths, rel_heights = self._rel_structure(num_grobs=num_grobs)


        areas = []

        for p_idx in np.arange(num_grobs):
            dmat_logic = self._get_design(num_grobs=num_grobs) == p_idx
            r_logic = dmat_logic.sum(axis=1) > 0
            c_logic = dmat_logic.sum(axis=0) > 0

            inner_x_where = np.argwhere(c_logic)
            inner_x_left = np.min(inner_x_where)
            inner_x_right = np.max(inner_x_where)
            inner_width = inner_x_right - inner_x_left + 1

            inner_x_where = np.argwhere(r_logic)
            inner_y_top = np.min(inner_x_where)
            inner_y_bottom = np.max(inner_x_where)
            inner_height = inner_y_bottom - inner_y_top + 1

            inner_design_area = area(x_left = inner_x_left,
                                     y_top = inner_y_top,
                                     width = inner_width,
                                     height = inner_height,
                                     _type = "design")

            areas.append(inner_design_area.pt(rel_widths=rel_widths,
                                              rel_heights=rel_heights,
                                              width_pt=width_pt,
                                              height_pt=height_pt))

        return areas

    def _yokogaki_ordering(self, num_grobs=None):
        """
        calculates the yokogaki (left to right, top to bottom) ordering
        the the patches

        Arguments
        ---------
        num_grobs : integer
            if not ``None``, then this value will be used to understand the
            number of grobs to be laid out

        Returns
        -------
        numpy array (vector) of integer index of plots in yokogaki ordering

        Notes
        -----
        Yokogaki is a Japanese word that concisely describes the left to right,
        top to bottom writing format. We'd like to thank `stack overflow`_.
        for pointing this out.

        .. _stack overflow:
            https://english.stackexchange.com/questions/81520/is-there-a-word-for-left-to-right-and-top-to-bottom
        """
        if self.num_grobs is None and num_grobs is None:
            raise ValueError("unclear number of grobs in layout...")
        if self.num_grobs is not None:
            if num_grobs is not None and num_grobs != self.num_grobs:
                warnings.warn("_element_locations overrides num_grobs "+
                              "with self.num_grobs")
            num_grobs = self.num_grobs

        areas = self._element_locations(1,1) # basically getting relative positions (doesn't matter) - nor does it matter about rel_height and width, but ah well
        all_x_left = np.array([a.x_left for a in areas])
        all_y_top = np.array([a.y_top for a in areas])

        index_list = np.arange(num_grobs)

        yokogaki_ordering = []
        # remember y_tops are w.r.t top axis
        for y_val in np.sort(np.unique(all_y_top)):
            given_row_logic = all_y_top == y_val
            inner_index = index_list[given_row_logic]
            inner_x_left = all_x_left[given_row_logic]

            row_ids = inner_index[np.argsort(inner_x_left)]
            yokogaki_ordering += list(row_ids)

        return np.array(yokogaki_ordering)

    def __hash__(self):
        """
        Creates a 'unique' hash for the object to help with identification

        Returns
        -------
        hash integer
        """
        if self.num_grobs is None:
            design_list = [None]
        else:
            design_list = list(self.design.ravel())

        rw_list = [None]
        if self.rel_widths is not None:
            rw_list = list(self.rel_widths)

        rh_list = [None]
        if self.rel_heights is not None:
            rh_list = list(self.rel_heights)

        info_list = design_list + \
            rw_list + rh_list +\
            [self.ncol, self.nrow, self.num_grobs]
        return abs(hash(tuple(info_list)))

    def __str__(self):
        return "<layout (%d)>" % self.__hash__()

    def __repr__(self):
        nrow_str = str(self.nrow)
        if self.nrow is None:
            nrow_str = "unk"
        ncol_str = str(self.ncol)
        if self.ncol is None:
            ncol_str = "unk"

        if self.num_grobs is None:
            design_str = "*unk*"
        else:
            design_str = self.design.__str__()

        rw_str = "unk"
        if self.rel_widths is not None:
            rw_str = self.rel_widths.__str__()

        rh_str = "unk"
        if self.rel_heights is not None:
            rh_str = self.rel_heights.__str__()

        out = "design (%s, %s):\n\n"% (nrow_str, ncol_str) +\
            design_str +\
            "\n\nwidths:\n" +\
            rw_str +\
            "\nheights:\n" +\
            rh_str
        return self.__str__() + "\n" + out

    def __eq__(self, value):
        """
        checks if object is equal to another object (value)

        Arguments
        ---------
        value : object
            another object (that major or may not be of the layout class)

        Returns
        -------
        boolean
            if current object and other object (value) are equal
        """
        # if value is not a layout...
        if not inherits(value, layout):
            return False

        # if __design hasn't been specified on 1 but is on another
        if (self.__design is None and value.__design is not None) or\
            (self.__design is not None and value.__design is None):
            return False

        # accounting for lack of __design specification
        design_logic = True
        if self.__design is not None:
            design_logic = np.allclose(self.design,value.design,equal_nan=True)

        return design_logic and \
            self.ncol == value.ncol and \
            self.nrow == value.nrow and \
            np.unique(self.rel_heights/value.rel_heights).shape[0] == 1 and \
            np.unique(self.rel_widths/value.rel_widths).shape[0] == 1


class area:
    def __init__(self,
                 x_left, y_top,
                 width, height,
                 _type):
        """
        object that stores information about what area a ``patch`` will fill

        Arguments
        ---------
        x_left : float
            scalar of where the left-most point of the patch is located (impacted
            by the ``_type`` parameter)
        y_top : float
            scalar of where the top-most point of the patch is located (impacted
            by the ``_type`` parameter)
        width : float
            scalar of the width of the patch (impacted by the ``_type``
            parameter)
        height : float
            scalar of the height of the patch (impacted by the ``_type``
            parameter)
        _type : str {"design", "relative", "pt"}
            describes how the parameters are stored. See Notes for more
            information between the options.


        Notes
        -----

        These objects provide structural information about where in the overall
        arangement individual plots / sub arangments lie.

        The ``_type`` parameter informs how to understand the other parameters:

        1. "design" means that the values are w.r.t. to a design matrix
        relative to the `layout` class, and values are relative to the rows
        and columns units.

        2. "relative" means the values are defined relative to the full size of
        the canvas and taking values between 0-1 (inclusive).

        3. "pt" means that values are defined relative to point values

        See also
        --------
        layout : object that incorporates multiple area definitions to define
            layouts.
        """

        # some structure check:
        self._check_info_wrt_type(x_left, y_top, width, height, _type)

        self.x_left = x_left
        self.y_top = y_top
        self.width = width
        self.height = height
        self._type = _type

    def _check_info_wrt_type(self, x_left, y_top, width, height, _type):
        """
        some logic checks of inputs relative to ``_type`` parameter

        Arguments
        ---------
        x_left : float
            scalar of where the left-most point of the patch is located
            (impacted by the ``_type`` parameter)
        y_top : float
            scalar of where the top-most point of the patch is located
            (impacted by the ``_type`` parameter)
        width : float
            scalar of the width of the patch (impacted by the ``_type``
            parameter)
        height : float
            scalar of the height of the patch (impacted by the ``_type``
            parameter)
        _type : str {"design", "relative", "pt"}
            describes how the parameters are stored. Options include
            ["design", "relative", "pt"]. See class docstring for more info

        Raises
        ------
        ValueError
            if any of the first four parameters don't make sense with respect
            to the ``_type`` parameter
        """

        if _type not in ["design", "relative", "pt"]:
            raise ValueError("_type parameter not an acceptable option, see"+
                             " documentation")

        if _type == "design" and \
            not np.all([is_non_neg_int(val) for val in [x_left,y_top]] +
                       [is_pos_int(val) for val in [width,height]]) :
            raise ValueError("with _type=\"design\", all parameters must be "+
                             "positive integers")
        elif _type == "relative" and \
            not np.all([is_proportion(val) for val in [x_left,y_top,
                                                       width,height]] +
                       [is_positive(val) for val in [width,height]]):
            raise ValueError("with _type=\"relative\", all parameters should"+
                             " be between 0 and 1 (inclusive) and width and"+
                             " height cannot be 0")
        elif _type == "pt" and \
            not np.all([is_non_negative(val) for val in [x_left,y_top]] +
                       [is_positive(val) for val in [width,height]]):
            raise ValueError("with _type=\"pt\", all x_left and y_top should"+
                             " be non-negative and width and height should"+
                             " be strictly positive")


    def _design_to_relative(self, rel_widths, rel_heights):
        """
        translates an area object with ``_type`` = "design" to area object
        with ``_type`` = "relative".

        Arguments
        ---------
        rel_widths : np.array (vector)
            list of relative widths of each column of the layout matrix
        rel_heights : np.array (vector)
            list of relative heights of each row of the layout matrix

        Returns
        -------
        area object
            area object of ``_type`` = "relative"
        """
        rel_widths = rel_widths/np.sum(rel_widths)
        rel_heights = rel_heights/np.sum(rel_heights)


        x_left = np.sum(rel_widths[:(self.x_left)])
        y_top = np.sum(rel_heights[:(self.y_top)])

        width = np.sum(rel_widths[self.x_left:(self.x_left + self.width)])
        height = np.sum(rel_heights[self.y_top:(self.y_top + self.height)])

        rel_area = area(x_left=x_left,
                        y_top=y_top,
                        width=width,
                        height=height,
                        _type="relative")
        return rel_area

    def _relative_to_pt(self, width_pt, height_pt):
        """
        translates an area object with ``_type`` = "relative" to area object
        with ``_type`` = "pt".

        Arguments
        ---------
        width_pt : float
            width in points
        height_pt : float
            height in points

        Returns
        -------
        area object
            area object of ``_type`` = "pt"
        """
        return area(x_left = self.x_left * width_pt,
                    y_top = self.y_top * height_pt,
                    width = self.width * width_pt,
                    height = self.height * height_pt,
                    _type = "pt")

    def pt(self,
           width_pt=None,
           height_pt=None,
           rel_widths=None,
           rel_heights=None
           ):
        """
        Translates area object to ``_type`` = "pt"

        Arguments
        ---------
        width_pt : float
            width in points (required if ``_type`` is not "pt")
        height_pt : float
            height in points (required if ``_type`` is not "pt")
        rel_widths : np.array (vector)
            list of relative widths of each column of the layout matrix
            (required if ``_type`` is "design")
        rel_heights : np.array (vector)
            list of relative heights of each row of the layout matrix
            (required if ``_type`` is "design")

        Returns
        -------
        area object
            area object of ``_type`` = "pt"
        """
        if self._type == "design":
            rel_area = self._design_to_relative(rel_widths = rel_widths,
                                                rel_heights = rel_heights)
            return rel_area.pt(width_pt = width_pt, height_pt = height_pt)
        elif self._type == "relative":
            return self._relative_to_pt(width_pt = width_pt,
                                        height_pt = height_pt)
        elif self._type == "pt":
            return copy.deepcopy(self)
        else:
            raise ValueError("_type attributes altered to a non-acceptable"+
                             " value")

    def _hash(self):
        """
        replacement function for ``__hash__`` due to equality conflicts

        Notes
        -----
        required since we defined ``__eq__`` and this conflicts with the
        standard ``__hash__``
        """
        return hash((self.x_left, self.y_top,
                     self.width, self.height,
                     self._type))

    def __str__(self):
        return "<area (%d)>" % self._hash()

    def __repr__(self):
        out = "_type: " + self._type +\
            "\n\nx_left: " +\
            self.x_left.__str__() +\
            "\ny_top: " +\
            self.y_top.__str__() +\
            "\nwidth: " +\
            self.width.__str__() +\
            "\nheight: " +\
            self.height.__str__()
        return self.__str__() + "\n" + out

    def __eq__(self, value):
        return type(self) == type(value) and \
            np.allclose(np.array([self.x_left, self.y_top,
                                self.width, self.height]),
                      np.array([value.x_left, value.y_top,
                                value.width, value.height])) and \
            self._type == value._type
