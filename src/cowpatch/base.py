import numpy as np
import plotnine as p9
import re
from PIL import Image
import matplotlib.pyplot as plt
from .utils import val_range
from .image_utils import gg2img

class layout:
    def __init__(self,
                 ncol=None, # patchwork::plot_layout, gridExtra::arrangeGrob
                 nrow=None, # patchwork::plot_layout, gridExtra::arrangeGrob
                 design=None, # gridExtra::arrangeGrob (layout_matrix), atchwork::plot_layout
                 #byrow=None, # patchwork::plot_layout
                 widths=None, # patchwork::plot_layout, list
                 heights=None, # patchwork::plot_layout, list
                 #guides=None, # patchwork::plot_layout
                 #tag_level=None, # patchwork::plot_layout
                 #design=None # patchwork::plot_layout
                 ):
        """
        This class stores information about layouts

        design: matrix or string
            e.g. np.array([[None, 0, 0],[1,1, None]]): (None) means blank in matrix
            or
            "#AA\nBB#": ("#") means blank in string
        """

        # https://patchwork.data-imaginist.com/articles/guides/layout.html

        # compared to cowplot::plot_grid
        # no align / axis (they're duplicated of ncol/nrow)
        # also rel_widths and rel_heights are just width/heights

        if design is not None:
            # this should just be a message
            assert ncol is None and nrow is None, \
                "if providing a design, ncol and nrow are overridden"

            if isinstance(design, np.ndarray):
                if len(design.shape) == 1:
                    row, ncol = 1, design.shape[0] # TODO: add comment about this
                    design = design.reshape((1,-1))
                else:
                    nrow, ncol = design.shape
            if isinstance(design, str):
                # convert design to desirable structure matrix structure
                design, nrow, ncol = self._design_string2mat(design)

        # TODO: check here that all integers 0-max are included...
        # TODO: also track this number

        if ncol is None:
            if widths is not None:
                if isinstance(widths, np.ndarray):
                    ncol = widths.shape[0]
                if isinstance(widths, list):
                    ncol = len(widths)
                    widths = np.array(widths)

        if nrow is None:
            if heights is not None:
                if isinstance(heights, np.ndarray):
                    nrow = heights.shape[0]
                if isinstance(heights, list):
                    nrow = len(heights)
                    heights= np.array(heights)

        if widths is None and heights is None:
            assert not (ncol is None and nrow is None), \
                "need some parameters to not be none in design initialization"

        if widths is None:
            widths = np.ones(ncol)
        if heights is None:
            heights = np.ones(nrow)

        if design is None:
            design = np.arange(ncol*nrow,dtype = int).reshape((nrow, ncol))

        self.ncol = ncol
        self.nrow = nrow
        self.design = design
        self.widths = widths
        self.heights = heights

    def _design_string2mat(self, design):
        """
        Internal function to convert design string into a matrix
        """
        row_info = re.split("\n", design)
        ncol_lengths = np.unique([len(x) for x in row_info])
        assert ncol_lengths.shape == (1,), \
            "expect all rows in design to have the same number of entries," +\
            "use # for an empty space if using a string format."

        ncol = int(ncol_lengths)
        nrow = len(re.findall("\n", design)) + 1

        design = np.array([[ ord(val)-65 if val != "#" else None for val in r]
                            for r in row_info])

        return design, nrow, ncol

    def __str__(self):
        out = "layout (%i, %i):\n"% (self.nrow, self.ncol) +\
            self.design.__str__() +\
            "\n\nwidths:\n" +\
            self.widths.__str__() +\
            "\nheights:\n" +\
            self.heights.__str__()
        return out
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if np.all(self.design == other.design) and \
            self.ncol == other.ncol and \
            self.nrow == other.nrow and \
            np.unique(self.heights/other.heights).shape[0] == 1 and \
            np.unique(self.widths/other.widths).shape[0] == 1:
            return True
        else:
            return False

def test_layout():
    design1 = np.array([[None, 0, 0],[1,1, None]])
    design2 = "#AA\nBB#"

    l1 = layout(design = design1)
    l2 = layout(design = design2)

    assert l2 == l1, \
        "expect string and matrix layout structure to create same matrix"

    ncol3 = 3
    nrow3 = 4

    l3 = layout(ncol = ncol3, nrow = nrow3)

    # not 100% sure what we want to test...



