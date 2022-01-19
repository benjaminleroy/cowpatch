import io
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import sympy
import plotnine as p9
import warnings
from matplotlib.patches import Rectangle
import svgutils.transform as sg
import re

# function from poc_svg.py



def transform_size(size_string_tuple):
    """
    takes string with unit and converts it to a float w.r.t pt

    Argument
    --------
    size_string_tuple : string tuple
        tuple of strings with size of svg image 

    Return
    ------
    tuple of floats of sizes w.r.t pt
    """
    value = [float(re.search(r'[0-9\.+]+', s).group())
                for s in size_string_tuple]
    
    if size_string_tuple[0].endswith("pt"):
       return (value[0], value[1])
    elif size_string_tuple[0].endswith("in"):
        return (value[0]/72, value[1]/72)
    elif size_string_tuple[0].endswith("px"):
        return (value[0]*.75, value[1]*.75)
    else:
        raise ValueError("size_string_tuple structure of object not as "+\
                         "expected, new size type")

# x = sympy.symbols('x')
# y = 5 /sympy.sqrt(1 + sympy.sin(sympy.sqrt(x**2 + 2))) 
# lat = sympy.latex(y)

# text = f"${lat}$"
# fig = plt.figure()
# t = plt.text(0.001, 0.001, text, fontsize=50)

# fig.patch.set_facecolor('white')
# plt.axis('off')
# plt.tight_layout()



# with io.BytesIO() as png_buf:
#     plt.savefig(png_buf, bbox_inches='tight', pad_inches=0)
#     png_buf.seek(0)
#     image = Image.open(png_buf)
#     image.load()
#     inverted_image = ImageOps.invert(image.convert("RGB"))
#     cropped = image.crop(inverted_image.getbbox())

# inch_dim = [val / 96 for val in cropped.size]

# bbox = fig.get_tightbbox(fig.canvas.get_renderer())
# fig.set_constrained_layout(bbox)
# fig.set_size_inches(inch_dim)


# fid = io.BytesIO()
# plt.savefig(fid, bbox_inches='tight', pad_inches=0, format = "svg",
#             facecolor=None)
# fid.seek(0)
# image = Image.open(png_buf)


# plt.savefig("test.svg", bbox_inches='tight', pad_inches=0,
#             transparent=True)

_acceptable_text_params = [
    # plt.Text arguments (minus x,y,text/s)
     "color", "verticalalignment",
    "horizontalalignment", "multialignment",
    "fontproperties","rotation",
    "linespacing",
    "rotation_mode",
    "usetex",
    "wrap",
    "transform_rotates_text",
    "parse_math",

    # kargs of plt.Text
    "agg_filter",
    "alpha",
    "animated",
    "backgroundcolor",
    "bbox",
    "clip_box",
    "clip_on",
    "clip_path",
    "color","c",
    "figure",
    "fontfamily","family" ,
    "fontproperties", "font", "font_properties",
    "fontsize", "size",
    "fontstretch", "stretch",
    "fontstyle","style",
    "fontvariant","variant",
    "fontweight", "weight",
    "gid",
    "horizontalalignment", "ha",
    "in_layout",
    "label",
    "linespacing",
    'math_fontfamily',
    "multialignment", "ma",
    "parse_math",
    'path_effects',
    "picker",
    "position",
    "rasterized",
    "rotation",
    "rotation_mode",
    "sketch_params",
    "snap",
    "text",
    "transform",
    "transform_rotates_text",
    "url",
    "usetex",
    "verticalalignment", "va", 
    "visible",
    "wrap",
    "zorder"
]

