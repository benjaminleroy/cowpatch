import plotnine as p9
import numpy as np

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

        Notes
        -----
        This class leverages matplotlib to create the text (given that
        matplotlib can create path-style objects for text if the individual
        is worried that the svg text visually won't be preserved - this is also
        annoying that this is the default).

        Note the function use the ``text`` attribute - NOT the
        ``plot_title`` attribute if a theme is provided.
        """
        self.label = label

        if element_text is not None and theme is not None:
            raise ValueError("please provide only a theme or element_text, "+
                             "not both")
        self.element_text = None # prep initialization
        self._clean_element_text(element_text)
        self.theme = theme

    def _clean_element_text(self, element_text):
        """
        cleans element_text to make sure any element_text() is a
        p9.themes.themeable, not just a p9.theme.elements.element_text

        Arguments
        ---------
        element_text : p9's element_text
            element text added to or initialized with the text object. Can
            be None, a p9.theme.elements.element_text or a p9.themes.themeable

        Notes
        -----
        updates i place
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

        TODO: make this work w.r.t patchwork approaches (edge cases #8)

        Arguments
        ---------
        other : plotnine.themes.elements.element_text or theme
            theme or element_text to define the attributes of the text.

        Notes
        -----
        Note the function use the ``text`` attribute - NOT the ``plot_title``
        attribute if a theme is provided.
        """

        if not isinstance(other, p9.themes.themeable.element_text) and \
           not isinstance(other, p9.theme):
            raise ValueError("text objects are only allowed to be combined "+
                             "with element_text objects.")
        # need to update theme or element_text...
        if isinstance(other, p9.themes.themeable.element_text):
            self._clean_element_text(other)

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
                self._clean_element_text(new_element_text)
        return self

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

    def _inner_prep(self):
        """
        Internal function to create matplotlib figure with text and
        provide a bounding box for the location in the plot

        Returns
        -------
        fig : matplotlib.figure.Figure
            figure with text at (0,0), no axes
        bbox : matplotlib.transforms.Bbox
            bbox location of text in figure
        """

        # apply theme/element_text correctly ------

        # mirrors code in p9.ggplot.draw_title() and
        #  p9.themeable.plot_title.apply_figure()
        # code references:
        # - https://github.com/has2k1/plotnine/blob/9fbb5f77c8a8fb8c522eb88d4274cd2fa4f8dd88/plotnine/ggplot.py#L545
        # - https://github.com/has2k1/plotnine/blob/6c82cdc20d6f81c96772da73fc07a672a0a0a6ef/plotnine/themes/themeable.py#L361
        #

        # collect desirable theme and properties --------
        theme = self._provide_complete_theme()

        text_themeable = theme.themeables.get('text')
        properties = text_themeable.properties.copy()


        # create text and apply ----------
        # https://stackoverflow.com/questions/24581194/matplotlib-text-bounding-box-dimensions

        fig, ax = plt.subplots()
        fig.set_dpi(96)
        txt = fig.text(x=0.000, y=0.000, s=self.label)
        with suppress(KeyError):
            del properties['margin']
        with suppress(KeyError):
            txt.set(**properties)

        bbox = txt.get_window_extent(fig.canvas.get_renderer())

        # remove background structure from mpl ----------
        # help from: https://stackoverflow.com/questions/21687571/matplotlib-remove-patches-from-figure
        fig.axes.pop()
        plt.axis('off')

        # bbox aids in cutting all but the desired image

        return fig, bbox


    def _create_svg_object(self, width=None, height=None):
        """
        Internal to create svg object (with text in correct location
        and correct image size)

        Arguments
        ---------
        width : float
            width of desired output (in inches)
        height : float
            height of desired output (in inches)

        Returns
        -------
        svg_obj : svgutils.transform.SVGFigure
            svg representation of text with correct format and image size
        """

        fig, bbox = self._inner_prep()

        if width is not None:
            width = to_pt(width, "in")
        if height is not None:
            height = to_pt(height, "in")


        # get original matplotlib image ------------
        fid = io.StringIO()
        fig.savefig(fid, bbox_inches=fig.bbox_inches, format='svg')
        fid.seek(0)
        image_string = fid.read()
        img = sg.fromstring(image_string)
        img_size = transform_size((img.width, img.height))
        # location correction for alignment and margins -------

        current_theme = self._provide_complete_theme()
        ha_str = current_theme.themeables.get("text").properties.get("ha")
        va_str = current_theme.themeables.get("text").properties.get("va")
        margin_dict = current_theme.themeables.get("text").properties.get("margin")
        margin_dict_pt = {"t": to_pt(margin_dict["t"], margin_dict["units"]),
                          "b": to_pt(margin_dict["b"], margin_dict["units"]),
                          "l": to_pt(margin_dict["l"], margin_dict["units"]),
                          "r": to_pt(margin_dict["r"], margin_dict["units"])}


        if width is None:
            width = to_pt(bbox.width, 'px') + margin_dict_pt["l"] + margin_dict_pt["r"]

        if height is None:
            height = to_pt(bbox.height, 'px') + margin_dict_pt["t"] + margin_dict_pt["b"]

        if ha_str == "center":
            x_shift = width/2 - to_pt(bbox.width, "px") /2
        elif ha_str == "right":
            x_shift = width - to_pt(bbox.width, "px") - margin_dict_pt["r"]
        else: # ha_str == "left"
            x_shift = margin_dict_pt["l"]


        if va_str == "center":
            y_shift = height/2 - to_pt(bbox.height, "px") /2
        elif va_str == "bottom":
            y_shift = height - to_pt(bbox.height, "px") - margin_dict_pt["b"]
        else: # va_str = "top"
            y_shift = margin_dict_pt["t"]

        # prep translated and smaller canvas image ----------
        # note that bbox coordinates are with respect to a bottom left axis
        # (aka cartesian)
        # and then we need to convert it to svg's top left axis
        svg_bb_top_left_corner = (to_pt(bbox.x0,
                                        units = "px"), # x_min
                                  img_size[1] - to_pt(bbox.y1,
                                        units = "px")) # height - y_max

        new_image_size = (str(width)+"pt",
                          str(height)+"pt")

        # need to declare the viewBox for some reason...
        new_image_size_string_val = [re.sub("pt", "", val)
                                        for val in new_image_size]

        new_viewBox = "0 0 %s %s" % (new_image_size_string_val[0],
                                    new_image_size_string_val[1])

        img_root = img.getroot()
        img_root.moveto(x = -1*svg_bb_top_left_corner[0] + x_shift,
                        y = -1*svg_bb_top_left_corner[1] + y_shift)
        img_root_str = img_root.tostr()


        new_image = sg.SVGFigure()
        new_image.set_size(new_image_size)
        new_image.root.set("viewBox", new_viewBox)


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
        to_remove = img_root2_xml.findall(".//{http://www.w3.org/2000/svg}path")[0]
        parent.remove(to_remove)
        img_root2_xml_str = ET.tostring(img_root2_xml)
        img2 = sg.fromstring(img_root2_xml_str.decode("utf-8"))

        new_image.append(img2)

        # closing plot
        plt.close()

        return new_image


    def save(self, filename, width=None, height=None):
        """
        save text object as image in minimal size object

        Arguments
        ---------
        filename : str
        width : float
            in inches (if None, then tight (w.r.t. to margins))
        height : float
            in inches (if None, then tight (w.r.t. to margins))
        """

        svg_obj = self._create_svg_object(width=width, height=height)

        svg_obj.save(filename)
        plt.close() # do we need this?