class annotation:
    # https://github.com/cran/gridExtra/blob/master/R/arrangeGrob.r
    # https://wilkelab.org/cowplot/articles/plot_grid.html
    # https://patchwork.data-imaginist.com/articles/guides/annotation.html
    def __init__(self, sub_labels=None):
        # need to think about how labels would work across cowplot and patchwork's approaches
        # probably with respect to ordering of grobs


class cowpatch:
    """The fundamental base class for cowpatch library"""

    def __init__(self, grobs=[]):
        """..."""

        self.grobs = grobs # these can be ggplot objects amd cowpatch objects or a single list of such things...

        self.to_process = True # if we need to process / create a png version
        self.png_obj = None # to be captured once processed (to not recreate unless necessary)
        self.layout = None
        self.depth = 1
        self.max_depth = _update_depth(self, grobs = self.grobs)


    def _update_depth(self, grobs):
        """
        This function can also be called when adding things...
        """
        max_depth = 1
        for grob in grobs:
            if inherits(grob, cowpatch):
                grob.depth += 1
                max_depth = np.max([max_depth, grob.depth])
        return max_depth


    def __str__(self):
        """convert to png and then show"""

        if self.to_process is not True:
            return self.png_obj

        self.updated = False # need to keep track of this... (and depth layering...)
        self.png_obj = _create_png(self)

        return self.png_obj.show()

    def show(self):
        if self.to_process is not True:
            return self.png_obj

        self.updated = False # need to keep track of this... (and depth layering...)
        self.png_obj = _create_png(self)

        return self.png_obj.show()

    def _create_png(self,
                    width=None,
                    height=None,
                    dpi=None,
                    limitsize=True): # should do the same check here as p9 does.., (for the global object)
        """creates png of objects"""

        units = "in"

        # setting defaults
        if width is None:
            width = plt.rcParams["figure.figsize"][0]# matplotlib default
        if height is None:
            height = plt.rcParams["figure.figsize"][1]# matplotlib default
        if dpi is None:
            dpi = plt.rcParams["figure.dpi"]
        if units is None:

        width_px = dpi*width
        height_px = dpi*height

        rel_widths = self.widths/np.sum(self.widths) * width_px
        rel_heights = self.heights/np.sum(self.widths) * height_px


        base_image = Image.new("RGB", (width_px, height_px),
                               (255,0,0,0)) # transparent color


        info_dict = self._design_to_structure(width_px, height_px,
                                              rel_widths,
                                              rel_heights)
        png_list = self._create_png_list(info_dict, dpi=dpi,
                                         limitsize=limitsize)
        # need to check index of elements...
        for vis_idx, inner_info in info_dict.items():
            inner_png = png_list[vis_idx]
            inner_png_array = np.array(inner_png)

            for s_idx, slice_info in enumerate(inner_info["slices"]):
                    inner_start = slice_info[0]

                    corrected_start = (int(np.floor(inner_start[0])),
                                       int(np.floor(inner_start[1])))

                    inner_width = slice_info[1]
                    inner_height = slice_info[2]

                    c1 = int(np.floor(inner_start[0] - inner_info["start"][0]))
                    c2 = int(c1 + np.ceil(inner_width))

                    r1 = int(np.floor(inner_start[1] - inner_info["start"][1]))
                    r2 = int(r1 + np.ceil(inner_height))

                    inner_image_array_slice = inner_png_array[r1:(r2+1), c1:(c2+1)]
                    inner_image_slice = Image.fromarray(inner_image_array_slice)

                    base_image.paste(inner_image_slice, corrected_start)

        return base_image

    def _create_png_list(self, info_dict, dpi, limitsize):
        images = []
        for g_idx_minus, grob in enumerate(self.grobs):
            g_idx = g_idx_minus + 1
            if inherits(grobs, p9.ggplot.ggplot):
                inner_png_raw = gg2img(grob,
                                       width = info_dict[g_idx]["full_size"][0]/dpi,
                                       height = info_dict[g_idx]["full_size"][1]/dpi,
                                       dpi = dpi,
                                       limitsize=limitsize)
                inner_png = inner_png_raw.resize((int(info_dict[g_idx]["full_size"][0]),
                                  int(info_dict[g_idx]["full_size"][1])))
                images.append(inner_png)
            elif inherits(grob, cowplot):
                inner_png_raw = grob._create_png(width= info_dict[g_idx]["full_size"][0]/dpi,
                                             height= info_dict[g_idx]["full_size"][1]/dpi,
                                             dpi=dpi,
                                             limitsize=limitsize)
                inner_png = inner_png_raw.resize((int(info_dict[g_idx]["full_size"][0]),
                                  int(info_dict[g_idx]["full_size"][1])))

                images.append(inner_png)
            else:
                raise ValueError("trying to create image when object not p9.ggplot "+\
                                 "or cowplot object")

        return images

    def _design_to_structure(self, width_px, height_px, rel_widths, rel_heights):
        row_idx_mat = np.tile(np.arange(self.layout.nrow,dtype=int).reshape(-1,1),
                                 self.layout.ncol)
        col_idx_mat = np.tile(np.arange(self.layout.ncol, dtype=int).reshape(1,-1),
                              (self.layout.nrow,1))

        info_dict = {}

        width_loc = np.array([0] + list(np.cumsum(rel_widths[:rel_widths.shape[0]-1])))
        height_loc = np.array([0] + list(np.cumsum(rel_heights[:rel_heights.shape[0]-1])))

        for g_idx in np.unique(self.layout.design):
            inner_row = row_idx_mat[self.layout.design == g_idx]
            inner_col = col_idx_mat[self.layout.design == g_idx]

            inner_range = (val_range(inner_row),
                           val_range(inner_col))
            # calc cumulative width and length for image
            c_size = np.sum(rel_widths[np.arange(inner_range[0][0],
                               inner_range[0][1]+1,
                               dtype = int)])

            r_size = np.sum(rel_heights[np.arange(inner_range[1][0],
                               inner_range[1][1]+1,
                               dtype = int)])
            start_loc = (width_loc[val_range[0][0]],
                         height_loc[val_range[1][0]])

            slices_list = []
            for s_idx in np.arange(inner_row.shape[0],dtype = int):
                r_idx = inner_row[s_idx]
                c_idx = inner_col[s_idx]

                slice_start = (width_loc[c_idx],
                               height_loc[r_idx])
                slice_width = rel_width[c_idx]
                slice_height = rel_height[r_idx]



            info_dict[g_idx] = dict(full_size = (c_size, r_size),
                                    start_loc = start_loc,
                                    slices = slices_list)
        return info_dict




    def save(self,
            filename=None,
            format=None,
            path=None,
            width=None,
            height=None,
            units='in',
            dpi=None,
            limitsize=True,
            verbose=True):
        """save png version of object"""

    # pathwork functions
    ## these functions have to start tracking sizing scalars...
    ## also - what does it mean to scale something if you alter the x and y sizes...
    ## generally will need to think about this...


    def _clean_layout(self):
        """
        Internal function that updates layout if need be
        (aka old layout doesn't work for number of plots or a layout has not
        been defined).
        """
        if self.layout is None or \
            (self.layout.ncol * self.layout.nrow < len(self.grobs)):

            self.layout = layout(ncol = len(self.grobs))

    # https://patchwork.data-imaginist.com/reference/plot_arithmetic.html
    # this will be harder than I though given (a+b)+c is expected to look like...
    def __add__(self, other):
        if inherits(other, layout):
            self.layout = other
        elif inherits(other, p9.ggplot.ggplot):
            self.grobs.append(other)
        elif inherits(other, cowpatch):
            self.grobs.append(other)
        else:
            raise ValueError("cannot add non-ggplot, cowpatch, layout or"+\
                             "annoation objects to cowpatch")

        # other must be ggplot object, cowpatch object or layout/annotation object
    def __truediv__(self, other):
        # ggplot object, cowpatch object
    def __or__(self, other):
        # ggplot object, cowpatch object
    def __sub__(self, other):
        # ggplot object, cowpatch object
    def __mul__(self, other):
        # theme application (current level) - how to do this across patchwork and cowplot? - need to identify levels...
    def __and__(self, other):
        # theme appilcation (global)





