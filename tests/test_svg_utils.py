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
                                        filename=fid2)

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
                                        filename=fid)

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
                                        filename=fid)

        image_regression.check(fid.getvalue(), diff_threshold=.1)
