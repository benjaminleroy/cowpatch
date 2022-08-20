import numpy as np
import plotnine as p9
import matplotlib.pyplot as plt
import svgutils.transform as sg
import copy

from .svg_utils import gg_to_svg, _save_svg_wrapper, _show_image, \
                    _raw_gg_to_svg, _select_correcting_size_svg
from .utils import to_inches, from_inches, inherits_plotnine, inherits, \
                    _flatten_nested_list
from .layout_elements import layout
from .annotation_elements import annotation
from .config import rcParams
from .text_elements import text

import pdb

class patch:
    def __init__(self, *args, grobs=None):
        """
        fundamental object of `cowpatch`, encapsulates plot objects and
        can be told how to present them

        Arguments
        ---------
        \*args : plot objects and patches
            all non-named parameters are expected to be plot objects or
            lower-level ``cow.patch`` objects.
        grobs : list
            list of plot objects and patches. Either ``\*args`` is empty or
            ``grobs`` is ``None``.


        Notes
        -----

        *Guiding arangement:*

        In combination with ``cow.layout`` one can define arrangement of plots
        and lower-level arangements.

        For example,

        >>> vis_obj = cow.patch(g1,g2,g3)
        >>> vis_obj += cow.layout(design = np.array([[0,1],
        ...                                          [2,2]]))
        >>> vis_obj.show()

        See the `Layout guide`_ for more detailed examples of functionality.

        .. _Layout guide: https://benjaminleroy.github.io/cowpatch/guides/Layout.html

        *Nesting:*

        One can nest `cow.patch` objects within other `cow.patch` objects. For
        example,

        >>> vis_obj2 = cow.patch(g4, vis_obj)
        >>> vis_obj2 += cow.layout(nrow = 1)
        >>> vis_obj2.show()

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

        >>> # Basic example:
        >>> vis_obj = cow.patch(g0,g1,g2)
        >>> vis_obj += cow.layout(design = np.array([[0,1],
        ...                                          [2,2]]))
        >>> vis_obj.show()

        >>> # Nesting example:
        >>> vis_obj2 = cow.patch(g3, vis_obj)
        >>> vis_obj2 += cow.layout(nrow = 1)
        >>> vis_obj2.show()

        See Also
        --------
        layout : class objects that can aid in defining the layout of plots in
            ``cow.patch`` objects
        """
        future_docstring = """

        *Algebraic Combinations:*

        *Titles and Labels:*
        """

        # put *args into a list
        args_grobs = [x for x in args]
        if len(args_grobs) > 0:
            if grobs is not None:
                raise ValueError("cannot input a grobs list"+\
                                 " as well as individual plots")
            else:
                self.grobs = args_grobs
        else:
            self.grobs = grobs

        self.__layout = "patch" # this is different than None...
        self.annotation = None

    @property
    def layout(self):
        """
        defines ``layout`` that either returns the last added ``cow.layout``
        object or the default ``layout`` if no layout has been explicitly
        defined
        """
        if self.__layout == "patch":
            if len(self.grobs) < 4:
                return layout(nrow = len(self.grobs), ncol = 1)
            else:
                num_grobs = len(self.grobs)
                nrow = int(np.ceil(np.sqrt(num_grobs)))
                ncol = int(np.ceil(len(self.grobs) / nrow))

                return layout(nrow=nrow, ncol=ncol)
        else:
            return self.__layout

    def _check_layout(self):
        """
        checks layout if design matrix is fulled defined
        """
        if self.layout.num_grobs is not None:
           if self.layout.num_grobs != len(self.grobs):
            raise AttributeError("layout's number of patches does not "+\
                                 "matches number of patches in arangement")

    def __or__(self, other):
        # check proper usage -------
        if not inherits(other, patch):
            raise ValueError("only can connect specific general patch items"+\
                             " with \"|\".")

        # combine with other -------
        if self.layout is None:
            # only for wrappers!
            return patch(grobs=[self, other]) + layout(ncol=2,nrow=1)
        elif self.layout == layout(design = np.array([[0]])):
            # current self is [inner]
            return patch(grobs=self.grobs+[other]) + layout(ncol=2,nrow=1)
        elif self.layout.nrow == 1:
            # continuing a row
            return patch(grobs=self.grobs+[other]) + layout(nrow = 1, ncol = len(self.grobs)+1)
        else:
            return patch(grobs=[self.grobs]+[other]) + layout(ncol=2,nrow=1)

    def __div__(self, other):
        # check proper usage -------
        if not inherits(other, patch):
            raise ValueError("only can connect specific general patch items"+\
                             " with \"/\".")

        # combine with other -------
        if self.layout is None:
            # only for wrappers!
            return patch(grobs=[self, other]) + layout(ncol=1,nrow=2)
        elif self.layout == layout(design = np.array([[0]])):
            # current self is [inner]
            return patch(grobs=self.grobs+[other]) + layout(ncol=1,nrow=2)
        elif self.layout.nrow == 1:
            # continuing a row
            return patch(grobs=self.grobs+[other]) + layout(nrow = len(self.grobs)+1, ncol = 1)
        else:
            return patch(grobs=[self.grobs]+[other]) + layout(ncol=2,nrow=1)

    def __add__(self, other):
        # check proper usage -------
        if not (inherits(other, patch) or \
            inherits(other, layout) or \
            inherits(other, annotation)):
            if inherits(other,p9.theme):
                raise ValueError("cannot directly add a theme to a patch" +\
                                 " object unless a wrapper, try \"&\" or \"*\"")
            raise ValueError("only can connect specific general patch items"+\
                             " with \"/\".")

        if inherits(other, patch):
            # combine with other patch -------
            if self.layout is None:
                # only for wrappers!
                return patch(grobs=[self, other])
            elif self.layout == layout(design = np.array([[0]])):
                # current self is [inner]
                return patch(grobs=self.grobs+[other])
            elif self.layout.nrow == 1:
                # continuing a row
                return patch(grobs=self.grobs+[other])
            else:
                return patch(grobs=[self.grobs]+[other])
        elif inherits(other, layout):
            # combine with layout -------------
            self.__layout = other
        elif inherits(other, annotation):
            if self.annotation is None:
                other_copy = copy.deepcopy(other)
                other_copy._clean_up_attributes()
                self.annotation = other_copy
            else:
                final_copy = copy.deepcopy(self.annotation + other)
                final_copy._clean_up_attributes()
                self.annotation = final_copy

        return self

    def __mul__(self, other):
        raise ValueError("currently not implimented *")

    def __and__(self, other):
        raise ValueError("currently not implimented &")

    def _get_grob_tag_ordering(self):
        """
        get ordering of tags related to grob index

        Returns
        -------
        numpy array of tag order for each grob

        Note
        ----
        This function leverages the patch's layout and annotation objects
        """
        self._check_layout()

        if self.annotation is None or self.annotation.tags is None:
            return np.array([])

        tags_order = self.annotation.tags_order
        if tags_order == "auto":
            if inherits(self.annotation.tags,list):
                tags_order = "input"
            else:
                tags_order = "yokogaki"


        if tags_order == "yokogaki":
            return self.layout._yokogaki_ordering(num_grobs = len(self.grobs))
        elif tags_order == "input":
            return np.arange(len(self.grobs))
        else:
            raise ValueError("patch's annotation's tags_order is not an expected option")


    def _svg(self, width_pt, height_pt, sizes=None, num_attempts=None):
        """
        Internal function to create an svg representation of the patch

        Arguments
        ---------
        width_pt : float
            desired width of svg object in points
        height_pt : float
            desired height of svg object in points
        sizes: TODO: write description
        num_attempts : TODO: write description

        Returns
        -------
        svg_object : ``svgutils.transforms`` object

        See also
        --------
        svgutils.transforms : pythonic svg object
        """

        self._check_layout()

        # examine if sizing is possible and update or error if not
        # --------------------------------------------------------
        if sizes is None: # top layer
            sizes = self._svg_get_sizes(width_pt, height_pt)


        layout = self.layout

        areas = layout._element_locations(width_pt=width_pt,
                                          height_pt=height_pt,
                                          num_grobs=len(self.grobs))

        base_image = sg.SVGFigure()
        base_image.set_size((str(width_pt)+"pt", str(height_pt)+"pt"))
        # add a view box... (set_size doesn't correctly update this...)
        # maybe should have used px instead of px....
        base_image.root.set("viewBox", "0 0 %s %s" % (str(width_pt), str(height_pt)))

        # TODO: way to make decisions about the base image...
        # TODO: this should only be on the base layer...
        base_image.append(
            sg.fromstring("<rect width=\"100%\" height=\"100%\" fill=\"#FFFFFF\"/>"))

        for p_idx in np.arange(len(self.grobs)):
            inner_area = areas[p_idx]
            # TODO: how to deal with ggplot objects vs patch objects
            if inherits(self.grobs[p_idx], patch):
                inner_width_pt, inner_height_pt = inner_area.width, inner_area.height
                inner_svg, _ = self.grobs[p_idx]._svg(width_pt = inner_width_pt,
                                                   height_pt = inner_height_pt,
                                                   sizes =  sizes[p_idx])
            elif inherits_plotnine(self.grobs[p_idx]):
                inner_gg_width_in, inner_gg_height_in  = sizes[p_idx]
                inner_svg = _raw_gg_to_svg(self.grobs[p_idx],
                                      width = inner_gg_width_in,
                                      height = inner_gg_height_in,
                                      dpi = 96)
            else:
                raise ValueError("grob idx %i is not a patch object nor"+\
                                 "a ggplot object within patch with hash %i" % p_idx, self.__hash__)


            inner_root = inner_svg.getroot()

            inner_root.moveto(x=inner_area.x_left,
                              y=inner_area.y_top)
            base_image.append(inner_root)

        return base_image, (width_pt, height_pt)

    def _estimate_default_min_desired_size(self, parent_index=()):
        """
        (Internal) Estimate default height and width of full image so that
        inner objects (plots, text, etc.) have a minimum desirable size
        and all titles are fully seen.

        Arguments
        ---------
        parent_index : int
            parent level index information

        Returns
        -------
        suggested_width : float
            proposed width for overall size (inches)
        suggested_height : float
            proposed height for overall size (inches)

        Notes
        -----
        ***Function's logic***:
        In order to propose a minimum sizing to an arrangement we take two
        things into account. Specially,

        1. we assure that each plot's height & width are greater then or equal
        to a minimum plot height and width (For text objects treated as plots,
        we just assure they are not truncated, with no minimize sizing is
        enforced).
        2. and for titles (,subtitles, captions,) and tags, we ensure that
        they will not be truncated based on the sizing of the plot/arrangement
        they are associated with.

        To accomplish this second goal, we track different dimensions of these
        text labeling objects. For clarity, define (1) a text object’s
        *typographic length* as the maximum width of all lines of and with
        each line’s text’s baseline being horizontal and a text object’s
        *typographic overall height* as the distance between the top “line” of
        text’s ascender line and the bottom "line" of text's descender line
        `reference <https://stackoverflow.com/questions/25520410/when-setting-a-font-size-in-css-what-is-the-real-height-of-the-letters>`_,
        and (2) a *bounding box* for any text object is the minimum sized box
        that can contain the text object. This bounding box has a *height* and
        *width* which is naturally impacted by the orientation of baseline of
        the text.


        For titles (,subtitles, captions,) and tags of tag_type = 0 (aka the
        tag is drawn outside the underlying plot/arrangement's space), we do
        the following:

        A. we make sure the associated plot/arangement’s requested height and
        weight ensures that the text object's *typographic length* is not
        truncated. To do so we assure that the plot-specific height and width
        being larger than max(image_min_height_from_objective_1, select_bbox_heights))
        and max(image_min_width_from_objective_1,select_bbox_widths)).  A text
        element contributes to the select_bbox_heights if it has left or right
        alignment and to select_bbox_widths if it has top or bottom alignment.
        B. we make sure the "global" location for said inner plot/arrangement
        and text greater than or equal to the the plot’s minimum sizing
        defined in (A) plus a selected_cumulative_extra_bbox_height and _width.
        A text element contributes to the selected_cumulative_extra_bbox_height
        if it has top or bottom alignment and to
        selected_cumulative_extra_bbox_width if it has  left or right
        alignment. Note that different types of titles and tags contribute to
        this valve in an addition sense.

        If a tag has tag_type=1, then all it's bounding box’s attributes
        contribute to the dimensions described in (A).

        ***Additional info:***
        The default rcParams are (in inches):
            base_height = 3.71,
            base_aspect_ratio = 1.618 # the golden ratio

        The idea of a minimum size for a subplot follows ideas proposed in
        cowplot: `wilkelab.org/cowplot/reference/save_plot.html <https://wilkelab.org/cowplot/reference/save_plot.html>`_.

        """

        min_image_height = rcParams["base_height"]
        min_image_width = rcParams["base_aspect_ratio"] * min_image_height

        ## dealing with titles
        if self.annotation is None:
            min_desired_widths = []
            extra_desired_widths = []
            min_desired_heights = []
            extra_desired_heights = []
        else:
            min_desired_widths, extra_desired_widths, \
                min_desired_heights, extra_desired_heights = \
                    self.annotation._calculate_margin_sizes(to_inches=True)

        # inner objects
        areas = self.layout._element_locations(width_pt=1,
                                               height_pt=1,
                                               num_grobs = len(self.grobs))

        if (self.annotation is not None) and \
            (self.annotation.order_type() == "yokogaki"):
            grob_tag_ordering = self.layout._yokogaki_ordering(
                                                num_grobs=len(self.grobs))
        else:
            grob_tag_ordering = np.arange(len(self.grobs))


        for g_idx in np.arange(len(self.grobs)):
            inner_area = areas[g_idx]
            current_index = tuple(list(parent_index) + \
                                        [grob_tag_ordering[g_idx]])
            ### tag sizing -----------
            if self.annotation is not None:
                tag_min_desired_widths, tag_extra_desired_widths, \
                    tag_min_desired_heights, tag_extra_desired_heights = \
                        self.annotation._calculate_tag_margin_sizes(
                            index = current_index,
                            fundamental = inherits(self.grobs[g_idx], patch),
                            to_inches=True)
            else:
                tag_min_desired_widths, tag_extra_desired_widths, \
                    tag_min_desired_heights, tag_extra_desired_heights = [0],[0],[0],[0]


            ### object sizing -------------
            if inherits_plotnine(self.grobs[g_idx]):
                inner_width = min_image_width
                inner_height = min_image_height
            elif inherits(self.grobs[g_idx], text):
                inner_width, inner_height = self.grobs[g_idx]._min_size(to_inches=True)
            else: # patch object...
                inner_width, inner_height = \
                    self.grobs[g_idx]._estimate_default_min_desired_size(parent_index=current_index)


            min_desired_widths.append((np.max([inner_width]+tag_min_desired_widths) +\
                                       tag_extra_desired_widths)*\
                                        1/inner_area.width)
            min_desired_heights.append((np.max([inner_height]+tag_min_desired_heights) +\
                                        tag_extra_desired_heights) *\
                                        1/inner_area.height)


        # wrap it all up (zeros added to allow for empty sets)
        min_desired_width = np.max(min_desired_widths+[0]) +\
                                np.sum(extra_desired_widths+[0])
        min_desired_height = np.max(min_desired_heights+[0]) +\
                                np.sum(extra_desired_heights+[0])

        return min_desired_width, min_desired_height

    def _default_size(self, width, height):
        """
        (Internal) obtain default recommended size of overall image if width or
        height is None

        Arguments
        ---------
        width : float
            width of output image in inches (this should actually be associated
            with the svg...)
        height : float
            height of svg in inches (this should actually be associated
            with the svg...)

        Returns
        -------
        width : float
            returns default width for given object if not provided (else just
            returns provided value). If only height is provided then width
            proposed is relative to a default aspect ratio for the object.
        height : float
            returns default height for given object if not provided (else just
            returns provided value). If only width is provided then height
            proposed is relative to a default aspect ratio for the object.
        """
        both_none = False
        if width is None or height is None:
            _width, _height = self._estimate_default_min_desired_size()#self._size_dive()
            if width is None and height is None:
                both_none = True
                width = _width
                height = _height
            elif width is not None:
                height = _height / _width * width
            else:
                width = _width / _height * height
        return width, height

    def _inner_svg_get_sizes(self, width_pt, height_pt, tag_parent_index=()):
        """
        (Internal) Calculates required sizes for plot objects to meet required
        sizes and logics if the requested sizing was possible

        Arguments
        ---------
        width_pt : float
            overall width of the image in points
        height_pt : float
            overall height of the image in points
        tags_parent_index : tuple
            tuple of integers that contain the relative level indices of the
            desired tag for parent.

        Returns
        -------
        sizes : nested list
            For each element in the patch (with nesting structure in the list),
            this contains width, height tuples that either capture the size
            to request the ggplot object to be to return the actual desired
            size (see gg_to_svg notes), OR it contains the fraction defined by
            the requested width (or height) w.r.t. the returned width
            (or height) from saving the plotnine object. The later option
            occurs when when the ggplot's sizing didn't converge to the
            desired size. These sizing do not contain information about
            annotations (but implicitly reflect them existing)
        logics : nested list
            For each element in the patch (with nesting structure in the list),
            this contains a boolean value if the ggplot object was able to
            be correctly size.
        sizes_text : nested list
        logics_text : nested list

        Notes
        -----
        Internally this function uses rcParams's ``eps``, ``mini_size_px`` and
        ``maxIter`` to determine the parameters to be put in
        .svg_utils._select_correcting_size_svg.
        """
        layout = self.layout

        areas = layout._element_locations(width_pt=width_pt,
                                          height_pt=height_pt,
                                          num_grobs=len(self.grobs))

        sizes = []
        logics = []
        sizes_annotation = []
        logics_annotation = []

        for p_idx in np.arange(len(self.grobs)):
            inner_area = areas[p_idx]
            inner_width_pt = inner_area.width
            inner_height_pt = inner_area.height

            if inherits(self.grobs[p_idx], patch):
                inner_sizes_list, logic_list = \
                    self.grobs[p_idx]._inner_svg_get_sizes(width_pt = inner_width_pt,
                                                 height_pt = inner_height_pt)
                sizes.append(inner_sizes_list)
                logics.append(logic_list)
            elif inherits_plotnine(self.grobs[p_idx]):
                inner_w, inner_h, inner_logic = \
                    _select_correcting_size_svg(self.grobs[p_idx],
                                      width=to_inches(inner_width_pt,
                                                        units="pt",
                                                        dpi=96),
                                      height=to_inches(inner_height_pt,
                                                        units="pt",
                                                        dpi=96),
                                      dpi=96,
                                      eps=rcParams["eps"],
                                      min_size_px=rcParams["min_size_px"],
                                      maxIter=rcParams["maxIter"],
                                      throw_error=False)
                sizes.append((inner_w,inner_h))
                logics.append(inner_logic)
            elif inherits(self.grobs[p_idx], text):
                raise ValueError("TODO!")
            else:
                raise ValueError("grob idx %i is not a patch object nor"+\
                                 "a ggplot object" % p_idx)

        return sizes, logics

    def _svg_get_sizes(self, width_pt, height_pt):
        """
        captures backend process of making sure the sizes requested can be
        provided with the actual images...
        """

        if num_attempts is None:
            num_attempts = rcParams["num_attempts"]

        while num_attempts > 0:
            sizes, logics = self._svg_get_sizes(width_pt=width_pt,
                                                height_pt=height_pt)
            out_info = self._process_sizes(sizes, logics)

            if type(out_info) is list:
                num_attempts = -412 # strictly less than 0
            else: # out_info is a scaling
                width_pt = width_pt*out_info
                height_pt = height_pt*out_info

            num_attempts -= 1

        if num_attempts == 0:
            raise StopIteration("Attempts to find the correct sizing of inner"+\
                        "plots failed with provided parameters")

        return sizes

    def _process_sizes(self, sizes, logics):
        """
        (Internal) draw conclusions about the output of _svg_get_sizes.

        This function assesses if any internal ggplot object failed to
        produce an image of the requested size (w.r.t. to given interation
        parameters)

        Arguments
        ---------
        sizes : nested list
            sizes output of _svg_get_sizes. This is a nested list with
            (width,height) or (requested_width/actual_width,
            requested_height/actual_width), with the different being if the
            ggplot object was able to be presented in the requested size
        logics : nested list
            logics output of _svg_get_sizes. This is a nested list of boolean
            values w.r.t. the previous different.

        Returns
        -------
        sizes : nested list
            Returned if no logics values are False. This object is the sizes
            nested list that was input.
        max_scaling : float
            Returned if at least one of the logics values are False. This is
            the scaling of the original ``width_pt`` and ``height_pt`` that
            defined the sizes and logics that could make the requested sizes
            for all ggplots that failed to be correctly sized be at least as
            large as the returned size from a basic ggplot saving.
        """
        flatten_logics = _flatten_nested_list(logics)
        if np.all(flatten_logics):
            return sizes

        # else suggest a rescale:
        flatten_sizes = _flatten_nested_list(sizes)
        bad_sizing_info = [flatten_sizes[i] for i in range(len(flatten_sizes))
            if not flatten_logics[i]]

        width_scaling = 1/np.min([sizing[0] for sizing in bad_sizing_info])
        height_scaling = 1/np.min([sizing[1] for sizing in bad_sizing_info])

        max_scaling = np.max([width_scaling, height_scaling])
        # ^ keeping aspect ratio with a single scaling

        return max_scaling

    def save(self, filename, width=None, height=None, dpi=96, _format=None,
             verbose=None):
        """
        save patch to file

        Arguments
        ---------
        filename : str
            local string to save the file to (this can also be at a
            ``io.BytesIO``)
        width : float
            width of output image in inches (this should actually be associated
            with the svg...)
        height : float
            height of svg in inches (this should actually be associated
            with the svg...)
        dpi : int or float
            dots per square inch, default is 96 (standard)
        _format : str
            string of format (error tells options). If provided this is the
            format used, if None, then we'll try to use the ``filename``
            extension.
        verbose : bool
            If ``True``, print the saving information. The package default
            is defined by cowpatch's own rcParams (the base default is
            ``True``), which is used if verbose is ``None``. See Notes.

        Returns
        -------
        None
            saves to a file

        Notes
        -----
        If width and/or height is None, the approach will attempt to define
        acceptable width and height.

        The ``verbose`` parameter can be changed either directly with defining
        ``verbose`` input parameter or changing
        ``cow.rcParams["save_verbose"]``.

        See also
        --------
        io.BytesIO : object that acts like a reading in of bytes
        """
        # updating width and height if necessary (some combine is none)
        width, height = self._default_size(width=width, height=height)

        # global default for verbose (if not provided by the user)
        if verbose is None:
            verbose = rcParams["save_verbose"]

        svg_obj, (actual_width_pt, actual_height_pt) = \
            self._svg(width_pt = from_inches(width, "pt", dpi=dpi),
                            height_pt = from_inches(height, "pt", dpi=dpi))

        _save_svg_wrapper(svg_obj,
                           filename=filename,
                           width=to_inches(actual_width_pt, "pt", dpi=dpi),
                           height=to_inches(actual_height_pt, "pt", dpi=dpi),
                           dpi=dpi,
                           _format=_format,
                           verbose=verbose)

    def show(self, width=None, height=None, dpi=96, verbose=None):
        """
        display object from the command line or in a jupyter notebook

        Arguments
        ---------
        width : float
            width of output image in inches (this should actually be associated
            with the svg...)
        height : float
            height of svg in inches (this should actually be associated
            with the svg...)
        dpi : int or float
            dots per square inch, default is 96 (standard)
        verbose : bool
            If ``True``, print the saving information. The package default
            is defined by cowpatch's own rcParams (the base default is
            ``True``), which is used if verbose is ``None``. See Notes.

        Notes
        -----
        If width and/or height is None, the approach will attempt to define
        acceptable width and height.

        The ``verbose`` parameter can be changed either directly with defining
        ``verbose`` input parameter or changing
        ``cow.rcParams["show_verbose"]``.

        If run from the command line, this approach leverage matplotlib's
        plot render to show a static png version of the image. If run inside
        a jupyter notebook, this approache presents the actual svg
        representation.
        """
        # updating width and height if necessary (some combine is none)
        width, height = self._default_size(width=width, height=height)

        # global default for verbose (if not provided by the user)
        if verbose is None:
            verbose = rcParams["show_verbose"]

        svg_obj, (actual_width_pt, actual_height_pt) = \
            self._svg(width_pt = from_inches(width, "pt", dpi=dpi),
                       height_pt = from_inches(height, "pt", dpi=dpi))

        _show_image(svg_obj,
                    width=to_inches(actual_width_pt, "pt", dpi=dpi),
                    height=to_inches(actual_height_pt, "pt", dpi=dpi),
                    dpi=dpi,
                    verbose=verbose)

    def __str__(self):
        self.show()
        return "<patch (%d)>" % self.__hash__()

    def __repr__(self):
        out = "num_grobs: " + str(len(self.grobs)) +\
            "\n---\nlayout:\n" + self.layout.__repr__()+\
            "\n---\nannotation:\n" + self.annotation.__repr__()

        return "<patch (%d)>" % self.__hash__() + "\n" + out
