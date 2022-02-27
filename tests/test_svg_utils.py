from pytest_regressions import image_regression
import pytest
import numpy as np

import io
import cowpatch.svg_utils
import cowpatch.utils

import svgutils.transform as sg

import plotnine as p9
import plotnine.data as p9_data

def test__save_svg_wrapper(image_regression):
    """
    image regression for _save_svg_wrapper (png only)

    we are showing that if we have known svgutils.transform object (known
    w.r.t. a plotnine plot definition), then the saved png object of the svg
    object is static/doesn't regress.
    """
    p0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.facet_wrap("cyl") +\
        p9.labs(title = 'Plot 0')

    image_width = 6
    image_height = 4
    inner_dpi = 96

    with io.StringIO() as fid1:
        p0.save(fid1, format="svg", width = image_width,
                height=image_height, verbose = False)
        fid1.seek(0)
        sg_obj = sg.fromstring(fid1.read())
        with io.BytesIO() as fid2:
            cowpatch.svg_utils._save_svg_wrapper(svg=sg_obj,
                                        width=image_width,
                                        height=image_height,
                                        _format="png",
                                        dpi=inner_dpi,
                                        filename=fid2,
                                        verbose=False)

            image_regression.check(fid2.getvalue(), diff_threshold=.1)

def test__raw_gg_to_svg(image_regression):
    """
    image regression for _raw_gg_to_svg

    we are showing that the _raw_gg_to_svg function preserves a ggplot's
    image (and doesn't regress)
    """

    mtcars = p9_data.mpg

    p0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.facet_wrap("cyl") +\
        p9.labs(title = 'Plot 0')

    image_width = 6
    image_height = 4
    inner_dpi = 96
    svg_obj = cowpatch.svg_utils._raw_gg_to_svg(p0,
                                      width=image_width,
                                      height=image_height,
                                      dpi=inner_dpi)
    with io.BytesIO() as fid:
        cowpatch.svg_utils._save_svg_wrapper(svg=svg_obj,
                                        width=image_width,
                                        height=image_height,
                                        _format="png",
                                        dpi=inner_dpi,
                                        filename=fid,
                                        verbose=False)

        image_regression.check(fid.getvalue(), diff_threshold=.1)

def test_gg_to_svg__size():
    """
    test underlying power to do size correction of the images (static)
    """
    # regular size image - correct scaling -------
    p0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_bar(p9.aes(x="hwy")) +\
        p9.labs(title = 'Plot 0')

    image_width = 6
    image_height = 4
    inner_dpi = 96

    img = cowpatch.svg_utils.gg_to_svg(p0,
                                       width = image_width,
                                       height = image_height,
                                       dpi = inner_dpi,
                                       eps = 1e-2)

    inches_dim = [cowpatch.utils.to_inches(x, "pt") for x in
            cowpatch.utils._transform_size_to_pt(img.get_size())]

    assert np.allclose(inches_dim, [image_width, image_height],
                       atol = 1e-2), \
        "gg_to_svg should create a svg object with the desired width & "+\
        "height if possible (and up to tolerance)"


    # smaller size - correct scaling -------

    p3_no_legend = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 3 color')

    image_width_s = 4
    image_height_s = 2
    inner_dpi_s = 96

    img_s = cowpatch.svg_utils.gg_to_svg(p3_no_legend,
                                       width = image_width_s,
                                       height = image_height_s,
                                       dpi = inner_dpi_s,
                                       eps = 1e-2,
                                       maxIter=10)

    inches_dim_s = [cowpatch.utils.to_inches(x, "pt") for x in
            cowpatch.utils._transform_size_to_pt(img_s.get_size())]

    assert np.allclose(inches_dim_s, [image_width_s, image_height_s],
                       atol = 1e-2), \
        "gg_to_svg should create a svg object with the desired width & "+\
        "height if possible (and up to tolerance) - (smaller size check, "+\
        "higher maxIter)"


    # errors with too small legend scaling: --------
    p3_color_legend = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +\
        p9.labs(title = 'Plot 3 color')

    image_width_f = 4
    image_height_f = 2
    inner_dpi_f = 96

    with pytest.raises(Exception) as e_info:
        img_fail = cowpatch.svg_utils.gg_to_svg(p3_color_legend,
                                       width = image_width_f,
                                       height = image_height_f,
                                       dpi = inner_dpi_f,
                                       eps = 1e-2)

