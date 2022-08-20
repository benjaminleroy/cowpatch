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

        Notes
        -----
        TODO:
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
        self.tags_format = None
        self.tags_depth = -1

        self._update_all_attributes(title=title,
                                    subtitle=subtitle,
                                    caption=caption,
                                    tags=tags,
                                    tags_format=tags_format,
                                    tags_order=tags_order,
                                    tags_loc=tags_loc,
                                    tags_inherit=tags_inherit)

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
            self.tags = (tags)
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

            self.tags_format = new_tags_format

        # tags_depth definition --------------------
        if inherits(self.tags, list):
            self.tags_depth = 0
        elif self.tags_format is None or self.tags_format is np.nan:
            self.tags_depth = -1
        else:
            self.tags_depth = len(self.tags_format) - 1

    def _get_tag(self, index=0):
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

        if len(self.tags_format) < len(index):
            raise ValueError("tags_format tuple has less indices than _get_tag index suggests")

        indices_used = [int(re.findall("[0-9]+", x)[0])
                            for x in re.findall("\{[0-9]+\}",
                                                self.tags_format[len(index)-1].label)]
        if np.max(indices_used) > len(index)-1:
            raise ValueError("tags_format has more indices than the tag hierarchy has.")

        et = copy.deepcopy(self.tags_format[len(index)-1])
        et.label = et.label.format(
                    *[self._get_index_value(i,x) for i,x in enumerate(index)])



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
        calculate tag's margin sizes

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
        min_desired_widths : float
        extra_desired_widths : float
        min_desired_heights : float
        extra_desired_heights : float

        # TODO: needs to deal with rotation...
        """

        # clean-ups...
        if not inherits(index, tuple):
            index = (index, )

        # if we shouldn't actually make the tag
        if self.tags_depth != len(index) and not fundamental:
            return [0],[0],[0],[0]

        # getting tag -------------------
        tag = self._get_tag(index = index)
        tag_sizes = tag._min_size(to_inches=to_inches)

        min_desired_widths = [tag_sizes[0] * \
            (self.tags_loc in ["top", "bottom", "t", "b"])]
        min_desired_heights = [tag_sizes[1] * \
            (self.tags_loc in ["left", "right", "l", "r"])]

        if True:#self.tags_type == 0: #outside of image box
            extra_desired_widths = [tag_sizes[0] * \
                (self.tags_loc in ["left", "right", "l", "r"])]
            extra_desired_heights = [tag_sizes[1] * \
                (self.tags_loc in ["top", "bottom", "t", "b"])]
        # else: # inside image box
        #     extra_desired_widths, extra_desired_heights = [0],[0]
        #     min_desired_widths.append(tag_sizes[0] * \
        #         (self.tags_loc in ["left", "right", "l", "r"]))
        #     min_desired_heights.append(tag_sizes[1] * \
        #         (self.tags_loc in ["top", "bottom", "t", "b"]))

        return min_desired_widths, extra_desired_widths, \
            min_desired_heights, extra_desired_heights

    def _calculate_margin_sizes(self, to_inches=False):
        """
        calculates marginal sizes needed to be displayed for titles

        Arguments
        ---------
        to_inches : boolean
            if the output should be converted to inches before returned

        Returns
        -------
        min_desired_widths : float
        extra_desired_widths : float
        min_desired_heights : float
        extra_desired_heights : float

        TODO: need to make sure left/right objects are correctly rotated...
        """
        min_desired_widths = \
            [t._min_size(to_inches=to_inches)[0] for t in [self.title.get("top"),
                                        self.title.get("bottom"),
                                        self.subtitle.get("top"),
                                        self.subtitle.get("bottom"),
                                        self.caption]
                if t is not None]
        extra_desired_widths = \
            [t._min_size(to_inches=to_inches)[0] for t in [self.title.get("left"),
                                        self.title.get("right"),
                                        self.subtitle.get("left"),
                                        self.subtitle.get("right")]
                if t is not None]
        min_desired_heights = \
            [t._min_size(to_inches=to_inches)[1] for t in [self.title.get("left"),
                                        self.title.get("right"),
                                        self.subtitle.get("left"),
                                        self.subtitle.get("right")]
                if t is not None]
        extra_desired_heights = \
            [t._min_size(to_inches=to_inches)[1] for t in [self.title.get("top"),
                                        self.title.get("bottom"),
                                        self.subtitle.get("top"),
                                        self.subtitle.get("bottom"),
                                        self.caption]
                if t is not None]

        return min_desired_widths, extra_desired_widths, \
            min_desired_heights, extra_desired_heights


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
        #TODO: likely can remove some of the other index stuff due to passing

        if len(self.tags) <= 1 or len(self.tags_format) <= 1:
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
                                    tags_format=other.tags_format,
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



