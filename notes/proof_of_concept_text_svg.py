import io
import matplotlib.pyplot as plt
import plotnine as p9
import svgutils.transform as sg
import re
from contextlib import suppress # suppress kwargs that are incorrect


# function from proof_of_concept_svg.py -----------

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


# text class --------------

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
        self.element_text = None # prep initialization
        self._init_element_text(element_text)
        self.theme = theme

    def _init_element_text(self, element_text):
        """
        make sure it's a themeable else create one

        updates is place!

        """
        if element_text is None:
            element_text = None

        if isinstance(element_text, p9.themes.elements.element_text):
            et_themeable = p9.theme(text = element_text
                                    ).themeables.get("text")
            element_text = et_themeable
        else:
            element_text = element_text

        if self.element_text is not None:
            self.element_text.merge(element_text)
        else:
            self.element_text = element_text


        return None # just a reminder

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
            self._init_element_text(other)

            # update theme if it already exists
            # (if not we'll update it when it's required)
            if self.theme is not None:
                self.theme += p9.theme(text = self.element_text.theme_element)

        if isinstance(other, p9.theme):
            if self.theme is None:
                self.theme = other
            else:
                self.theme.add_theme(other)

                new_element_text = self.theme.themeables.get("text")
                self._init_element_text(new_element_text)
        return self # do I need to do a copy somewhere? (also weird __radd__ we'll need to think about...)


    def _provide_complete_theme(self):
        """
        It should be here that the current global theme is accessed, and thing are completed...
        """
        if self.theme is None:
            current_theme = p9.theme_get()
            # and update with our element_text
            if self.element_text is not None:
                # problem here... (need to update themeable.get("text") instead)
                current_theme += p9.theme(text=self.element_text.theme_element)
        else:
            current_theme = self.theme

        return current_theme

    def _gather_text_properties(self):
        """
        this function mirrors the "_draw_title" function of plotnine ggplot
        found here: https://github.com/has2k1/plotnine/blob/9fbb5f77c8a8fb8c522eb88d4274cd2fa4f8dd88/plotnine/ggplot.py#L545

        NOTE: these help define the x and y location - we'll need to
        get that later since we currently do x=0,y=0 (but let's ignore that for now
        # also not the _draw_title() function's default is ha="center", va="center")

        TODO: we likely actually want the default to be left aligned (not centered...)
        ^- Not sure this is where we do it though...
        """
        theme = self._provide_complete_theme()
        # rcParams = theme.rcParams
        # get_property = theme.themeables.property

        # # font size:
        # try:
        #     fontsize = get_property('text', 'size')
        # except KeyError:
        #     fontsize = float(rcParams.get("font.size", 12))

        # # linspace:
        # try:
        #     linespacing = get_property('text', 'linespacing')
        # except KeyError:
        #     linespacing = 1.2

        # # padding:
        # try:
        #     margin = get_property('text', 'margin')
        # except KeyError:
        #     pad = 0.09
        # else:
        #     pad = margin.get_as('b', 'in')

        # updating_properties = dict(fontsize=fontsize,
        #                            linespacing=linespacing,
        #                            pad=pad)

        return theme#, updating_properties


    def _inner_prep(self):
        """
        shows text in cropped window

        theres a difference in the text bounding and the image boundary (text allows to tails and tops of glphs)
        """

        # apply theme/element_text correctly ------

        # mirrors code in p9.ggplot.draw_title() and
        #  p9.themeable.plot_title.apply_figure()
        # code references:
        # - https://github.com/has2k1/plotnine/blob/9fbb5f77c8a8fb8c522eb88d4274cd2fa4f8dd88/plotnine/ggplot.py#L545
        # - https://github.com/has2k1/plotnine/blob/6c82cdc20d6f81c96772da73fc07a672a0a0a6ef/plotnine/themes/themeable.py#L361
        #

        # collect desirable theme and properties --------
        theme = self._gather_text_properties()

        text_themeable = theme.themeables.get('text')
        properties = text_themeable.properties.copy()


        # create text and apply ----------
        fig = plt.figure()
        txt = plt.text(x=0.000, y=0.000, s=self.label)#,
                     #**updating_properties)
        with suppress(KeyError):
            del properties['margin']
        with suppress(KeyError):
            txt.set(**properties)

        # remove background structure from mpl ----------
        #fig.patch.set_visible('false')
        # help from: https://stackoverflow.com/questions/21687571/matplotlib-remove-patches-from-figure
        fig.axes.pop()
        plt.axis('off')

        # bbox aids in cutting all but the desired image
        bbox = txt.get_window_extent(fig.canvas.get_renderer())

        return fig, bbox


    def _create_svg_object(self):
        """
        returns svgutils.transform.SVGFigure object representation of
        text
        """

        fig, bbox = self._inner_prep()

        # get original matplotlib image ------------
        fid = io.StringIO()
        fig.savefig(fid, bbox_inches=fig.bbox_inches, format='svg')
        fid.seek(0)
        image_string = fid.read()
        img = sg.fromstring(image_string)
        img_size = transform_size((img.width, img.height))

        # prep translated and smaller canvas image ----------
        svg_bb_top_left_corner = (bbox.x0/fig.get_dpi() * 72,
                                  img_size[1] - bbox.y1/fig.get_dpi() * 72) # not sure why x0 isn't lower...

        new_image_size = (str(bbox.width/fig.get_dpi() * 72)+"pt",
                          str(bbox.height/fig.get_dpi() * 72)+"pt")

        # need to declare the viewBox for some reason...
        new_image_size_string_val = [re.sub("pt","", val)
                                        for val in new_image_size]

        new_viewBox = "0 0 %s %s" % (new_image_size_string_val[0],
                                    new_image_size_string_val[1])

        img_root = img.getroot()
        img_root.moveto(x = -1*svg_bb_top_left_corner[0],
                        y = -1*svg_bb_top_left_corner[1])

        new_image = sg.SVGFigure()
        new_image.set_size(new_image_size)
        new_image.root.set("viewBox", new_viewBox)

        img_root_str = img_root.tostr()

        # remove patch (lxml.etree) ----------
        # img_root2_lxml = etree.fromstring(img_root_str)
        # parent = img_root2_lxml.findall(".//{http://www.w3.org/2000/svg}g[@id=\"patch_1\"]")[0]
        # to_remove = parent.getchildren()[0]
        # parent.remove(to_remove)
        # img_root2_str = etree.tostring(img_root2_lxml)
        # img2 = sg.fromstring(img_root2_str.decode("utf-8"))

        # remove path (xml.etree.ElementTree) ---------
        img_root2_xml = ET.fromstring(img_root_str)
        parent = img_root2_xml.findall(".//{http://www.w3.org/2000/svg}g[@id=\"patch_1\"]")[0]
        to_remove =  img_root2_xml.findall(".//{http://www.w3.org/2000/svg}path")[0]
        parent.remove(to_remove)
        img_root2_xml_str = ET.tostring(img_root2_xml)
        img2 = sg.fromstring(img_root2_xml_str.decode("utf-8"))

        new_image.append(img2)

        return new_image

    def create_svg_object(self):
        out, out2 = self._create_svg_object()
        plt.close()

        return out, out2

    def save(self, filename):
        """
        save text object as image in minimal size object

        """
        svg_obj = self._create_svg_object()

        svg_obj.save(filename)
        plt.close()


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
#^ notice that as of 1/19 these are centered (not sure we want that...)


# element_text addition ----------

my_text = text("thing")

my_text += p9.element_text(size = 50)
my_text.save("thing_demo50.svg")

my_text += p9.element_text(size = 50, color = "red")
my_text.save("thing_demo50red.svg")

my_text_cumu = text("thing") + p9.element_text(size = 50) +\
    p9.element_text(color = "red")
my_text_cumu.save("thing_demo50red_2.svg")



# theme addition --------

my_text = text("thing")
my_text += p9.theme(text= p9.element_text(size = 50))
my_text.save("thing_demo50_theme.svg")

my_text = text("thing")
my_text += p9.theme(text= p9.element_text(size = 50, color = "red"))
my_text.save("thing_demo50red_theme.svg")

my_text_cumu = text("thing") + p9.theme(text= p9.element_text(size = 50)) +\
    p9.theme(text= p9.element_text(color = "red"))
my_text.save("thing_demo50red_2_theme.svg")



