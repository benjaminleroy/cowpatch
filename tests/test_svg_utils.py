from pytest_regressions import image_regression

import pytest
import numpy as np

import io
import cowpatch.svg_utils
import cowpatch.utils
import cowpatch.layout_elements

import svgutils.transform as sg

import plotnine as p9
import plotnine.data as p9_data

import copy

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

def test__uniquify_svg_safe(image_regression):
    """
    static test for _uniquify_svg_safe to confirm that we can have
    multiple different legend gradients.
    """

    vis1 = p9.ggplot(p9_data.mtcars) +\
        p9.aes('wt', 'mpg', color='hp') +\
        p9.geom_point()


    vis2 = p9.ggplot(p9_data.mtcars) +\
        p9.aes('wt', 'mpg', color='hp') +\
        p9.geom_point() +\
        p9.scale_color_continuous('inferno')

    str_update_all = ["_bpl_0", "_bpl_1"]

    store_images = [cowpatch.svg_utils._raw_gg_to_svg(x,
                        width=5,
                        height=4,
                        dpi=96)
                            for x in [vis1, vis2]]

    store_images_updated = [cowpatch.svg_utils._uniquify_svg_safe(
                                store_images[idx],
                                str_update_all[idx])
                                    for idx in [0,1]]

    width_pt = 72*10
    height_pt = 72*4

    store_location = [cowpatch.layout_elements.area(x_left=0.0,
                                           y_top=0.0,
                                           width=360.0,
                                           height=288.0,
                                           _type="pt"),
                      cowpatch.layout_elements.area(x_left=360.0,
                                           y_top=0.0,
                                           width=360.0,
                                           height=288.0,
                                           _type="pt")]

    base_created_image_u = sg.SVGFigure()
    base_created_image_u.set_size((str(width_pt)+"pt", str(height_pt)+"pt"))
    base_created_image_u.root.set("viewBox", "0 0 %s %s" % (str(width_pt), str(height_pt)))

    base_created_image_u.append(
        sg.fromstring("<rect width=\"100%\" height=\"100%\" fill=\"#FFFFFF\"/>"))

    for p_idx in [0,1]:
        inner_svg = copy.deepcopy(store_images_updated[p_idx])
        inner_root = inner_svg.getroot()
        inner_area = copy.deepcopy(store_location[p_idx])

        inner_root.moveto(x=inner_area.x_left,
                          y=inner_area.y_top)
        base_created_image_u.append(inner_root)

    with io.BytesIO() as fid:
        cowpatch.svg_utils._save_svg_wrapper(base_created_image_u,
                          filename=fid,
                          _format="png",
                          width=10,
                          height=4,
                          dpi=96,
                          verbose=False)

        image_regression.check(fid.getvalue(), diff_threshold=.1)
