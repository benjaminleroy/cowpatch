import numpy as np
import pandas as pd
import plotnine as p9
import cowpatch as cpt
import unittest
import svgutils


# Predefined plots
# -----------------
# from https://github.com/thomasp85/patchwork/blob/master/tests/testthat/helper-setup.R
mtcars = pd.read_csv('https://gist.githubusercontent.com/ZeccaLehn/4e06d2575eb9589dbe8c365d61cb056c/raw/64f1660f38ef523b2a1a13be77b002b98665cdfe/mtcars.csv')


p1 = (p9.ggplot(mtcars) +\
  p9.geom_point(p9.aes(x = "mpg", y="disp")) +\
  p9.labs(title = 'Plot 1'))

p2 = p9.ggplot(mtcars) +\
  p9.geom_boxplot(p9.aes(x="gear",y= "disp", group = "gear")) +\
  p9.labs(title = 'Plot 2')

p3 = p9.ggplot(mtcars) +\
  p9.geom_point(p9.aes(x="hp", y="wt", color = "mpg")) +\
  p9.labs(title = 'Plot 3')

p4 = p9.ggplot(mtcars) +\
  p9.geom_bar(p9.aes(x="gear")) +\
  p9.facet_wrap("cyl") +\
  p9.labs(title = 'Plot 4')


# test 1:
#
def test_cowpatch1():
    """
    test cowpatch and layout structure

    The subtests in this internal function check
    1.
    """


    design = np.array([[0,1,1,0],
                      [1,2,2,1],
                      [1,2,2,1],
                      [0,np.nan,np.nan,0]])
    width = np.ones(4)/4
    height = np.ones(3)/3


    cpt1 = cpt.cowpatch(grobs = [p1,p2,p3])
    cpt1_l = cpt1 + cpt.layout(design = design)

    #cpt1_l.show()


    design = np.array([[1,1,0,0,np.nan,np.nan,np.nan,np.nan],
                      [1,1,0,0,np.nan,np.nan,np.nan,np.nan],
                      [0,0,0,0,2,2,2,2],
                      [0,0,0,0,2,2,2,2]])


    cpt1 = cpt.cowpatch(grobs = [p1,p2,p3])
    cpt1_l = cpt1 + cpt.layout(design = design)
    image = cpt1_l._create_png(width = 4, height = 4)


def test_cowpatch_svg1():
    design = np.array([[1,1,3,3,np.nan,np.nan,np.nan,np.nan],
                  [1,1,3,3,np.nan,np.nan,np.nan,np.nan],
                  [0,0,0,0,2,2,2,2],
                  [0,0,0,0,2,2,2,2]])

    width = 10
    height = 8
    dpi = 300

    info_dict = {}

    info_dict[0] = dict(full_size = (5.0,4.0),
                        start = (0.0,5.0))
    info_dict[1] = dict(full_size = (2.5,4.0),
                        start = (0.0,0.0))
    info_dict[2] = dict(full_size = (5.0,4.0),
                        start = (5.0,4.0))
    info_dict[3] = dict(full_size = (2.5,4.0),
                        start = (2.5,0.0))

    grobs = [p1,p2,p3,p4]

    full_width = width * dpi
    full_height = height * dpi

    full_width_pt = str(width * 72)+"pt"
    full_height_pt = str(height * 72)+"pt"

    base_image = sg.SVGFigure(width = full_width_pt,
                              height = full_height_pt) # hoping for the best...
    base_image.set_size((full_width_pt, full_height_pt))
    base_image.append(sg.fromstring("<rect width=\"100%\" height=\"100%\" fill=\"red\"/>"))

    for p_idx in np.arange(4, dtype = int):
        svg = gg_to_svg(grobs[p_idx],
                              width = info_dict[p_idx]["full_size"][0],
                              height = info_dict[p_idx]["full_size"][1],
                              dpi = dpi)
        inner_root = svg.getroot()
        inner_root.moveto(info_dict[p_idx]["start"][0] * 72,
                           info_dict[p_idx]["start"][1] * 72)
        base_image.append(inner_root)

    base_image.save("hopeful.svg")



   # pt = inch * 72





