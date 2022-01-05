# Navigating scaling and fixed aspect ratios

The current idea for this package is to create a image object[^1] then do a minor scaling to perfect fit the desired size for the object (with respect to the global image). The python file `proof_of_concept.py` file presents an example of the type of approach I'm thinking.

[^1]: In this case a `svg` but likely this problem would also occur in a different way with `png`, etc.

The next question is then, how to navigate scaling of objects and when to not scale, only scale with a fixed aspect ratio or generally scale. I think we can successfully do so within the `svg` space with a few tools (I'm guessing a `svg` style proof of concept and then convert that into a more general `python` wrapper).

A few articles I've skimmed and would like to make better use of include:

1. [CSS-tricks: scale parts of SVG seperately](https://css-tricks.com/scale-svg/#how-to-scale-parts-of-an-svg-separately) - this article discusses use of `perserveAspectRatio` and `viewBox` and specifically presents "silo"-ing each object (that has you want to have different scalings/aspect ratio approaches).
2. [stackoverflow: Preserve aspect ratio for SVG Text](https://stackoverflow.com/a/61139485/5760387) - this discussion captures simlar things to the "CSS-tricks"'s article, but helpfuls reinforce the idea of sub-class `svgs`.
3. [mathplotlib: SVG Histogram](https://matplotlib.org/stable/gallery/user_interfaces/svg_histogram_sgskip.html) - this article may be useful for the pythonic implimentation of any approaches (though sadly highlights that `matplotlib` uses more `<g>` tags and less seperation of elements).
4. [svgutils: python package](https://svgutils.readthedocs.io/en/latest/) - this is the current package we're using to transform the images. They use the `transform` attribute to `scale` and `shift` objects. This is useful to understand but we may actually need to write our own. It does demonstrate use of the `lxml.etree` package to manipulate the `svg` code (e.g. [source code: `svgutils.transform`](https://svgutils.readthedocs.io/en/latest/_modules/svgutils/transform.html#FigureElement)).

## What's next

My next thing to skim / read is this [w3 chapter](https://www.w3.org/TR/SVG2/coords.html), which discusses the coordinate systems, transformations and `viewBox` + `preserveAspectRatio` attributes.

In the `basic_clean.svg` file you'll see an example of a basic svg image (`plotnine` `ggplot` image cleaned up so we can easily test things out). The first thing to notice is that the circle and bounding box rectangle are `svg` `path` objects - but more specifically, the coordinates use capital `M`, `L` and `C` descriptions (which are **exact** not **relative** descriptors, which means using the `transform` attribute is a little tricky). I imagine the [w3 chapter](https://www.w3.org/TR/SVG2/coords.html) will help understand the best approach for us (and how to manipulate the objects cleanly).

### My current approach

After reading the [w3 chapter](https://www.w3.org/TR/SVG2/coords.html) I'll be trying to figure out the cleanest ways to scale things (with and without aspect ratio) and how to deal with text (which we actually don't want scaled at all- but wanted centered at the correct location). Probably will require segmentation of `svg` code like [CSS-tricks: scale parts of SVG seperately](https://css-tricks.com/scale-svg/#how-to-scale-parts-of-an-svg-separately), understanding how to redefine object's anchoring locations and more.

# Other things

1. Matplotlib defaults with non-text output (see [stackoverflow](https://stackoverflow.com/questions/34387893/output-matplotlib-figure-to-svg-with-text-as-text-not-curves) - already fixed in `proof_of_concept.py`)
2. potentially useful to find center of object with bounding box (see [stackoverflow](https://stackoverflow.com/questions/56512018/finding-the-center-point-coordinates-of-svg/56537308))
3. understanding svg `paths` and other object specification ([mozilla docs: SVG paths](https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths))





# How to manipulate the `svg` objects

To explore the `svg` objects, I'll open the object in a web browser for quick refreshing, then also open it in a text editor (like `Sublime`).
