import numpy as np

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