## functions to test: _design_to_structure...

def test_cowpatch__design_to_structure():
    ## inner test 1 --------------
    # same size height and width, cuts of multiple structures
    #

    design = np.array([[0,1,1,0],
                  [1,2,2,1],
                  [1,2,2,1],
                  [0,np.nan,np.nan,0]])
    just_layout = cpt.cowpatch() + cpt.layout(design=design)
    # cowpatch layout structure -----
    info_dict_out = just_layout._design_to_structure(350,350,
                                     np.ones(4)*350/4,
                                     np.ones(4)*350/4)

    # expected layout structure -----
    expected_info_dict = {}
    #plot 1
    expected_info_dict[0] = dict(
                      full_size= (350.0,350.0),
                      start=(0.0,0.0),
                      slices=[((0.0,0.0),87.5,87.5),
                              ((0.0,262.5),87.5,87.5),
                              ((262.5,0.0),87.5,87.5),
                              ((262.5,262.5),87.5,87.5)
                              ])
    #plot 2
    expected_info_dict[1] = dict(full_size= (350.0,262.5),
                        start=(0.0,0.0),
                          slices=[((87.5,0.0),87.5,87.5),
                                  ((175.0,0.0),87.5,87.5),
                                  ((0.0,87.5),87.5,87.5),
                                  ((0.0,175.0),87.5,87.5),
                                  ((262.5,87.5),87.5,87.5),
                                  ((262.5,175.0),87.5,87.5)
                                  ])

    #plot 3
    expected_info_dict[2] = dict(full_size = (175.0,175.0),
                                 start= (87.5,87.5),
                                 slices=[((87.5,87.5),87.5,87.5),
                                         ((175.0,87.5),87.5,87.5),
                                         ((87.5,175.0),87.5,87.5),
                                         ((175.0,175.0),87.5,87.5),
                                          ])
    # due to poential different orderings of slices...
    # unittest.TestCase().assertCountEqual(info_dict_out, expected_info_dict)
    # ^ doesn't work...

    ## inner test 2 -------------
    # different dimensions, no direct overlap
    #
    design = np.array([[0.0,np.nan,np.nan],
                  [np.nan,1,1],
                  [np.nan,1,1]])

    just_layout = cpt.cowpatch() + cpt.layout(design=design)
    # cowpatch layout structure -----
    info_dict_out = just_layout._design_to_structure(350,300,
                                     np.ones(3)*350/3,
                                     np.ones(3)*300/3)

    expected_info_dict = {}
    # plot 1
    expected_info_dict[0] = dict(
                      full= (350/3,100.),
                      start=(0.,0.),
                      slices=[((0.,0.),350/3,100.)])
    # plot 2
    expected_info_dict[1] = dict(full= (350*2/3,200.),
                        start=(350/3,100.),
                          slices=[((350/3,100.),350/3,100.),
                                  ((350/3,200.),350/3,100.),
                                  ((350*2/3,100.),350/3,100.),
                                  ((350*2/3,200.),350/3,100.)])
    #unittest.TestCase().assertCountEqual(info_dict_out, expected_info_dict)


    ## inner test 3 ---------------
    # different dimensions, overlap images
    # also different relative sizes
    #

    design = np.array([[0.0,1,1],
                  [1,1,1],
                  [1,1,1]])

    just_layout = cpt.cowpatch() + cpt.layout(design=design)
    # cowpatch layout structure -----

    rel_width = np.array([1.,2,2])
    rel_width /= np.sum(rel_width)
    rel_height = np.array([1.,2,2])
    rel_height /= np.sum(rel_height)
    info_dict_out = just_layout._design_to_structure(350,300,
                                     rel_width*350,
                                     rel_height*300)
    # plot 1
    expected_info_dict = {}
    expected_info_dict[0] = dict(
                      full= (350*1/5,1/5*300),
                      start=(0.,0.),
                      slices=[((0.,0.),350*1/5,1/5*300)])
    # plot 2
    expected_info_dict[1] = dict(full= (350.,300.),
                        start=(0.,0.),
                          slices=[((0.,1/5*300),350*1/5,2/5*300),
                                  ((0.,3/5*300),350*1/5,2/5*300),
                                  ((350*1/5,0.),350*2/5,1/5*300),
                                  ((350*1/5,1/5*300),350*2/5,2/5*300),
                                  ((350*1/5,3/5*300),350*2/5,2/5*300),
                                  ((350*3/5,0.),350*2/5,1/5*300),
                                  ((350*3/5,1/5*300),350*2/5,2/5*300),
                                  ((350*3/5,3/5*300),350*2/5,2/5*300)])

    ## inner test 4+ --------
    # non square design matrix, alphabetic design, ...
    #


