# Strategy

## Recap on Gap

The `python` package `plotnine` currently cannot easily create arangement of plots to a similar level to `R`'s `gridExtra`, `cowplot` and `patchwork`'s ability to do so for `ggplot2`. This is because of how `plotnine` is built on `matplotlib` and is therefore directly effected by how `matplotlib` create structure and manage subplots.

## Solution Strategy

Instead of focusing on building completely python data approaches (through altering `matplotlib` structure and then `plotnine`), we propose using image represent in SVG objects and performing `gridExtra`, `cowplot` and `patchwork` combinations of plots, etc within the SVG framework. Using an SVG base structure makes a lot of sense (especially w.r.t. to png objects) as SVG objects create "scalable vector graphics". This file type can be scaled after saving the file (which fits into the academic paradigm of creating both papers and posters with very different scales). SVG objects can, in theory be zoomed in forever without lost of quality of image. Additionally, SVG objects can naturally be converted to raster files (like png and jpeg files) as well.

# Understanding SVG objects

SVG objects have some clear structure.

1. the svg objects' text look a lot like `.html` files (they are acutaly XML-based)
2. the define locations of objects (relative or globally) with respect to an origin at the top left of the figure. This makes it more like `html` than a standard cartesian plot that has a origin at the bottom left of the plot (classically).
3. There are some basic elements of SVGs, including
    - text (`<text style="font: 8.8px 'Dejavu Sans'">actual text</text>`)
    - paths (`<path d="M 0 0 L 200 200 z"/>`)
    - groupings (`<g id="my_id"> ... </g>`)
4. Objects can be scaled, shifted, etc. using the `transform=` parameter. This functionality impacts all children of the object (even if the inner objects have locations defined in a global sense). Function examples include:
    - `scale(a,b)` or `scale(a)`: if are included the first scalar defines x scaling and the second defines y-scaling
    - `translate(c, d)`: this shifts the associated upper left point of the object by (c,d) in the base units.
    - others like `rotate(...)` and `skewX(...), skewY(...)` do similar transformations (and you can techically do a lot at  once with a matrix), but are probably not that useful to us.
5. Units in SVG are a little abstract, but you can specify different sizes and unit types. Because of the dpi saving goal some of these are less flexible than SVG documentation seems to allow. Generally the following conversions exist:
    - inches -> px: 1/72
    - inches -> pt: 1/96
    - px -> pt: 3/4
6. With `width`s and `height`s you can also specify "100%", etc. styles (more akin to `html`). This kinda relates to the fact that when getting information out of a matplotlib object we often need to tell it to basically "render" the object to actually get desirable non abstract information about objects
