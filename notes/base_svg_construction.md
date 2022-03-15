# Base svg construction for `cow.patch`

*March 12, 2022*

This document aims to capture how `cow.patch` creates `svg objects for the user.`

## upper level understanding

`cow.patch` and `cow.layout` work together to provide and store information about the layout of objects (within `cow.layout`) and the objects themselves (within `cow.patch`). `cow.patch` directly allows for nesting and `cow.layout` provides layout information for a single level.

It should be useful to note that `cow.layout` expresses layouts in grid, and often will do so with an underlying matrix expression underneath.

## `cow.layout` focused

`cow.layout` provides two functions that relate to `cow.patch`'s work to creat an svg image.

1. `_element_locations`: this function is a major workforce, and translates the abstract loctional structure provided by the user into locations and sizes for each plot to be placed. It returns information in terms of `cow.area(_type="pt")` objects and requires information about the overall arangement's width and height.

2. `_yokogaki_ordering`: this function isn't super impressive (and uses `_element_locatioons` to do a lot of processing), but this function tracks the (left->right, top-> bottom) order of the plots (hopefully to, in the future help with plot labeling).

## `cow.patch` focused

### why it's complicated

To aid the user, `cowpatch`'s underlying code attempts to deal with a lot of complex internal in an "out of sight, out of mind". Particularly impactful is the fact that `plotnine` `ggplot` object's size when saved is different than the input images due to a `matplotlib` `bbox="tight"` decision. In the worst case scenario, this might mean that the size of the output requested is not possible. Additionally, the general goal of not requiring the user to provide widths and heights automatically, encourages additional analysis to propose acceptable sizes of figures. Both of these are combined with the array of complex combinations of plots the user can propose, most notably the nesting structure of images.

### estimating default sizing

`cow.patch` estimates the "optimal" default sizing with the idea that the minimum width and height of any plot (at any nesting level) should probably be a lower bounded. These lower bounds mirror ideas in `R`'s `cowplot` package and also attempt to naturally avoid some sizing problems as described in the subsection above.

Two functions (of `cow.patch`) relate to this estimation:

1. `_size_dive`: This function looks through potential nested structure to provide a desired width and height of the global / top level `cow.patch` relative to underlying global parameters stored in `cow.rcParams`.
2. `_default_size`: wraps around the `_size_dive` to give recommended width and heights relative to any width and height information given to the user (this is only in terms of missingness - i.e. when a user provides only part of the width+height requests or non of it)

### creating the svg object

The inner `_svg` function works to provide the svg object requested, updating sizes if requested & necessary. It relies on a set of other functions to process information efficiently and relies on global parameters to mask some of the decision making process. These functions (and global parmeters) include:

1. `_svg_get_sizes`: this function looks at all plots (including nested plots) and calculates the optimal size to request so that the output is of the correct size. It also tracks if such attempts fail, and if so, the relative difference between the desired size and the returned size given the desired size as imput.
2. `_process_sizes`: this function processes information from `_svg_get_sizes`, either returning a nested list of sizes to use as input to create the correct size of plots, or a scalar float of the scaling to be preformed of the global sizes to likely avoid problems

The overall approach (as reflected in some of the descriptions above) is as follows:

1. **Process and examines sizes**:

    The first step involves leveraging the above functions to collect the parameters to save the plots with so that they come out the correct size (in `_svg_get_sizes`).

    This procedure, as noted in the information above, also identifies (1) if
    there were sizing errors (within `_svg_get_sizes`), and (2) a potential
    scaling to the originally requested global size to avoid these errors
    (within `_process_sizes`). To actually select the global size and get the
    correct input sizes for each plot, we leverage a global parameter
    `cow.rcParams["num_attempts"]` (default: `2`) which describes the number
    of times we'll run the above 2-part process.


    <details>
        <summary>Code block</summary>
        <pre><code>
        if num_attempts is None:
            num_attempts = rcParams["num_attempts"]
        # examine if sizing is possible and update or error if not
        # --------------------------------------------------------
        if sizes is None: # top layer
            #pdb.set_trace()
            while num_attempts > 0:
                sizes, logics = self._svg_get_sizes(width_pt=width_pt,
                                                    height_pt=height_pt)
                out_info = self._process_sizes(sizes, logics)
                if type(out_info) is list:
                    num_attempts = -412 # strictly less than 0
                else: # out_info is a scaling
                    width_pt = width_pt*out_info
                    height_pt = height_pt*out_info
                num_attempts -= 1
            if num_attempts == 0:
                raise StopIteration("Attempts to find the correct sizing of inner"+&#92;
                            "plots failed with provided parameters")
        </code></pre>
    </details>