# import io
# def gg2img(gg, width, height, dpi=100, limitsize =True):
#     """
#     Convert plotnine ggplot figure to PIL Image and return it

#     Arguments
#     ---------
#     gg: plotnine.ggplot.ggplot
#         object to save as a png image

#     Returns
#     -------
#     PIL.Image coversion of the ggplot object

#     Details
#     -------
#     Associated with the stackoverflow question here: https://stackoverflow.com/questions/8598673/how-to-save-a-pylab-figure-into-in-memory-file-which-can-be-read-into-pil-image/8598881
#     """

#     buf = io.BytesIO()
#     gg.save(buf, format= "png", height = height, width = width,
#             dpi=dpi, units = "in", limitsize = limitsize)
#     buf.seek(0)
#     img = Image.open(buf)
#     return img

# from PIL import Image

# base_image = Image.new("RGB",size= (global_size["full_width"], global_size["full_height"]))

# gg_list = [None,p1,p2,p3]

# for idx in np.arange(1,4):
#     inner_info = info_dict[idx]

#     # inch related
#     inner_png = gg2img(gg_list[idx],
#                        width = inner_info["full"][0]/100,
#                        height = inner_info["full"][1]/100,
#                        dpi = 100,
#                        limitsize=False) # doesn't exactly do what we expected... some roudning...
#     # pixels vs inches and dpi...
#     inner_png = inner_png.resize((int(inner_info["full"][0]),
#                                   int(inner_info["full"][1])))
#     inner_png_array = np.array(inner_png)
#     # np.array(inner_png).shape
#     # pixel related...
#     for s_idx, slice_info in enumerate(inner_info["slices"]):
#         inner_start = slice_info[0]

#         corrected_start = (int(np.floor(inner_start[0])),
#                            int(np.floor(inner_start[1])))

#         inner_width = slice_info[1]
#         inner_height = slice_info[2]

#         c1 = int(np.floor(inner_start[0] - inner_info["start"][0]))
#         c2 = int(c1 + np.ceil(inner_width))

#         r1 = int(np.floor(inner_start[1] - inner_info["start"][1]))
#         r2 = int(r1 + np.ceil(inner_height))

#         inner_image_array_slice = inner_png_array[r1:(r2+1), c1:(c2+1)]
#         inner_image_slice = Image.fromarray(inner_image_array_slice)

#         base_image.paste(inner_image_slice, corrected_start)

# base_image.show()

# #^ plots title are different sizes (which is interesting since dpi is the smae... but I guess inches are not...)


## test 2

design = np.array([[1,None,None],
                  [None,2,2],
                  [None,2,2]])

width = np.ones(3)/3
height = np.ones(3)/3

global_size = dict(
                full_width=350,
                full_height=300)

# rel_width = width * global_size["full_width"]
# rel_height = height * global_size["full_height"]


# info_dict = {}
# # 1
# info_dict[1] = dict(
#                   full= (350/3,100),
#                   start=(0,0),
#                   slices=[((0,0),350/3,100)])
# # 2
# info_dict[2] = dict(full= (350*2/3,200),
#                     start=(350/3,100),
#                       slices=[((350/3,100),350/3,100),
#                               ((350/3,200),350/3,100),
#                               ((350*2/3,100),350/3,100),
#                               ((350*2/3,200),350/3,100)])


# base_image = Image.new("RGB",size= (global_size["full_width"], global_size["full_height"]))

# gg_list = [None,p1,p1]

# for idx in np.arange(1,3):
#     inner_info = info_dict[idx]

