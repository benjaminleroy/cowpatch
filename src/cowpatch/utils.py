import numpy as np
import plotnine as p9
import inspect
import re

def val_range(x):
    return (np.min(x), np.max(x))

def is_int(x):
    return np.round(x) == x

def is_positive(x):
    return x > 0

def is_non_neg_int(x):
    return is_non_negative(x) and is_int(x)

def is_pos_int(x):
    return is_positive(x) and is_int(x)


def is_proportion(x):
    return x >=0 and x <= 1

def is_non_negative(x):
    return x >= 0

def inherits(object, _class):
    return issubclass(type(object),_class)


# TODO: I'm not 100% sure these conversions do the right thing (especially w.r.t to dpi notation...)
def to_pt(value, units, dpi=96):
    """
    convert length from given units to pt

    Arguments
    ---------
    value : float
        length in measurement units
    units : str
        unit type (e.g. "pt", "px", "in", "cm", "mm")
    dpi : float / int
        dots per inch (conversion between inches and px)

    Return
    ------
    length in pt
    """
    if units not in ["pt", "cm", "mm", "in", "inches", "px"]:
        raise ValueError("please constrain units string parameter to "+\
                         "options listed in doc string")

    if units == "pt":
        return value

    # metric to inches
    if units == "cm":
        value = value/2.54
        units = "in"

    if units == "mm":
        value = value/25.4
        units = 'in'

    # inches to pixels
    if units == "in" or units == "inches":
        value = value * dpi
        units = "px"

    # pixel to pt
    if units == "px":
        value = value * .75
        return value

def from_pt(value, units, dpi=96):
    """
    convert length from pt to given units

    Arguments
    ---------
    value : float
        length in pt
    units : str
        unit type (e.g. "pt", "px", "in", "cm", "mm") to convert to
    dpi : float / int
        dots per inch (conversion between inches and px)

    Return
    ------
    length given units
    """
    if units not in ["pt", "cm", "mm", "in", "inches", "px"]:
        raise ValueError("please constrain units string parameter to "+\
                         "options listed in doc string")

    if units == "pt":
        return value

    # metric to inches
    if units == "cm":
        value = value * 2.54
        units = "in"

    if units == "mm":
        value = value * 25.4
        units = 'in'

    # inches to pixels
    if units == "in" or units == "inches":
        value = value / dpi
        units = "px"

    # pt to px
    if units == "px":
        value = value * 4/3
        return value

def to_inches(value, units, dpi=96):
    """
    convert length from given units to pt

    Arguments
    ---------
    value : float
        length in measurement units
    units : str
        unit type (e.g. "pt", "px", "in", "cm", "mm")
    dpi : float / int
        dots per inch (conversion between inches and px)

    Return
    ------
    length in pt
    """
    pt_val = to_pt(value, units, dpi)
    return from_pt(pt_val, "in", dpi)


def from_inches(value, units, dpi=96):
    """
    convert length from inches to given units

    Arguments
    ---------
    value : float
        length in inches
    units : str
        unit type (e.g. "pt", "px", "in", "cm", "mm") to convert to
    dpi : float / int
        dots per inch (conversion between inches and px)

    Return
    ------
    length given units
    """
    pt_val = to_pt(value, "in", dpi)
    return from_pt(pt_val, units, dpi)

def inherits_plotnine(other):
    """
    checks if object is a plotnine one (but really only checks if comes
    from plotnine package...)
    """
    # https://stackoverflow.com/questions/14570802/python-check-if-object-is-instance-of-any-class-from-a-certain-module
    module_tree = getattr(other, '__module__', None)
    parent = module_tree.split('.')[0] if module_tree else None

    return "plotnine" == parent



