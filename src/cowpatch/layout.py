import re
import numpy as np
import warnings
import copy
from .utils import is_pos_int, is_non_neg_int, \
                is_proportion, is_positive, is_non_negative

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
        layout class to store information about arangement of patches

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
            Notes.
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

        Notes
        -----
        The `design` parameter expects specific input.

        1. If the `design` is input as a numpy array, we expect it to have
        integers only (0 to # patches-1). It is allowed to have `np.nan` values
        if certain "squares" of the  layout are not covered by others (the
        covering is defined by the value ordering). Note that we won't check
        for overlap and `np.nan` is not enforced if another patches' relative
        (min-x,min-y) and (max-x, max-y) define a box over that `np.nan`'s
        area.

        An example of a design of the numpy array form could look like

        .. code-block::

                my_np_design = np.array([[1,1,2],
                                         [3,3,2],
                                         [3,3,np.nan]])


        2. if the `design` parameter takes in a string, we expect it to have
        a structure such that each line (pre "\\n") contains the same number
        of characters, and these characters must come from the first
        (# patches-1) capital alphabetical characters or the "#" or "." sign to
        indicate an empty square. Similar arguments w.r.t. overlap and the
        lack of real enforcement for empty squares applies (as in #1).

        An example of a design of the string form could look like

        .. code-block::

                my_str_design = \"\"\"
                AAB
                CCB
                CC#
                \"\"\"

        or

        .. code-block::

                my_str_design = \"\"\"
                AAB
                CCB
                CC.
                \"\"\"


        **Similarities to `R` cousins:**

        This layout function is similar to `patchwork::plot_layout` (with a
        special node to `design` parameter) and helps perform similar ideas to
        `gridExtra::arrangeGrob`'s `layout_matrix` parameter, and
        `cowplot::plot_grid`'s `rel_widths` and `rel_heights` parameters
        """
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
        self.rel_widths = np.array(rel_widths)
        self.rel_heights = np.array(rel_heights)
        self.num_items = self._assess_mat(design)

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
            indices between 0 to (# patches - 1)
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

    def _element_locations(self, width_px, height_px):
        """
        create a list of `area` objects associated with the location of
        each of the layout's grobs w.r.t. a given pixel width and height

        Arguments
        ---------
        width_px : float
            global width (in pixels) of the full arangement of patches
        height_px : float
            global height (in pixels) of the full arangement of patches

        Returns
        -------
        list
            list of `area` objects describing the location for each of the
            layout's grobs (in the order of the index in the self.design)
        """
        areas = []

        for p_idx in np.arange(self.num_items):
            dmat_logic = self.design == p_idx
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
            areas.append(inner_design_area.px(rel_widths=self.rel_widths,
                                              rel_heights=self.rel_heights,
                                              width_px=width_px,
                                              height_px=height_px))

        return areas

    def _yokogaki_ordering(self):
        """
        calculates the yokogaki (left to right, top to bottom) ordering
        the the patches

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
        areas = self._element_locations(1,1) # basically getting relative positions (doesn't matter) - nor does it matter about rel_height and width, but ah well
        all_x_left = np.array([a.x_left for a in areas])
        all_y_top = np.array([a.y_top for a in areas])
        index_list = np.arange(self.num_items)

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
        info_list = list(self.design.ravel()) + \
            list(self.rel_widths) + list(self.rel_heights) +\
            [self.ncol, self.nrow, self.num_items]
        return abs(hash(tuple(info_list)))

    def __repr__(self):
        return "<layout (%d)>" % self.__hash__()

    def __str__(self):
        out = "design (%i, %i):\n\n"% (self.nrow, self.ncol) +\
            self.design.__str__() +\
            "\n\nwidths:\n" +\
            self.rel_widths.__str__() +\
            "\nheights:\n" +\
            self.rel_heights.__str__()
        return self.__repr__() + "\n" + out

    def __eq__(self, value):
        return np.allclose(self.design,value.design,equal_nan=True) and \
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
        area class that stores information about what area a patch will fill

        Arguments
        ---------
        x_left : float
            scalar of where the left-most point of the patch is located (impacted
            by the `_type` parameter)
        y_top : float
            scalar of where the top-most point of the patch is located (impacted
            by the `_type` parameter)
        width : float
            scalar of the width of the patch (impacted by the `_type` parameter)
        height : float
            scalar of the height of the patch (impacted by the `_type` parameter)
        _type : str {"design", "relative", "px"}
            describes how the parameters are stored. See Notes for more information
            between the options.

        Notes
        -----
        The `_type` parameter informs how to understand the other parameters:

        1. "design" means that the values are w.r.t. to a design matrix
        relative to the `layout` class, and values are relative to the rows
        and columns units.

        2. "relative" means the values are defined relative to the full size of
        the canvas and taking values between 0-1 (inclusive).

        3. "px" means that values are defined relative to pixel values
        """

        # some structure check:
        self._check_info_wrt_type(x_left, y_top, width, height, _type)

        self.x_left = x_left
        self.y_top = y_top
        self.width = width
        self.height = height
        self._type = _type

    def _check_info_wrt_type(self, x_left, y_top, width, height,_type):
        """
        some logic checks of inputs relative to `_type` parameter

        Arguments
        ---------
        x_left : float
            scalar of where the left-most point of the patch is located
            (impacted by the `_type` parameter)
        y_top : float
            scalar of where the top-most point of the patch is located
            (impacted by the `_type` parameter)
        width : float
            scalar of the width of the patch (impacted by the `_type`
            parameter)
        height : float
            scalar of the height of the patch (impacted by the `_type`
            parameter)
        _type : str
            describes how the parameters are stored. Options include
            ["design", "relative", "px"]. See class docstring for more info

        Raises
        ------
        ValueError
            if any of the first four parameters don't make sense with respect
            to the `_type` parameter
        """

        if _type not in ["design", "relative", "px"]:
            raise ValueError("_type parameter not an acceptable option, see"+\
                             " documentation")

        if _type == "design" and \
            not np.all([is_non_neg_int(val) for val in [x_left,y_top]] +\
                       [is_pos_int(val) for val in [width,height]]) :
            raise ValueError("with _type=\"design\", all parameters must be "+\
                             "positive integers")
        elif _type == "relative" and \
            not np.all([is_proportion(val) for val in [x_left,y_top,
                                                       width,height]] +\
                       [is_positive(val) for val in [width,height]]):
            raise ValueError("with _type=\"relative\", all parameters should"+\
                             " be between 0 and 1 (inclusive) and width and"+\
                             " height cannot be 0")
        elif _type == "px" and \
            not np.all([is_non_negative(val) for val in [x_left,y_top]] +\
                       [is_positive(val) for val in [width,height]]):
            raise ValueError("with _type=\"px\", all x_left and y_top should"+\
                             " be non-negative and width and height should"+\
                             " be strictly positive")


    def _design_to_relative(self, rel_widths, rel_heights):
        """
        translates an area object with `_type` = "design" to area object
        with `_type` = "relative".

        Arguments
        ---------
        rel_widths : np.array (vector)
            list of relative widths of each column of the layout matrix
        rel_heights : np.array (vector)
            list of relative heights of each row of the layout matrix

        Returns
        -------
        area object
            area object of `_type` = "relative"
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

    def _relative_to_px(self, width_px, height_px):
        """
        translates an area object with `_type` = "relative" to area object
        with `_type` = "px".

        Arguments
        ---------
        width_px : float
            width in pixels
        height_px : float
            height in pixels

        Returns
        -------
        area object
            area object of `_type` = "px"
        """
        return area(x_left = self.x_left * width_px,
                    y_top = self.y_top * height_px,
                    width = self.width * width_px,
                    height = self.height * height_px,
                    _type = "px")

    def px(self,
           width_px=None,
           height_px=None,
           rel_widths=None,
           rel_heights=None
           ):
        """
        Translates area object to `_type` = "px"

        Arguments
        ---------
        width_px : float
            width in pixels (required if `_type` is not "px")
        height_px : float
            height in pixels (required if `_type` is not "px")
        rel_widths : np.array (vector)
            list of relative widths of each column of the layout matrix
            (required if `_type` is "design")
        rel_heights : np.array (vector)
            list of relative heights of each row of the layout matrix
            (required if `_type` is "design")

        Returns
        -------
        area object
            area object of `_type` = "px"
        """
        if self._type == "design":
            rel_area = self._design_to_relative(rel_widths = rel_widths,
                                                rel_heights = rel_heights)
            return rel_area.px(width_px = width_px, height_px = height_px)
        elif self._type == "relative":
            return self._relative_to_px(width_px = width_px,
                                        height_px = height_px)
        elif self._type == "px":
            return copy.deepcopy(self)
        else:
            raise ValueError("_type attributes altered to a non-acceptable"+\
                             " value")

    def _hash(self):
        """
        replacement function for `__hash__` due to equality conflicts

        Notes
        -----
        required since we defined `__eq__` and this conflicts with the
        standard `__hash__`
        """
        return hash((self.x_left, self.y_top,
                     self.width, self.height,
                     self._type))

    def __repr__(self):
        return "<area (%d)>" % self._hash()

    def __str__(self):
        out = "_type: " + self._type +\
            "\n\nx_left: " +\
            self.x_left.__str__() +\
            "\ny_top: " +\
            self.y_top.__str__() +\
            "\nwidth: " +\
            self.width.__str__() +\
            "\nheight: " +\
            self.height.__str__()
        return self.__repr__() + "\n" + out

    def __eq__(self, value):
        return type(self) == type(value) and \
            np.allclose(np.array([self.x_left, self.y_top,
                                self.width, self.height]),
                      np.array([value.x_left, value.y_top,
                                value.width, value.height])) and \
            self._type == value._type
