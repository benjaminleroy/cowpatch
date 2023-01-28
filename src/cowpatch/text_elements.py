import plotnine as p9
from plotnine.themes.themeable import themeable
from plotnine.themes.theme import theme
import numpy as np
import copy
import matplotlib.pyplot as plt
import io
import svgutils.transform as sg
import xml.etree.ElementTree as ET
import re

from contextlib import suppress # suppress kwargs that are incorrect

import pdb

from .utils import to_pt, from_pt, to_inches, from_inches, \
    _transform_size_to_pt, inherits
from .utils import to_inches as _to_inches
from .svg_utils import _show_image, _save_svg_wrapper
from .config import rcParams

class text:
    def __init__(self, label, element_text=None, _type = "cow_text"):
        """
        create a new text object

        Arguments
        ---------
        label : string
            text label with desirable format (e.g. sympy, etc.)
        element_text : plotnine.themes.elements.element_text
            element object from plotnine
        _type : string
            string of which cowpatch text object should inherit attributes
            from, if element_text argument doesn't competely define the text
            attributes

        Notes
        -----
        https://stackoverflow.com/questions/34387893/output-matplotlib-figure-to-svg-with-text-as-text-not-curves
        ^ on text vs paths for text in mathplotlib
        """
        self.label = label
        self._type = _type
        self.element_text = None # prep initialization
        self._theme = p9.theme()
        self._clean_element_text(element_text)

    def _define_type(self, _type):
        self._type = _type

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
        updates in place
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

        # keeping theme update tracking
        if self.element_text is not None:
            self._theme += p9.theme(
                            **{self._type: self.element_text.theme_element})


        return None # just a reminder

    def __add__(self, other):
        """
        add element_text update format

        Arguments
        ---------
        other : plotnine.themes.elements.element_text
            element_text to define the attributes of the text.

        Returns
        -------
        updated text object

        Notes
        -----
        The way we allow for alterations when text objects are used in
        `annotate` function only allows direct alterations of the text's style
        with the addition of a p9.element_text object.
        """

        if isinstance(other, p9.theme):
            # "a text object's information should not be updated with p9.theme
            # directly due to uncertainity in which theme key parameter will
            # actually be used.
            raise ValueError("a text object's presentation information is not "+\
                             "able to be directly updated with a p9.theme, " +
                             "use a p9.element_text object instead. See Notes "+\
                             "for more information")

        if not isinstance(other, p9.themes.themeable.element_text):
            raise ValueError("text objects are only allowed to be combined "+\
                             "with p9.element_text objects.")

        new_object = copy.deepcopy(self)

        new_object._clean_element_text(other)

        # # need to update theme or element_text...
        # if isinstance(other, p9.themes.themeable.element_text):
        #     self._clean_element_text(other)

        #     # update theme if it already exists
        #     # (if not we'll update it when it's required)
        #     if self.theme is not None:
        #         self.theme += p9.theme(text = self.element_text.theme_element)

        # if isinstance(other, p9.theme):
        #     if self.theme is None:
        #         self.theme = other
        #     else:
        #         self.theme.add_theme(other)

        #         new_element_text = self.theme.themeables.get("text")
        #         self._clean_element_text(new_element_text)
        return new_object

    def __eq__(self, other):
        """
        Check if current object is equal to another

        Arguments
        ---------
        other : other object, assumed to be text object

        Returns
        -------
        boolean if equivalent
        """

        if not inherits(other, text):
            return False

        return self.__dict__ == other.__dict__

    def _additional_rotation(self, angle=0):
        """
        (internal function) to create a rotation of the original object

        Arguments
        ---------
        angle : float
            angle in degrees (0-360) to rotate the current text

        Returns
        -------
        new text object that is a rotation of the current one
        """

        new_text_object = copy.deepcopy(self)

        if angle == 0: # not alterations done
            return new_text_object

        if new_text_object.element_text is None:
            new_text_object += p9.element_text(angle = angle)
        else:
            # grab the elment_text from text object
            et = new_text_object.element_text.theme_element
            current_angle = et.properties["rotation"]
            et.properties["rotation"] = \
                (((current_angle + angle) / 360.) -
                    np.floor(((current_angle + angle) / 360.))) * 360

            new_text_object += et

        return new_text_object




    def _update_element_text_from_theme(self, theme, key=None):
        """
        Internal function to update .element_text description from a theme

        Arguments
        ---------
        theme : plotnine.theme object
            theme object from plotnine
        key : str
            string associated with which of theme's internal parameter keys
            the element_text will be updated from. If key is None, then we
            use the internal ._type value

        Notes
        -----
        updates element_text inplace.
        """
        if key is None:
            key = self._type

        # 1. check that theme has desired key
        if not key in theme.themeables.keys():
            raise ValueError("key parameter in _update_element_text_from_theme " +\
                             "function call needs to be a key in the provided " +\
                             "theme's themeables.")

        # update element_text with new element_text
        new_et = theme.themeables.get(key)
        if self.element_text is not None:
            self.element_text.merge(new_et)
        else:
            self.element_text = new_et

        self._theme += theme
        self._clean_element_text(self.element_text)

        return None # just a reminder

    def _get_full_element_text(self):
        """
        create a "full" element_text from base p9 theme

        Notes
        -----
        This function will update the element_text *only with* attributes
        that aren't currently defined (using the cow.theme_get() function)
        """
        new_self = copy.deepcopy(self)
        new_self._update_element_text_from_theme(theme_get() + self._theme, # don't want to actually update self.element_text or self._theme
                                                 key=self._type)
        if self.element_text is not None:
            new_self.element_text.merge(self.element_text)

        # full set of structure inherited from cow_text - TODO: smarter approach mirroring p9 functionality?
        if self._type != "cow_text": # assume inherits properties
            cow_text_et = new_self._theme.themeables.get("cow_text")
            cow_text_et.merge(new_self.element_text)
            return cow_text_et
        else:
            return new_self.element_text


    def _min_size(self, to_inches=False):
        """
        calculate minimum size of bounding box around self in pt and
        creates base image of text object


        Arguments
        ---------
        to_inches : boolean
            if the output should be converted to inches before returned

        Returns
        -------
        min_width : float
            minimum width for text in pt (or inches if `to_inches` is True)
        min_height: float
            minimum height for text in pt (or inches if `to_inches` is True)

        Note
        ----
        this code is simlar to that in _base_text_image
        """
        current_element_text = self._get_full_element_text()

        properties = current_element_text.properties.copy()

        # create text and apply ----------
        # https://stackoverflow.com/questions/24581194/matplotlib-text-bounding-box-dimensions

        fig, ax = plt.subplots()
        fig.set_dpi(96) # used for bbox in pixel sizes...
        txt = fig.text(x=0.000, y=0.000, s=self.label)
        with suppress(KeyError):
            del properties['margin']
        with suppress(KeyError):
            txt.set(**properties)

        bbox = txt.get_window_extent(fig.canvas.get_renderer())
        min_width_pt = to_pt(bbox.width, 'px')
        min_height_pt = to_pt(bbox.height, 'px')

        margin_dict = current_element_text.properties.get("margin")
        if margin_dict is not None:
            margin_dict_pt = {"t": to_pt(margin_dict["t"], margin_dict["units"]),
                              "b": to_pt(margin_dict["b"], margin_dict["units"]),
                              "l": to_pt(margin_dict["l"], margin_dict["units"]),
                              "r": to_pt(margin_dict["r"], margin_dict["units"])}
        else:
            margin_dict_pt = {"t":0, "b":0, "l":0, "r":0}


        min_width_pt += (margin_dict_pt["l"] + margin_dict_pt["r"])
        min_height_pt += (margin_dict_pt["t"] + margin_dict_pt["b"])

        plt.close()

        if to_inches:
            min_width = _to_inches(min_width_pt, units = "pt")
            min_height = _to_inches(min_height_pt, units = "pt")
        else:
            min_width = min_width_pt
            min_height = min_height_pt


        return min_width, min_height

    def _base_text_image(self, close=True):
        """
        Create base figure and obtain bbox structure that contains
        the image in the figure

        Arguments
        ---------
        close : boolean
            if we should close the matplotlib plt instance (default True)

        Returns
        -------
        fig : matplotlib figure
            figure of the text (in the smallest area possible)
        bbox : matplotlib bbox object
            bbox for the associated figure (describing bounding box
            of text object in the image)

        Note
        ----
        this code is simlar to that in _min_size
        """
        current_element_text = self._get_full_element_text()
        properties = current_element_text.properties.copy()
        # create text and apply ----------
        # https://stackoverflow.com/questions/24581194/matplotlib-text-bounding-box-dimensions

        fig, ax = plt.subplots()
        fig.set_dpi(96) # used for bbox in pixel sizes...
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

        if close:
            plt.close()

        return fig, bbox

    def _default_size(self, width=None, height=None):
        """
        (Internal) obtain default recommended size of overall text object if
        width or height is None

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
            proposed is the minimum width (including margins). THIS IS IN INCHES
        height : float
            returns default height for given object if not provided (else just
            returns provided value). If only width is provided then height
            proposed is the minimum height (including margins). THIS IS IN INCHES

        Notes
        -----
        This function is internal, it does assume that in width/height is not
        None that you've done your homework and not set width or height as too
        small.
        """
        if width is not None and height is not None:
            return width, height

        min_width_pt, min_height_pt = self._min_size()

        if width is None:
            width = from_pt(min_width_pt, "inches")
        if height is None:
            height = from_pt(min_height_pt, "inches")

        return width, height

    def _svg(self, width_pt=None, height_pt=None, sizes=None, num_attempts=None):
        """
        Internal to create svg object (with text in correct location
        and correct image size)

        Arguments
        ---------
        width_pt : float
            width of desired output (in pt)
        height_pt : float
            height of desired output (in pt)
        sizes: TODO: write description & code up
        num_attempts : TODO: write description & code up

        Returns
        -------
        svg_obj : svgutils.transform.SVGFigure
            svg representation of text with correct format and image size

        See also
        --------
        patch._svg : similar functionality for a patch object
        svgutils.transforms : pythonic svg object
        """

        fig, bbox = self._base_text_image(close=False)
        min_width_pt, min_height_pt = self._min_size()

        # TODO: update to the "correction proposal approach"
        if width_pt is not None:
            if width_pt < min_width_pt - 1e-10: # eps needed
                plt.close()
                raise ValueError("requested width of text object isn't "+\
                                 "large enough for text")
        else: #if width is None
            width_pt = min_width_pt


        if height_pt is not None:
            if height_pt < min_height_pt - 1e-10: # eps needed
                plt.close()
                raise ValueError("requested height of text object isn't "+\
                                 "large enough for text")
        else: #if height is None
            height_pt = min_height_pt



        # get original matplotlib image ------------
        fid = io.StringIO()
        fig.savefig(fid, bbox_inches=fig.bbox_inches, format='svg')
        fid.seek(0)
        image_string = fid.read()
        img = sg.fromstring(image_string)
        img_size = _transform_size_to_pt((img.width, img.height))
        # ^this won't be width or min_width_pt related

        # location correction for alignment and margins -------
        current_element_text = self._get_full_element_text()
        ha_str = current_element_text.properties.get("ha")
        va_str = current_element_text.properties.get("va")
        margin_dict = current_element_text.properties.get("margin")

        if margin_dict is not None:
            margin_dict_pt = {"t": to_pt(margin_dict["t"], margin_dict["units"]),
                              "b": to_pt(margin_dict["b"], margin_dict["units"]),
                              "l": to_pt(margin_dict["l"], margin_dict["units"]),
                              "r": to_pt(margin_dict["r"], margin_dict["units"])}
        else:
            margin_dict_pt = {"t":0, "b":0, "l":0, "r":0}


        if ha_str == "center":
            x_shift = width_pt/2 - to_pt(bbox.width, "px")/2
        elif ha_str == "right":
            x_shift = width_pt - to_pt(bbox.width, "px") - margin_dict_pt["r"]
        else: # ha_str == "left"
            x_shift = margin_dict_pt["l"]

        if va_str == "center":
            y_shift = height_pt/2 - to_pt(bbox.height, "px")/2
        elif va_str == "bottom":
            y_shift = height_pt - to_pt(bbox.height, "px") - margin_dict_pt["b"]
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

        new_image_size_string_val = (str(width_pt), str(height_pt))
        new_image_size = (new_image_size_string_val[0] + "pt",
                          new_image_size_string_val[1] + "pt")

        # need to declare the viewBox for some reason...
        new_viewBox = "0 0 %s %s" % (new_image_size_string_val[0],
                                    new_image_size_string_val[1])

        img_root = img.getroot()
        img_root.moveto(x = -1*svg_bb_top_left_corner[0] + x_shift,
                        y = -1*svg_bb_top_left_corner[1] + y_shift)
        img_root_str = img_root.tostr()

        new_image = sg.SVGFigure()
        new_image.set_size(new_image_size)
        new_image.root.set("viewBox", new_viewBox)

        ### remove path (xml.etree.ElementTree) ---------
        # removing the background behind the text object (allows text to be
        # above other objects)
        img_root2_xml = ET.fromstring(img_root_str)
        parent = img_root2_xml.findall(".//{http://www.w3.org/2000/svg}g[@id=\"patch_1\"]")[0]
        to_remove = img_root2_xml.findall(".//{http://www.w3.org/2000/svg}path")[0]
        parent.remove(to_remove)
        img_root2_xml_str = ET.tostring(img_root2_xml)
        img2 = sg.fromstring(img_root2_xml_str.decode("utf-8"))

        new_image.append(img2)

        # closing plot
        plt.close()

        return new_image, (width_pt, height_pt)

    def save(self, filename, width=None, height=None, dpi=96, _format=None,
             verbose=None):
        """
        save text object image to file

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
        cow.patch.save : same function but for a cow.patch object
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
        display text object from the command line or in a jupyter notebook

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

        See also
        --------
        cow.patch.show : same function but for a cow.patch object
        """
        # updating width and height if necessary (some combine is none)
        width, height = self._default_size(width=width, height=height)

        # global default for verbose (if not provided by the user)
        if verbose is None:
            verbose = rcParams["show_verbose"]

        svg_obj, (actual_width_pt, actual_height_pt) = \
            self._svg(width_pt=from_inches(width, "pt", dpi=dpi),
                       height_pt=from_inches(height, "pt", dpi=dpi))

        _show_image(svg_obj,
                    width=to_inches(actual_width_pt, "pt", dpi=dpi),
                    height=to_inches(actual_height_pt, "pt", dpi=dpi),
                    dpi=dpi,
                    verbose=verbose)

    def __str__(self):
        self.show()
        return "<text (%d)>" % self.__hash__()

    def __repr__(self):
        out = "label:\n" +  "  |" + re.sub("\n", "\n  |", self.label) +\
              "\nelement_text:\n  |" + self.element_text.__repr__() +\
              "\n_type:\n  |\"" + self._type +"\""

        return "<text (%d)>" % self.__hash__() + "\n" + out

    def __hash__(self):
        return hash(tuple(self.__dict__))