def _transform_size_to_pt(size_string_tuple):
    """
    takes string with unit and converts it to a float w.r.t pt

    Arguments
    ---------
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
        return (value[0]*72, value[1]*72)
    elif size_string_tuple[0].endswith("px"):
        return (value[0]*.75, value[1]*.75)
    else:
        raise ValueError("size_string_tuple structure of object not as "+\
                         "expected, new size type")



def _proposed_scaling_both(current, desired):
    """
    identify a x and y scaling to make the current size into the desired size

    Arguments
    ---------
    current : tuple
        float tuple of current size of svg object
    desired : tuple
        float tuple of desired size of svg object

    Returns
    -------
    tuple
        float tuple of scalar constants for size change in each dimension
    """
    scale_x = desired[0]/current[0]
    scale_y = desired[1]/current[1]

    return scale_x, scale_y

def _flatten_nested_list(x):
    """
    Flatten nested list

    Argument
    --------
    x : list
        nested list with different leveling of different objects

    Returns
    -------
    flatten version of list
    """
    out = []
    for xi in x:
        if type(xi) is list:
            out += _flatten_nested_list(xi)
        else:
            out.append(xi)
    return out


_arabic_roman_map = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'),
            (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
def _to_roman_numerials(x, caps = False):
    """
    Arguments
    ---------
    x : int
        arabic numeral
    caps : boolean
        if output should be capitalized

    Returns
    -------
    out : str
        roman numeral
    """
    # from https://stackoverflow.com/a/40274588
    out = ''

    if x > 3999:
        raise ValueError("current implimentation only works for input <= 3999")

    while x > 0:
        for i, r in _arabic_roman_map:
            while x >= i:
                out += r
                x -= i

    if caps:
        return out
    else:
        return out.lower()

_alphabet = "abcdefghijklmnopqrstuvwxyz"
def _to_alphabet_representation(x, caps = False):
    """
    Arguments
    ---------
    x : int
        arabic numeral
    caps : boolean
        if output should be capitalized

    Returns
    -------
    out : str
        alphabet numeric representation
    """
    out = ''
    while x > 0:
        r = x % 26
        out = _alphabet[r-1] + out
        x = x // 26

    if caps:
        return out.upper()
    else:
        return out

def _string_tag_format(max_level=0):
    out = '{0}'
    level = 1
    while level <= max_level:
        out += ".{"+str(level)+"}"
        level +=1

    return out



def _overall_scale_recommendation_single(image_new_size,
                                         text_inner_size,
                                         text_extra_size,
                                         original_overall_size):
    """
    proposal an overall size based on inner image needs and text annotation
    sizes

    Arguments
    ---------
    image_new_size : tuple
        size 2 float tuple with the requested minimum size the inner image can
        be (relative to the image)
    text_inner_size : tuple
        size 2 float tuple with the requested minimum size the inner image can
        be (relative to the surrounding text)
    text_extra_size : tuple
        size 2 float tuple with extra width and height for surrounding text,
        beyond the inner image
    original_overall_size : tuple
        size 2 float tuple of original size provided for the overall image

    Returns
    -------
    out1 : tuple
        size 2 length tuple of newly requested size
    out2 : float
        fraction scaling of new size to old size

    Notes
    -----
    This function assumes ate least one of the new image_new_size values are
    greater than the original requested size (original_overall_size -
    text_extra_sizes)
    """

    min_inner_size_needed = (np.max([image_new_size[i], text_inner_size[i]])
                                for i in [0,1])

    min_overall_size_needed = tuple(np.array(min_inner_size_needed) +\
        np.array(text_extra_size))

    size_ratio = orginal_overall_size[0] / orginal_overall_size[0]

    out_array = np.zeros(2)

    if min_overall_size_needed[1] < 1/size_ratio * min_overall_size_needed[0]:
        out_array[1] = min_overall_size_needed[1]
        out_array[0] = size_ratio * min_overall_size_needed[1]
    else:
        out_array[0] = min_overall_size_needed[0]
        out_array[1] = 1/size_ratio * min_overall_size_needed[0]

    return tuple(out_array), out_array[0]/original_overall_size[0]

def _overall_scale_recommendation_patch(interior_image_scalings,
                                        text_inner_size,
                                        text_extra_size,
                                        original_overall_size):
    """
    proposal an overall size for an arangement based on information about
    interior image and overall text

    Arguments
    ---------
    interior_image_scalings : list
        list of floats. Each value is the requested scaling of a inner image
        (as a function of the image and the associated tag information)
    text_inner_size : tuple
        size 2 float tuple with the requested minimum size the inner image can
        be (relative to the surrounding text)
    text_extra_size : tuple
        size 2 float tuple with extra width and height for surrounding text,
        beyond the inner image
    original_overall_size : tuple
        size 2 float tuple of original size provided for the overall image

    Returns
    -------
    out1 : tuple
        size 2 length tuple of newly requested size
    out2 : float
        fraction scaling of new size to old size

    Notes
    -----
    This function assumes ate least one of the new image_new_size values are
    greater than the original requested size (original_overall_size -
    text_extra_sizes)
    """
    original_inner_size = tuple(np.array(original_overall_size) - \
                                    np.array(text_extra_size))

    inner_new_size_request = \
        np.array(original_inner_size) * np.max(interior_image_scalings + [1])

    out = \
        _overall_scale_recommendation_single(inner_new_size_request,
                                         text_inner_size,
                                         text_extra_size,
                                         original_overall_size)

    return out