class text:
    def __init__(self, label, element_text=None, theme=None):
        """
        create a new text object

        Arguments
        ---------
        label : string
            text label with desirable format (e.g. sympy, etc.)
        element_text : plotnine.themes.elements.element_text
            element object from plotnine, can also be added later
        theme : plotnine.theme object
            theme object from plotnine, can be associated later
            should only provide a theme or element_text (as a theme
            contains an element_text)


        Details
        -------
        This class leverages matplotlib to create the text (given that 
        matplotlib can create path-style objects for text if the individual
        is worried that the svg text visually won't be preserved - this is also
        annoying that this is the default).

        Note the function use the ``text`` attribute - NOT the ``plot_title``
        attribute if a theme is provided.
        """
        self.label = label

        if element_text is not None and theme is not None:
            raise ValueError("please provide only a theme or element_text, "+\
                             "not both")
        self.element_text = p9.element_text()#element_text
        self.theme = theme


    def __add__(self, other):
        """
        add element_text or theme to update format

        Arguments
        ---------
        other : plotnine.themes.elements.element_text or theme
            theme or element_text to define the attributes of the text.

        Details
        -------
        Note the function use the ``text`` attribute - NOT the ``plot_title``
        attribute if a theme is provided.
        """
        # difference between p9.themes.themeable.element_text vs
        # p9.themes.elements.element_text?
        # ^- themeable seems more full - probably want that version...
        #    (but that's not what's created naturally...)

        if not isinstance(other, p9.themes.themeable.element_text) and \
           not isinstance(other, p9.theme):
            raise ValueError("text objects are only allowed to be combined "+\
                             "with element_text objects.")
        # need to update theme or element_text...
        if isinstance(other, p9.themes.themeable.element_text):
            if self.element_text is None:
                self.element_text = other
            else:
                # update element_text & theme...
                pass


        if isinstance(other, p9.theme):
            if self.theme is None:
                self.theme = other
            else:
                # update theme and element_text...
                pass


    def _provide_complete_element_text(self):
        """
        It should be here that the current global theme is accessed, and thing are completed...
        """
        if self.theme is None:
            current_theme = p9.theme_get()
        else:
            current_theme = self.theme


        if self.element_text is not None:
            current_theme += theme(text=self.element_text)

        return current_theme

    def _gather_text_properties(self):
        """
        this function mirrors the "_draw_title" function of plotnine ggplot
        found here: https://github.com/has2k1/plotnine/blob/9fbb5f77c8a8fb8c522eb88d4274cd2fa4f8dd88/plotnine/ggplot.py#L545


        """
        theme = self._provide_complete_element_text()
        rcParams = theme.rcParams
        get_property = self.theme.themables.property

        # font size:
        try:
            fontsize = get_property('text', 'size')
        except KeyError:
            fontsize = float(rcParams.get("font.size", 12))

        # linspace:
        try:
            linespacing = get_property('text', 'linespacing')
        except KeyError:
            linespacing = 1.2

        # padding:
        try:
            margin = get_property('text', 'margin')
        except KeyError:
            pad = 0.09
        else:
            pad = margin.get_as('b', 'in')

        # do we need to deal with multiple lines?


    def _gather_complete_rcParams(self):
        """
        gathers current properties from global theme and combines them
        with specified element_text theme.
        """
        full_rcParams = p9.theme_get().rcParams
        full_rcParams.update(self.element_text.properties)

        text_rcParams = {key:value for key,value in full_rcParams.items() 
                            if key in _acceptable_text_params}


        return text_rcParams


    def _inner_prep(self):
        """
        shows text in cropped window

        theres a difference in the text bounding and the image boundary (text allows to tails and tops of glphs)
        """

        # https://stackoverflow.com/questions/22667224/get-text-bounding-box-independent-of-backend?lq=1

        fig = plt.figure()
        txt = plt.text(x=0.000, y=0.000, s=self.label,
                     **self._gather_complete_rcParams()) # pads are not defaulted as 0... should figure that out for size...

        #


        # renderer2 = mpl.backend_bases.RendererBase()
        # bbox2 = txt.get_window_extent(renderer2)
        # rect2 = Rectangle([bbox2.x0, bbox2.y0], bbox2.width, bbox2.height, \
        #     color = [1,0,0], fill = False)
        # fig.patches.append(rect2)


        # fig = plt.figure()
        # ax = plt.subplot()
        # txt = fig.text(0.15,0.5,'high', fontsize = 36)
        # renderer1 = fig.canvas.get_renderer()
        # bbox1 = txt.get_window_extent(renderer1)
        # rect1 = Rectangle([bbox1.x0, bbox1.y0], bbox1.width, bbox1.height, \
        #     color = [0,0,0], fill = False)
        # fig.patches.append(rect1)

        fig.patch.set_visible('false')
        plt.axis('off')

        with io.BytesIO() as png_buf:
            plt.savefig(png_buf)
            png_buf.seek(0)
            image = Image.open(png_buf)
            image.load()
            inverted_image = ImageOps.invert(image.convert("RGB"))
            cropped = image.crop(inverted_image.getbbox())

        inch_dim = [val / 96 for val in cropped.size]

        #fig.set_size_inches(inch_dim)
        bbox = txt.get_window_extent(fig.canvas.get_renderer())
        #rect = Rectangle([bbox.x0, bbox.y0], bbox.width, bbox.height, 
        #            color = [0,0,0], fill = False)
        #fig.patches.append(rect)

        #fig.set_constrained_layout(bbox)
        #fig.set_constrained_layout_pads(w_pad=0,h_pad=0,wspace=0,hspace=0)

        #fig.set_size_inches(inch_dim)


        # do with svg - should be able to shift and then change size...
        return fig, bbox, inch_dim

    def _svg_object(self):
        """
        returns svgutils.transform.SVGFigure object representation of
        text 
        """

        fig, bbox, inch_dim = self._inner_prep()

        # get original matplotlib image ------------
        fid = io.StringIO()
        fig.savefig(fid, bbox_inches=fig.bbox_inches, format = 'svg')
        fid.seek(0)
        image_string = fid.read()
        img = sg.fromstring(image_string)
        img_size = transform_size((img.width, img.height))

        # prep translated and smaller canvas image ----------
        svg_bb_top_left_corner = (bbox.x0/fig.get_dpi()*72, 
                                  img_size[1]-bbox.y1/fig.get_dpi()*72) # not sure why x0 isn't lower...

        new_image_size = (str(bbox.width/fig.get_dpi()*72)+"pt", 
                          str(bbox.height/fig.get_dpi()*72)+"pt")
        # need to declare the viewBox for some reason...

        new_image_size_string_val = [re.sub("pt","", val) for val in new_image_size]
        new_viewBox = "0 0 %s %s" % (new_image_size_string_val[0], 
                                    new_image_size_string_val[1])

        img_root = img.getroot()
        img_root.moveto(x = -1*svg_bb_top_left_corner[0],
                        y = -1*svg_bb_top_left_corner[1])

        new_image = sg.SVGFigure()
        new_image.set_size(new_image_size)
        new_image.root.set("viewBox", new_viewBox)

        new_image.append(img_root)

        return new_image

    def save(self, filename):
        """
        save text object as image in minimal size object

        """
        new_image = self._svg_object()

        new_image.save(filename)


# visual tests ---------

# text structure ---------
my_text = text("thing")
my_text.save("thing_demo.svg")

my_text_lower_only = text("gya")
my_text_lower_only.save("gya_lower_only_demo.svg")
#^ notice the slight space above (to allow for the potential of upper parts)

my_text_upper_only = text("tiHF")
my_text_upper_only.save("tiHF_upper_only_demo.svg")

# multiple lines
my_text_mult_lines = text("stranger\nthings")
my_text_mult_lines.save("stranger_things_multiple_lines_demo.svg")

# element_text addition ----------




