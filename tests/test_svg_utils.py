import cowpatch as cow

def def_test_gg_to_svg():
    """
    this test is just testing consistency
    """
    # new example --------
    # https://github.com/pyvista/pyvista/blob/main/tests/plotting/test_plotting.py


    # old notes --------
    #from matplotlib.testing.decorators import image_comparison
    # https://github.com/matplotlib/matplotlib/blob/f6e0ee49c598f59c6e6cf4eefe473e4dc634a58a/lib/matplotlib/tests/test_png.py
    # https://www.pyimagesearch.com/2014/09/15/python-compare-two-images/
    # ^ compare image pixels ()

    # https://pypi.org/project/pixelmatch/ (# of pixels mismatched)

    # ^ plotnine saves png images (could also save svg objects... but harder to compare...)
    # https://github.com/has2k1/plotnine/tree/master/plotnine/tests/baseline_images
    # should we have differences somewhere?

    # ^ good snapshot test (but I'm currently worried about change element ordering in strings.)

    # probably do something like plotnine (but not 100% sure about updating, etc.)

    pass