#     # inch related
#     inner_png = gg2img(gg_list[idx],
#                        width = inner_info["full"][0]/100,
#                        height = inner_info["full"][1]/100,
#                        dpi = 100,
#                        limitsize=False) # doesn't exactly do what we expected... some roudning...
#     # pixels vs inches and dpi...
#     inner_png = inner_png.resize((int(inner_info["full"][0]),
#                                   int(inner_info["full"][1])))
#     inner_png_array = np.array(inner_png)
#     # np.array(inner_png).shape
#     # pixel related...
#     for s_idx, slice_info in enumerate(inner_info["slices"]):
#         inner_start = slice_info[0]

#         corrected_start = (int(np.floor(inner_start[0])),
#                            int(np.floor(inner_start[1])))

#         inner_width = slice_info[1]
#         inner_height = slice_info[2]

#         c1 = int(np.floor(inner_start[0] - inner_info["start"][0]))
#         c2 = int(c1 + np.ceil(inner_width))

#         r1 = int(np.floor(inner_start[1] - inner_info["start"][1]))
#         r2 = int(r1 + np.ceil(inner_height))

#         inner_image_array_slice = inner_png_array[r1:(r2+1), c1:(c2+1)]
#         inner_image_slice = Image.fromarray(inner_image_array_slice)

#         base_image.paste(inner_image_slice, corrected_start)

# base_image.show()

# ## test 3
# design = np.array([[1,2,2],
#                   [2,2,2],
#                   [2,2,2]])

# width = np.ones(3)/3
# height = np.ones(3)/3

# global_size = dict(
#                 full_width=350,
#                 full_height=300)

# rel_width = width * global_size["full_width"]
# rel_height = height * global_size["full_height"]


# info_dict = {}
# # 1
# info_dict[1] = dict(
#                   full= (350/3,100),
#                   start=(0,0),
#                   slices=[((0,0),350/3,100)])
# # 2
# info_dict[2] = dict(full= (350,300),
#                     start=(0,0),
#                       slices=[((0,100),350/3,100),
#                               ((0,200),350/3,100),
#                               ((350/3,0),350/3,100),
#                               ((350/3,100),350/3,100),
#                               ((350/3,200),350/3,100),
#                               ((350*2/3,0),350/3,100),
#                               ((350*2/3,100),350/3,100),
#                               ((350*2/3,200),350/3,100)])


# base_image = Image.new("RGB",size= (global_size["full_width"], global_size["full_height"]))

# gg_list = [None,p1,p2]

# for idx in np.arange(1,3):
#     inner_info = info_dict[idx]

#     # inch related
#     inner_png = gg2img(gg_list[idx],
#                        width = inner_info["full"][0]/100,
#                        height = inner_info["full"][1]/100,
#                        dpi = 100,
#                        limitsize=False) # doesn't exactly do what we expected... some roudning...
#     # pixels vs inches and dpi...
#     inner_png = inner_png.resize((int(inner_info["full"][0]),
#                                   int(inner_info["full"][1])))
#     inner_png_array = np.array(inner_png)
#     # np.array(inner_png).shape
#     # pixel related...
#     for s_idx, slice_info in enumerate(inner_info["slices"]):
#         inner_start = slice_info[0]

#         corrected_start = (int(np.floor(inner_start[0])),
#                            int(np.floor(inner_start[1])))

#         inner_width = slice_info[1]
#         inner_height = slice_info[2]

#         c1 = int(np.floor(inner_start[0] - inner_info["start"][0]))
#         c2 = int(c1 + np.ceil(inner_width))

#         r1 = int(np.floor(inner_start[1] - inner_info["start"][1]))
#         r2 = int(r1 + np.ceil(inner_height))

#         inner_image_array_slice = inner_png_array[r1:(r2+1), c1:(c2+1)]
#         inner_image_slice = Image.fromarray(inner_image_array_slice)

#         base_image.paste(inner_image_slice, corrected_start)

# base_image.show()



# tests to mirror
## https://github.com/thomasp85/patchwork/blob/master/tests/testthat/test-layout.R
## https://github.com/thomasp85/patchwork/blob/master/tests/testthat/test-arithmetic.R
## https://github.com/wilkelab/cowplot/tree/master/tests/testthat