2. **obtain locations (relative to potentially new sizes)**:

    After obtaining the best size for the arangement (potentially updated), and
    the input sizes for all subplots, we still need to obtain the expected
    locations in the svg that each "grob" will be. We do so with the
    `layout._element_locations` function. As mentioned a while above, this
    function returns `cow.area` objects that provide one with the upper left
    corner location of the image (and the height and width, but that's less
    important at this point).

    <details>
        <summary>Code block</summary>
        <pre><code>
        layout = self.layout
        areas = layout._element_locations(width_pt=width_pt,
                                          height_pt=height_pt,
                                          num_grobs=len(self.grobs))
        </code></pre>
    </details>

3. **create a base image**:

    To start build the svg object we then build a base image to place the other
    svg objects on top of.

    <details>
        <summary>Code block</summary>
        <pre><code>
        base_image = sg.SVGFigure()
        base_image.set_size((str(width_pt)+"pt", str(height_pt)+"pt"))
        # add a view box... (set_size doesn't correctly update this...)
        # maybe should have used px instead of px....
        base_image.root.set("viewBox", "0 0 %s %s" % (str(width_pt), str(height_pt)))
        # TODO: way to make decisions about the base image...
        base_image.append(
            sg.fromstring("&lt;rect width=&#92;"100%&#92;" height=&#92;"100%&#92;" fill=&#92;"#FFFFFF&#92;"/&gt;"))
        </code></pre> <!-- sorry for html symbols above, see actual code for real code -->
    </details>

4. **placing inner images**:

    Finally, we look through the top layer of plot objects and place them on top of the base image. Note that this procedure is recursive, but passes the sizing information with the `_svg(sizes=...)` parameter so the first step is not repeated each level (given it was a nested calculation to begin with).

    <details>
        <summary>Code block</summary>
        <pre><code>
        for p_idx in np.arange(len(self.grobs)):
            inner_area = areas[p_idx]
            # TODO: how to deal with ggplot objects vs patch objects
            if inherits(self.grobs[p_idx], patch):
                inner_width_pt, inner_height_pt = inner_area.width, inner_area.height
                inner_svg, _ = self.grobs[p_idx]._svg(width_pt = inner_width_pt,
                                                   height_pt = inner_height_pt,
                                                   sizes =  sizes[p_idx])
            elif inherits_plotnine(self.grobs[p_idx]):
                inner_gg_width_in, inner_gg_height_in  = sizes[p_idx]
                inner_svg = _raw_gg_to_svg(self.grobs[p_idx],
                                      width = inner_gg_width_in,
                                      height = inner_gg_height_in,
                                      dpi = 96)
            else:
                raise ValueError("grob idx %i is not a patch object nor"+&#92;
                                 "a ggplot object within patch with hash %i" % p_idx, self.__hash__)
            inner_root = inner_svg.getroot()
            inner_root.moveto(x=inner_area.x_left,
                              y=inner_area.y_top)
            base_image.append(inner_root)
        </code></pre>
    </details>

5. **returns base svg object and sizing**:

    Because we may have changed the size of the output image, we return the svg object and the it's size.


    <details>
        <summary>Code block</summary>
        <pre><code>
        return base_image, (width_pt, height_pt)
        </code></pre>
    </details>


