import numpy as np
from .base_elements import patch
from .svg_utils import gg_to_svg
from .utils import inherits_plotnine


# TODO notes:
# 2/7 (Ben): wrapper_plotnine is pretty clean, but needs to be tested
#       wrapper_mlt and wrapper_sns need to be done, specifically mlt
#       needs to make sure the svg object returned with _svg is the correct
#       size - this can probably be done with similar code to that done in the
#       gg_to_svg approach

class wrapper_plotnine(patch):
    def __init__(self,gg):
        """
        wrapper for plotnine objects

        Arguments
        ---------
        gg : plotnine ggplot object

        Notes
        -----
        You can still use the plotnine ggplot "+" to this object to continue to
        update this object. This wrapper creates a special patch object that
        can be combined with other patch objects.
        """
        self.gg = gg
        self.layout = None

    def _svg(self, width_px, height_px):
        """
        convert plot to svg objecct

        Arguments
        ---------
        width_px : float
            desired width of svg object in pixels
        height_px : float
            desired height of svg object in pixels

        Returns
        -------
        svg_object : svgutils.transforms object
        """
        return gg_to_svg(self.gg,
                         width = to_inches(width_px, "px"),
                         height = to_inches(height_px, "px"))

    def __add__(self, other):
        # this allows for the object to has specially addition properties
        # that still provide ggplot structure (not just patch structure)
        if inherits_plotnine(other):
            self.gg = self.gg + other
        else:
            super().__add__(other)




class wrapper_matplotlib(patch):
    def __init__(self, fig, axes):
        """
        wrapper for matplotlib objects

        Arguments
        ---------
        fig : matplotlib figure object
        axes : matplotlib axes object

        Notes
        -----
        You can still update the plot using `object.fig.(function)` and
        `object.fig.(function)`. This wrapper creates a special patch object that
        can be combined with other patch objects.
        """
        self.fig = fig
        self.axes = axes

    def _svg(self, width_px, height_px):
        raise ValueError("TODO: implement")

class wrapper_seaborn(wrapper_matplotlib):
    def __init__(self, fig, axes):
        """
        wrapper for seaborn objects

        Arguments
        ---------
        fig : matplotlib figure object
        axes : matplotlib axes object

        Notes
        -----
        This is the same as the `wrapper_matplotlib` function.

        You can still update the plot using `object.fig.(function)` and
        `object.fig.(function)`. This wrapper creates a special patch object that
        can be combined with other patch objects.

        """
        super().__init__(fig, axes)
