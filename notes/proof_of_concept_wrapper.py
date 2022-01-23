import numpy as np
import plotnine as p9
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import copy

from PIL import Image
import cairosvg
import svgutils.transform as sg

mtcars = pd.read_csv('https://gist.githubusercontent.com/ZeccaLehn/4e06d2575eb9589dbe8c365d61cb056c/raw/64f1660f38ef523b2a1a13be77b002b98665cdfe/mtcars.csv')


p0 = p9.ggplot(mtcars) +\
  p9.geom_bar(p9.aes(x="gear")) +\
  p9.facet_wrap("cyl") +\
  p9.labs(title = 'Plot 0')

## gg_wrapper ------
## can use a wrapper for patchwork type stuff... (at least in parenthesis)

# class gg_encapsulate():# should inherit cowplot stuff...
#     def __init__(self,gg):
#         """
#         you can technically
#         """
#         self.gg = gg
#         super(self).__init__(grobs = [self.gg])
#         # ^this should work since self.gg is is a reference

#     def __add__(self,other):
#         try:
#             self.gg += other
#             return self
#         except:
#             super(self).__add__(self,other)



class fa_encapsulate():
    def __init__(self, fig, axes):
        """
        Figure and axes cowplot encapsulation.

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

    def create_svg(self, figsize=None):
        """
        through svg...
        """
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

    def show(self, figsize=None):
        """
        returns png

        can instead call self.figure.show()...
        """
        if figsize is None:
            figsize = self.fig.get_size_inches()
        base_image_string = self.create_svg(figsize=figsize).to_str()
        fid = io.BytesIO()
        out_bytes = cairosvg.svg2png(bytestring = base_image_string,
                         write_to = fid,
                         dpi = 96,
                         output_width = figsize[0] * 96,
                         output_height = figsize[1] * 96)
        img_png = Image.open(io.BytesIO(fid.getvalue()))
        img_png.show()

sns_fig, sns_ax = plt.subplots()
sns.boxplot(x = mtcars.gear, y = mtcars.disp, ax=sns_ax)
sns_fig.suptitle("Plot 1")

sns_example = fa_encapsulate(sns_fig, sns_ax)
sns_example.show()

mtl_fig, mtl_ax = plt.subplots()
mtl_ax.scatter(x = mtcars.hp, y = mtcars.wt, c = mtcars.mpg)
mtl_fig.suptitle("Plot 2")

mtl_example = fa_encapsulate(mtl_fig, mtl_ax)
mtl_example.show()
