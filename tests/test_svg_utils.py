from pytest_regressions import image_regression
import io
import cowpatch.svg_utils
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
