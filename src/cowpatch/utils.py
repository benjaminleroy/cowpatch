import numpy as np
import plotnine as p9
import inspect

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
    if units == "pt":
        return value

    # metric to inches
    if units == "cm":
        value = value/2.54
        unit = "in"

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
        length in measurement units
    units : str
        unit type (e.g. "pt", "px", "in", "cm", "mm")
    dpi : float / int
        dots per inch (conversion between inches and px)

    Return
    ------
    length given units
    """
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
    raise ValueError("TODO: impliment")

def from_inches(value, units, dpi=96):
    raise ValueError("TODO: impliment")


def inherits_plotnine(other):
    """
    checks if object is a plotnine one (but really only checks if comes
    from plotnine package...)
    """
    # https://stackoverflow.com/questions/14570802/python-check-if-object-is-instance-of-any-class-from-a-certain-module
    module_tree = getattr(other, '__module__', None)
    parent = module_tree.split('.')[0] if module_tree else None

    return "plotnine" == parent