class cow_title(themeable):
    """
    text class for cow.patch titles

    Parameters
    ----------
    theme_element : element_text
    """
    pass

class cow_subtitle(themeable):
    """
    text class for cow.patch subtitles

    Parameters
    ----------
    theme_element : element_text
    """
    pass

class cow_caption(themeable):
    """
    text class for cow.patch captions

    Parameters
    ----------
    theme_element : element_text
    """
    pass

class cow_tag(themeable):
    """
    text class for cow.patch tags

    Parameters
    ----------
    theme_element : element_text
    """
    pass

class cow_text(cow_title, cow_subtitle, cow_caption, cow_tag):
    """
    default text for cow.text object

    Parameters
    ----------
    theme_element : element_text
    """

    @property
    def rcParams(self):
        rcParams = super().rcParams

        family = self.properties.get('family')
        style = self.properties.get('style')
        weight = self.properties.get('weight')
        size = self.properties.get('size')
        color = self.properties.get('color')

        if family:
            rcParams['font.family'] = family
        if style:
            rcParams['font.style'] = style
        if weight:
            rcParams['font.weight'] = weight
        if size:
            rcParams['font.size'] = size
            rcParams['xtick.labelsize'] = size
            rcParams['ytick.labelsize'] = size
            rcParams['legend.fontsize'] = size
        if color:
            rcParams['text.color'] = color

        return rcParams



def theme_get():
    """
    Creates a theme that contains defaults for cow related themeables
    added to a p9.theme_get if needed.

    From plotnine:

    The default theme is the one set (using :func:`theme_set`) by
    the user. If none has been set, then :class:`theme_gray` is
    the default.
    """
    return theme_complete(p9.theme_get())


def theme_complete(other):
    """
    a object that can be right added to another p9.theme and
    will complete this p9.theme (relative to cow's default rcParms)

    """
    base = copy.deepcopy(other)
    for cow_key in ["cow_text", "cow_title", "cow_subtitle",
                    "cow_caption", "cow_tag"]:
        if cow_key not in base.themeables.keys() and \
            cow_key in rcParams.keys():
            base += theme(**{cow_key: rcParams[cow_key]})
        else:
            current_et = base.themables[cow_key]
            updated_et = rcParams[cow_key].merge(current_et)
            base += theme(**{cow_key: updated_et})
    return base


