import copy
from .text_elements import text
from .utils import inherits, _to_alphabet_representation, _to_roman_numerials,\
    _string_tag_format
import re
import numpy as np
import copy

import pdb

# TODO: potentially allow addition of theme to pass info standard formats...

# annotation
#
# internal functions:
# 1. pass tags farther down (to another annotation)
# 2. create tag of requested size
# 3.

class annotation:
    def __init__(self, title=None, subtitle=None, caption=None, 
                 tags=None, tags_format=None, tags_order="auto",
                 tags_loc=None, tags_inherit="fix"):
        """
        annotation tools for adding titles and tags to cow.patch
        arangement of plots.
    
        Arguments
        ---------
        title : str, cow.text, or dictionary
            This contains information for the top level patch's titles, which
            can appear on the top (dictionary key: "top"/"t"), left
            ("left"/"l"), right ("right"/"r"), or bottom ("bottom"/"b"). One
            can have multiple titles (e.g. one on top and one on the left).
        subtitle : str, cow.text, or dictionary
            This contains information for the top level patch's subtitles
            (and appear below the titles). Like `title`, these can appear on
            the top (dictionary key: "top"/"t"), left ("left"/"l"),
            right ("right"/"r"), or bottom ("bottom"/"b"). One can have
            multiple subtitles (e.g. one on top and one on the left).
        caption : str or cow.text
            Each patch can have 1 caption which is located below all other
            elements when the patch is configured (i.e. below all plots,
            titles, subtitles and tags).
        tags : list or tuple
            list or tuple. If one wants to define each labels name by hand,
            use a list. If you would like to define labels in an automated
            manner relative to the the hierachical storage structure, use a
            tuple. The length of the tuple, at max should be the max depth of
            the arangement of plots. Each value in the tuple can either be
            a string specifying the general auto-index structure ("1" or "0",
            "a", "A", "i", "I") OR it can be a list that acts like the auto
            ordering for the given level.
        tags_format : str/text objects or tuple of str/text objects
            Format of strings relative to levels of inserts. For example, if
            we were using the automated labels and had a depth of 2, one might
            see something like "Fig {0}.{1}" for this paramter. We could then
            see the output of "Fig 2.1" if both tags liked like ("1","1")
            or ("0","0"). The default, if tags on auto-constructed, is
            ("{0}", "{0}.{1}", "{0}.{1}.{2}", "{0}.{1}.{2}.{3}", ...)
        tags_order : str ["auto", "input", "yokogaki"]
            How we orderthe tags. If auto, the default is by "input" if you
            provide your own labels and "yokogaki" if you don't. "Input" means
            that the tags ordering will be assoicated with the grobs ordering.
            "Yokogaki" means that the tags will be associated with the
            top-to-bottom, left-to-right ordering of the grobs.
        tags_loc : str ["top", "left", "right", "bottom"]
            Location of the tags relative to grob they are tagging.
        tags_inherit : str ["fix", "override"]
            Indicates how tagging should behave relative to plotential plot
            hierachy. If "fix", then the associated cowpatch object and inner
            objects won't inherits tags from parents. If "override",
            parent tagging structure will pass through *and* override tagging
            desires for this level.

        Notes
        -----
        TODO (update docstring):
        Due to "tags_inherit", we need to allow updates. Potential solution
        to removing values would be to have additions say "np.nan" instead of
        None to clean something out. Annoyingly this would force updates of
        of a dictionary - which will also need this functionality.

        Note this function doesn't track if the text object is the correct
        class... maybe it should override it if it isn't the correct class?
        """

        # prep definition
        self.title = dict()
        self.subtitle = dict()
        self.caption = None
        self.tags = None
        self.tags_order = None
        self.tags_loc = None
        self.tags_inherit = None
        self._tags_format = None
        self.tags_depth = -1

        self._update_all_attributes(title=title,
                                    subtitle=subtitle,
                                    caption=caption,
                                    tags=tags,
                                    tags_format=tags_format,
                                    tags_order=tags_order,
                                    tags_loc=tags_loc,
                                    tags_inherit=tags_inherit)

    @property
    def tags_format(self):
        if self._tags_format is not None and self._tags_format is not np.nan:
            _tags_format = self._tags_format
        elif self.tags is None or self.tags is np.nan: # both tags_format and tags are None
            _tags_format = self._tags_format
        elif inherits(self.tags, list):
            _tags_format = ("{0}", )
        else:
            _tags_format = tuple(_string_tag_format(x)
                                 for x in np.arange(len(self.tags)))

        ## making tags_format text  (same code in _update_all_attributes...)
        if _tags_format is not None and _tags_format is not np.nan: # if None/np.nan, then tags is also None
            new_tags_format = []
            for e in _tags_format:
                if inherits(e, text):
                    e2 = copy.deepcopy(e)
                    e2._define_type(_type = "cow_tag")
                    new_tags_format.append(e2)
                else: #e is string
                    e = text(label = e, _type = "cow_tag")
                    new_tags_format.append(e)
            new_tags_format = tuple(new_tags_format)
        else:
            new_tags_format = _tags_format

        return new_tags_format



    def _clean_up_attributes(self):
        """
        Examines all attributes and those that are np.nan are converted to None
        """
        attributes = copy.deepcopy(self.__dict__)

        for key, value in attributes.items():
            if value is np.nan:
                if key in ["title", "subtitle"]:
                    self.__dict__[key] = {}
                else:
                    self.__dict__[key] = None




        return None

    def _update_all_attributes(self, title=None, subtitle=None, caption=None,
                     tags=None, tags_format=None, tags_order="auto",
                    tags_loc=None, tags_inherit="fix"):
        """
        Updates all attributes of self related to input values

        Arguments
        ---------
        title : str, cow.text, or dictionary
            This contains information for the top level patch's titles, which
            can appear on the top (dictionary key: "top"/"t"), left
            ("left"/"l"), right ("right"/"r"), or bottom ("bottom"/"b"). One
            can have multiple titles (e.g. one on top and one on the left).
        subtitle : str, cow.text, or dictionary
            This contains information for the top level patch's subtitles
            (and appear below the titles). Like `title`, these can appear on
            the top (dictionary key: "top"/"t"), left ("left"/"l"),
            right ("right"/"r"), or bottom ("bottom"/"b"). One can have
            multiple subtitles (e.g. one on top and one on the left).
        caption : str or cow.text
            Each patch can have 1 caption which is located below all other
            elements when the patch is configured (i.e. below all plots,
            titles, subtitles and tags).
        tags : list or tuple
            list or tuple. If one wants to define each labels name by hand,
            use a list. If you would like to define labels in an automated
            manner relative to the the hierachical storage structure, use a
            tuple. The length of the tuple, at max should be the max depth of
            the arangement of plots. Each value in the tuple can either be
            a string specifying the general auto-index structure ("1" or "0",
            "a", "A", "i", "I") OR it can be a list that acts like the auto
            ordering for the given level.
        tags_format : str or text
            Format of strings relative to levels of inserts. For example, if
            we were using the automated labels and had a depth of 2, one might
            see something like "Fig {0}.{1}" for this paramter. We could then
            see the output of "Fig 2.1" if both tags liked like ("1","1")
            or ("0","0"). The default, if tags on auto-constructed, is
            ("{0}", "{0}.{1}", "{0}.{1}.{2}", "{0}.{1}.{2}.{3}", ...)
        tags_order : str ["auto", "input", "yokogaki"]
            How we the tags. If auto, the default is by "input" if you provide
            your own labels and "yokogaki" if you don't. "Input" means that the
            tags ordering will be assoicated with the grobs ordering.
            "Yokogaki" means that the tags will be associated with the
            top-to-bottom, left-to-right ordering of the grobs.
        tags_loc : str ["top", "left", "right", "bottom"]
            Location of the tags relative to grob they are tagging.
        tags_inherit : str ["fix", "override"]
            Indicates how tagging should behave relative to plotential plot
            hierachy. If "fix", then the associated cowpatch object and inner
            objects won't inherits tags from parents. If "override",
            parent tagging structure will pass through *and* override tagging
            desires for this level.

        Returns
        -------
        None - internally updates self

        Note
        ----
        Value of np.nan removes current value and none doesn't update
        """

        # process title -------------
        self.title = self._update_tdict_info(t = title,
                                             current_t = self.title,
                                             _type = "title")

        # process subtitle ------------
        self.subtitle = self._update_tdict_info(t = subtitle,
                                                current_t = self.subtitle,
                                                _type = "subtitle")

        # process caption ----------
        # basic update
        if caption is np.nan:
            self.caption = np.nan
        elif caption is not None:
            if inherits(caption, str):
                caption = text(label = caption)
                caption._define_type(_type = "cow_caption")

            self.caption = caption

        # process tag information -----------
        ## tags
        if tags is np.nan:
            self.tags = np.nan
        elif not inherits(tags, list) and not inherits(tags, tuple) and tags is not None:
            raise ValueError("tags should be either a list or tuple")
        elif inherits(tags, list):
            self.tags = (tags,)
        elif tags is not None:
            self.tags = tags

        ## tags_order
        if tags_order is np.nan:
           self.tags_order = "auto"
        elif tags_order not in ["auto", "input", "yokogaki"]:
            raise ValueError("tags_order can only take values None, \"auto\", "+\
                             "\"yokogaki\", or \"input\" (or np.nan if you "+\
                             "wish to revert to None with an update)")
        else:
            self.tags_order = tags_order

        if self.tags_order is None:
            self.tags_order = "auto"

        ## tags_loc
        if tags_loc is np.nan:
           self.tags_loc = np.nan
        elif tags_loc is not None:
            self.tags_loc = tags_loc

        ## tags_inherit
        if tags_inherit is np.nan:
            self.tags_inherit = np.nan
        elif tags_inherit is not None and (tags_inherit not in ["fix", "override"]):
            raise ValueError("tags_inherit can only take values None, \"fix\" "+\
                             "or \"override\" (or np.nan if you wish to revert "+\
                             "to None with an update)")
        elif tags_inherit is not None:
            self.tags_inherit = tags_inherit

        if self.tags_inherit is None: # default value is fix
            self.tags_inherit = "fix"

        # tags_format processing ---------------------
        ## default tags_format
        if tags_format is not None: # then we will be overriding...
            if tags_format is np.nan:
                if self.tags is None:
                    tags_format = np.nan
                elif inherits(self.tags, list):
                    tags_format = ("{0}",)
                else:
                    tags_format = tuple(_string_tag_format(x)
                                            for x in np.arange(len(self.tags)))
            elif (inherits(tags_format, str) or \
                     inherits(tags_format, text)):
                tags_format = (tags_format, )

            ## making tags_format text objects
            if tags_format is not None and tags_format is not np.nan: # if None/np.nan, then tags is also None
                new_tags_format = []
                for e in tags_format:
                    if inherits(e, text):
                        e2 = copy.deepcopy(e)
                        e2._define_type(_type = "cow_tag")
                        new_tags_format.append(e2)
                    else: #e is string
                        e = text(label = e)
                        e._define_type(_type = "cow_tag")
                        new_tags_format.append(e)
                new_tags_format = tuple(new_tags_format)
            else:
                new_tags_format = tags_format

            self._tags_format = new_tags_format

        # tags_depth definition --------------------
        if inherits(self.tags, list):
            self.tags_depth = 1
        elif (self.tags_format is None or self.tags_format is np.nan) and \
            (self.tags is None or self.tags is np.nan):
            self.tags_depth = -1
        elif self.tags_format is None or self.tags_format is np.nan:
            self.tags_depth = len(self.tags)
        else:
            self.tags_depth = len(self.tags_format)

    def _get_tag(self, index=(0,)):
        """
        Create text of tag for given level and index

        Arguments
        ---------
        index : tuple
            tuple of integers that contain the relative level indices of the
            desired tag.

        Returns
        -------
        cow.text object for tag

        Notes
        -----
        this should return objects relative to correct rotation...
        """
        if inherits(index, int):
            index = (index,)

        pdb.set_trace()
        if len(self.tags_format) < len(index):
            raise ValueError("tags_format tuple has less indices than _get_tag index suggests")

        indices_used = [int(re.findall("[0-9]+", x)[0])
                            for x in re.findall("\{[0-9]+\}",
                                                self.tags_format[len(index)-1].label)]
        if np.max(indices_used) > len(index)-1:
            raise ValueError("tags_format has more indices than the tag hierarchy has.")

        if np.all([True if not inherits(self.tags[i], list)
                    else True if len(self.tags[i]) > x
                    else False for i, x in enumerate(index)]):
            et = copy.deepcopy(self.tags_format[len(index)-1])
            et.label = et.label.format(
                        *[self._get_index_value(i,x) if not inherits(self.tags[i], list)
                        else self.tags[i][x] if len(self.tags[i]) > x
                        else "" for i,x in enumerate(index)
                        ])
        else:
            et = text(label = "", _type = "cow_tag")


        return et



    def _get_index_value(self, level=0, index=0):
        """
        provide index level of a tag

        Arguments
        ---------
        level : int
            level of depth of tag (0 is top level, 1 is first level below, etc.)
        index : tuple
            tuple of integers that contain the relative level indices of the
            desired tag.

        """
        if len(self.tags) < level:
            return ""
        if inherits(self.tags[level], list):
            if len(self.tags[level]) < index:
                return ""
            else:
                return self.tags[level][index]
        else:
            return self._get_auto_index_value(index=index,
                                              _type = self.tags[level])

    def _get_auto_index_value(self, index=0, _type = ["0","1", "a", "A", "i","I"][0]):
        """
        (Internal) get the index of a particular type of auto-index

        Arguments
        ---------
        index : int
            0-based index
        _type : str
            type of indexing

        Returns
        -------
        out : str
            index related to requested style
        """

        if _type == "0":
            return str(index)
        elif _type == "1":
            return str(index+1)
        elif _type == "a":
            return _to_alphabet_representation(index+1)
        elif _type == "A":
            return _to_alphabet_representation(index+1, caps=True)
        elif _type == "i":
            return _to_roman_numerials(index+1)
        elif _type == "I":
            return _to_roman_numerials(index+1, caps=True)
        else:
            raise ValueError('type of auto-tags must be in '+\
                             '["0","1", "a", "A", "i", "I"]')

    def _calculate_tag_margin_sizes(self, index=(0,),
                                    fundamental=False,
                                    to_inches=False):
        """
        (Internal) calculate tag's margin sizes

        Arguments
        ---------
        index : int or tuple
            tuple of indices relative to the hierarchical ordering of the tag
        fundamental : boolean
            if the associated object being "tagged" is a fundamental object,
            if not, a tag is only made if the tags_depth is at the final level.
        to_inches : boolean
            if the output should be converted to inches before returned

        Returns
        -------
        dictatiory with following keys/ objects
        min_inner_width : float
            minimum width required for title & subtitles on top or bottom
        min_full_width : float
            minium width required for caption (spans all of width). This
            will always be zero for the tag structure
        extra_used_width : float
            extra width required for title & subtitles on left or right
        min_inner_height : float
            minimum height required for title & subtitles on left or right
        extra_used_height : float
            extra height required for title & subtitles on top or bottom
        top_left_loc : tuple
            tuple of top left corner of inner image relative to title text

        """
        # if we shouldn't actually make the tag
        if index is None or \
            (self.tags_depth != len(index) and not fundamental):
            return {"min_inner_width": 0,
                "min_full_width": 0, # not able to be nonzero for tag
                "extra_used_width": 0,
                "min_inner_height": 0,
                "extra_used_height": 0,
                "top_left_loc": (0,0)
                }

        # clean-up
        if not inherits(index, tuple):
            index = (index, )

        # getting tag -------------------
        tag = self._get_tag(index=index)
        tag_sizes = tag._min_size(to_inches=to_inches)

        min_inner_width = tag_sizes[0] * \
            (self.tags_loc in ["top", "bottom", "t", "b"])
        min_inner_height = tag_sizes[1] * \
            (self.tags_loc in ["left", "right", "l", "r"])


        extra_used_width = tag_sizes[0] * \
            (self.tags_loc in ["left", "right", "l", "r"])
        extra_used_height = tag_sizes[1] * \
            (self.tags_loc in ["top", "bottom", "t", "b"])

        top_left_loc = (
            tag_sizes[0] * (self.tags_loc in ["left", "l"]),
            tag_sizes[1] * (self.tags_loc in ["top", "t"])
                        )


        return {"min_inner_width": min_inner_width,
                "min_full_width": 0, # not able to be nonzero for tag
                "extra_used_width": extra_used_width,
                "min_inner_height": min_inner_height,
                "extra_used_height": extra_used_height,
                "top_left_loc": top_left_loc
                }

    def _get_tag_and_location(self, width, height,
                              index = (0,),
                              fundamental=False):
        """
        create desired tag and identify location to place tag and associated
        image

        Arguments
        ---------
        width : float
            width in pt
        height : float
            height in pt
        index : tuple
            index of the tag. The size of the tuple captures
            depth.

        Return
        ------
        tag_loc : tuple
            upper left corner location for tag
        image_loc : tuple
            upper left corner location for image (assoicated with tag). If
            the tag is on the top, this means where the corner of the image
            should be placed to correctly be below the tag.
        tag_image :
            tag text svg object
        """
        # clean-up
        if not inherits(index, tuple):
            index = (index, )

        # if we shouldn't actually make the tag
        if self.tags_depth != len(index) and not fundamental:
            return None, None, None

        tag_image = self.get_tag(index = index)

        if self.tags_loc in ["top", "bottom"]:
            inner_width_pt = width
            inner_height_pt = None
        else:
            inner_width_pt = None
            inner_height_pt = height

        tag_image, size_pt = \
            inner_tag._svg(width_pt=inner_width_pt,
                           height_pt=inner_height_pt)

        if self.tags_loc == "top":
            tag_loc = (0,0)
            image_loc = (0, size_pt[1])
        elif self.tags_loc == "left":
            tag_loc = (0,0)
            image_loc = (size_pt[0], 0)
        elif self.tags_loc == "bottom":
            tag_loc = (0, height - size_pt[0])
            image_loc = (0,0)
        else: # self.tags_loc == "right":
            tag_loc = (width - size_pt[1],0)
            image_loc = (0,0)

        return tag_loc, image_loc, tag_image







    def _calculate_margin_sizes(self, to_inches=False):
        """
        (Internal) calculates marginal sizes needed to be displayed for titles

        Arguments
        ---------
        to_inches : boolean
            if the output should be converted to inches before returned

        Returns
        -------
        dictatiory with following keys/ objects
        min_inner_width : float
            minimum width required for title & subtitles on top or bottom
        min_full_width : float
            minium width required for caption (spans all of width)
        extra_used_width : float
            extra width required for title & subtitles on left or right
        min_inner_height : float
            minimum height required for title & subtitles on left or right
        extra_used_height : float
            extra height required for title & subtitles on top or bottom
        top_left_loc : tuple
            tuple of top left corner of inner image relative to title text

        TODO: need to make sure left/right objects are correctly rotated... [9/22 I think this is done]
        """
        min_inner_width = \
            np.sum([t._min_size(to_inches=to_inches)[0] for t in [self.title.get("top"),
                                        self.title.get("bottom"),
                                        self.subtitle.get("top"),
                                        self.subtitle.get("bottom")]
                if t is not None] + [0])

        min_full_width = \
            np.sum([t._min_size(to_inches=to_inches)[0] for t in [self.caption]
                if t is not None] + [0])

        extra_used_width = \
            np.sum([t._min_size(to_inches=to_inches)[0] for t in [self.title.get("left"),
                                        self.title.get("right"),
                                        self.subtitle.get("left"),
                                        self.subtitle.get("right")]
                if t is not None]+ [0])

        min_inner_height = \
            np.sum([t._min_size(to_inches=to_inches)[1] for t in [self.title.get("left"),
                                        self.title.get("right"),
                                        self.subtitle.get("left"),
                                        self.subtitle.get("right")]
                if t is not None] +[0])

        extra_used_height = \
            np.sum([t._min_size(to_inches=to_inches)[1] for t in [self.title.get("top"),
                                        self.title.get("bottom"),
                                        self.subtitle.get("top"),
                                        self.subtitle.get("bottom"),
                                        self.caption]
                if t is not None] + [0])

        top_left_loc = (
            np.sum([t._min_size(to_inches=to_inches)[0]
                    for t in [self.title.get("left"), self.subtitle.get("left")]
                        if t is not None] + [0]),
            np.sum([t._min_size(to_inches=to_inches)[1]
                    for t in [self.title.get("top"), self.subtitle.get("top")]
                        if t is not None] + [0])

            )

        return {"min_inner_width": min_inner_width,
                "min_full_width": min_full_width,
                "extra_used_width": extra_used_width,
                "min_inner_height": min_inner_height,
                "extra_used_height": extra_used_height,
                "top_left_loc": top_left_loc
                }


    def _get_titles_and_locations(self, width, height):
        """
        (Internal) Create title objects and locations to be placed in image

        Arguments
        ---------
        width : float
            width of overall image (in inches?)
        height : float
            height of overall image (in inches?)

        Returns
        -------
        out_list : list
            list of tuples of the location to place the title (top left corner)
            and the image of the title itself. The list has entries for any
            titles, then any subtitles and then the caption (if any). Each
            entry is a tuple with (1) a tuple of the top left corner location
            for the title and (2) the svg object of the title itself

        Notes
        -----
        Here's a visual diagram that helped define this function


                ~~~~ width ~~~~~
                =====b'=====    (width - b)
                            =b= (width of 7 and 8)
                =a=             (width of 1 and 2)
                a1              (width of 1)

                            b_1 (width of 7)
        ~/*'       | 33333 |
        ~/*        | 44444 |
        ~/      ---+-------+---
        ~/      1 2|       |7 8
        ~/      1 2|       |7 8
        ~/      1 2|       |7 8
        ~/      ---+-------+---
        ~  %$      | 55555 |
        ~  %       | 66666 |
        ~    &  999999999999999

        ~ : height
        / : ii'    (height - ii - iii_1)
        * : i      (height of 3 and 4)
        ' : i_1    (height of 3)
        % : ii     (height of 5 and 6)
        $ : ii_1   (height of 5)
        & : iii_1  (height of 9)



        where
        1 : title, left
        2 : subtitle, left
        3 : title, top
        4 : subtitle, top
        5 : title, bottom
        6 : subtitle, bottom
        7 : title, right
        8 : subtitle, right
        9 : caption
        """
        # TODO: testing (likely just do a complex image)
        # TODO: make sure the pt vs inch question is settled

        # minimum size of each object
        title_min_size_dict = {key : [t.min_size() if t is not None else (0,0)
                                         for t in [self.title.get(key),
                                                   self.subtitle.get(key)]]
                                for key in ["top", "bottom", "left", "right"]}

        if self.caption is not None:
            title_min_size_dict["caption"] = self.caption.min_size()
        else:
            title_min_size_dict["caption"] = (0,0)


        # shifts for top left positioning
        shift_horizonal = {
            # same value
            ("title", "top") : np.sum([tu[0] for tu in title_min_size_dict["left"]]),
            ("subtitle", "top") : np.sum([tu[0] for tu in title_min_size_dict["left"]]),
            ("title", "bottom") : np.sum([tu[0] for tu in title_min_size_dict["left"]]),
            ("subtitle", "bottom") : np.sum([tu[0] for tu in title_min_size_dict["left"]]),

            "caption" : 0,

            ("title", "left") : 0,
            ("subtitle", "left") : title_min_size_dict["left"][0][0],
            ("title", "right") : width - np.sum([tu[0] for tu in title_min_size_dict["right"]]),
            ("subtitle", "right") : width - title_min_size_dict["right"][1][0]
        }

        shift_horizonal = {
            # same value
            ("title", "left") : np.sum([tu[1] for tu in title_min_size_dict["top"]]),
            ("subtitle", "left") : np.sum([tu[1] for tu in title_min_size_dict["top"]]),
            ("title", "right") : np.sum([tu[1] for tu in title_min_size_dict["top"]]),
            ("subtitle", "right") : np.sum([tu[1] for tu in title_min_size_dict["top"]]),

            "caption" : height - title_min_size_dict["caption"][1],

            ("title", "top") : 0,
            ("subtitle", "top") : title_min_size_dict["top"][0][1],
            ("title", "bottom") : width - np.sum([tu[1] for tu in title_min_size_dict["right"]]) -\
                                    title_min_size_dict["caption"][1],
            ("subtitle", "bottom") : width - title_min_size_dict["bottom"][1][1] -\
                                    title_min_size_dict["caption"][1]
        }

        # sizes to create each title element with
        inner_width = np.sum([tu[0] for tu in title_min_size_dict["left"] +\
                                     title_min_size_dict["right"]])
        inner_height = np.sum([tu[1] for tu in title_min_size_dict["top"] +\
                                     title_min_size_dict["bottom"]])

        size_request = {
            ("title","top") : (inner_width, None),
            ("title","bottom") : (inner_width, None),
            ("title","left") : (None, inner_height),
            ("title","right") : (None, inner_height),
            ("subtitle","top") : (inner_width, None),
            ("subtitle","bottom") : (inner_width, None),
            ("subtitle","left") : (None, inner_height),
            ("subtitle","right") : (None, inner_height),
            "caption" : (width, None)
        }


        out_list = []
        out_list += [ ( (shift_horizontal[("title",key)], \
                            shift_vertical[("title",key)]), \
                        self.title.get(key)._svg(width_pt = size_request[("title", key)][0],
                                                 height_pt = size_request[("title", key)][1])
                        ) for key in ["top", "bottom", "left", "right"]
                            if self.title.get(key) is not None]

        out_list += [ ( (shift_horizontal[("subtitle",key)], \
                            shift_vertical[("subtitle",key)]), \
                        self.subtitle.get(key)._svg(width_pt = size_request[("subtitle", key)][0],
                                                 height_pt = size_request[("subtitle", key)][1])
                        ) for key in ["top", "bottom", "left", "right"]
                            if self.subtitle.get(key) is not None]

        out_list += [((shift_horizontal[key], shift_vertical[key]), \
                        self.caption._svg(width_pt = size_request[key][0], \
                                         height_pt = size_request[key][1])
                        ) for key in ["caption"] if
                            self.caption is not None]


        return out_list






    def _update_tdict_info(self, t, current_t = dict(), _type = "title"):
        """
        Update or define title/subtitle

        Arguments
        ---------
        t : str, cow.text, or dictionary
            This contains information for the top level patch's titles or subtitles,
            which can appear on the top (dictionary key: "top"/"t"), left
            ("left"/"l"), right ("right"/"r"), or bottom ("bottom"/"b"). One can
            have multiple titles (e.g. one on top and one on the left).
        current_t : dictionary
            current title/subtitle dictionary to be updated.
        _type : str ["title", "subtitle"]
            string indicates if the t is a title or subtitle.

        Returns
        -------
        an updated version of `current_t`.

        Notes:
        ------
        A value of "np.nan" with remove any existing values, and a value of "None"
        with do nothing to the current value. If one is trying to remove the "top"
        title, but not all titles, they must use the dictionary structure (i.e.
        "t = {top: np.nan}".
        """

        current_t = copy.deepcopy(current_t)

        if inherits(t, str):
            t = {"top": copy.deepcopy(t)}

        if inherits(t, text):
            t = {"top": copy.deepcopy(t)}

        if t is np.nan:
            current_t = np.nan
            t = None

        if t is not None:
            if not inherits(t, dict):
                raise ValueError(_type + " type isn't one of the expected types")
            else:
                text_keys = {"t":"top", "l":"left", "r":"right", "b":"bottom"}
                for key, el in t.items():
                    if key in text_keys.keys():
                        key = text_keys[key]
                    if key not in text_keys.values():
                        raise ValueError(_type +\
                                (" dictionary key is not as expected (%s)" % key))

                    if el is np.nan: # remove current element if new element value is np.nan
                        current_val = current_t.get(key)
                        if current_val is not None:
                            current_t.pop(key)
                    elif el is not None:
                        if inherits(el, str):
                            el = text(label = el)
                        el._define_type(_type = "cow_" + _type)

                        current_t[key] = el


        return current_t



    def _step_down_tags_info(self, parent_index):
        """
        Create an updated version of tags_info for children

        Arguments
        ---------
        parent_index : int
            integer associated with the child's tag index

        Returns
        -------
        annotation with all tag attributes to update for children's
        annotation.
        """
        if self.tags is None or \
            len(self.tags) <= 1 or \
            len(self.tags_format) <= 1:
            return annotation()

        tags = self.tags[1:]

        # updating tags_format
        old_tags_format = self.tags_format[1:]

        new_tags_format = []
        new_fillers = ["{"+str(i)+"}" for i in range(len(tags))]

        for t in old_tags_format:
            new_t = copy.deepcopy(t)
            current_index = self._get_index_value(0, parent_index)
            new_t.label = new_t.label.format(current_index, *new_fillers)

            new_tags_format.append(new_t)

        tags_format = tuple(new_tags_format)

        inner_annotation = annotation(tags = tags,
                                      tags_format = tags_format,
                                      tags_order = self.tags_order,
                                      tags_loc = self.tags_loc)
        return inner_annotation



    def __add__(self, other):
        """
        update annotations through addition

        Arguments
        ---------
        other : annotation object
            object to update current annotation object with

        Returns
        -------
        updated self (annotation object)
        """
        if not inherits(other, annotation):
            raise ValueError("annotation can be only added with "+\
                             "another annotation")

        self._update_all_attributes(title = other.title,
                                    subtitle = other.subtitle,
                                    caption = other.caption,
                                    tags=other.tags,
                                    tags_format=other._tags_format,
                                    tags_order=other.tags_order,
                                    tags_loc=other.tags_loc,
                                    tags_inherit=other.tags_inherit)

        return self

    def __eq__(self, other):
        """
        checks if two annotation objects are equal

        Arguments
        ---------
        other : annotation object
            object to update current annotation object with

        Returns
        -------
        boolean for equality (if second object is not an annotation object,
        will return False)
        """
        if not inherits(other, annotation):
            return False

        return self.__dict__ == other.__dict__