def test_gg_to_svg__image(image_regression):
    """
    makes sure the visualization stays the desired size and type
    """
    p3_no_legend = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 3 color')

    image_width_s = 4
    image_height_s = 2
    inner_dpi_s = 96

    img_s = cowpatch.svg_utils.gg_to_svg(p3_no_legend,
                                       width = image_width_s,
                                       height = image_height_s,
                                       dpi = inner_dpi_s,
                                       eps = 1e-2,
                                       maxIter=10)

    with io.BytesIO() as fid:
        cowpatch.svg_utils._save_svg_wrapper(svg=img_s,
                                        width=image_width_s,
                                        height=image_height_s,
                                        _format="png",
                                        dpi=inner_dpi_s,
                                        filename=fid,
                                        verbose=False)

        image_regression.check(fid.getvalue(), diff_threshold=.1)

def test__select_correcting_size_svg():
    # don't expect error -------

    g0 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ")) +\
        p9.labs(title = 'Plot 0')

    desired_width = 5
    desired_height = 4

    width, height, boolean = \
        cowpatch.svg_utils._select_correcting_size_svg(g0,
                                                   height = desired_height,
                                                   width = desired_width,
                                                   dpi = 96)
    assert boolean, \
        "expected _select_correcting_size_svg to succeed..."

    assert 1/3 < np.abs(width/desired_width) < 3, \
        "suggested width isn't too extreme - this is just a sanity check, "+\
        "not a robust test"

    assert 1/3 < np.abs(height/desired_height) < 3, \
        "suggested height isn't too extreme - this is just a sanity check, "+\
        "not a robust test"

    # expected error -------

    # throw_error = False

    g1 = p9.ggplot(p9_data.mpg) +\
        p9.geom_point(p9.aes(x="hwy", y = "displ",  color="class")) +\
        p9.labs(title = 'Plot 0 color')

    desired_width_error = 5/4
    desired_height_error = 4/4

    width_scale, height_scale, boolean_fail = \
        cowpatch.svg_utils._select_correcting_size_svg(g1,
                                                   height = desired_height_error,
                                                   width = desired_width_error,
                                                   dpi = 96,
                                                   throw_error=False)

    assert not boolean_fail, \
        "expected _select_correcting_size_svg to fail if desired is much to "+\
        "small (and plot has legend)"

    assert 0 < width_scale < 1, \
        "suggested width scaling is less than 1 "+\
        "(it's an inverse scaling for some reason)..."

    assert 0 < height_scale < 1, \
        "suggested height scaling is less than 1 "+\
        "(it's an inverse scaling for some reason)..."

    # throw_error = True

    # incorrect sizings error
    with pytest.raises(Exception) as e_info:
        cowpatch.svg_utils._select_correcting_size_svg(g1,
                                               height = desired_height_error,
                                               width = desired_width_error,
                                               dpi = 96,
                                               throw_error=True)

    assert e_info.value.args[0] == "height or width is too small for "+\
            "acceptable image", \
        "expected error when throw_error =True (sizing to small) not observed"

    with pytest.raises(Exception) as e_info:
        cowpatch.svg_utils._select_correcting_size_svg(g0,
                                               height = desired_height,
                                               width = desired_width,
                                               dpi = 96,
                                               maxIter=1,
                                               throw_error=True)

    assert e_info.value.args[0] == "unable to get correct size within "+\
            "epsilon and number of interations", \
        "expected error when throw_error =True (not enough interations "+\
        "to succeed) not observed"

