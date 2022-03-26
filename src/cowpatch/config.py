rcParams = dict(maxIter=20,
                min_size_px=10,
                eps=1e-2,

                save_verbose=True,
                show_verbose=True,

                num_attempts=2,

                base_height=3.71,
                base_aspect_ratio=1.618 # the golden ratio

                )
"""
underlying parameters of that control the generation of the actual
images

maxIter : int
    maximum number of iterations to be used to convert
    a plotnine ggplot object output into the correct size
min_size_px : int
    early stopping rule for conversion a plotnine ggplot
    object output into the correct size, if size of image
    goes below this value the process stops with an error
eps : float
    difference between desired and converged sizes to successfully
    stop the interation for the conversion a plotnine ggplot
    object output into the correct size
save_verbose : boolean
    logic if saving a cow.patch arangement (with .save) is is done so
    verbosely as a default (can be overridden)
show_verbose : boolean
    logic if showing a cow.patch arangement (with .show) is is done so
    verbosely as a default (can be overridden)
num_attempts : int
    Number of attempts to correct the global size of the arangment to
    allow the plotnine ggplot objects to have the expected sizes with
    desired aspect ratio. Minimum value is 1, which means no correction is
    made.
base_height : float
    inches for the minimum height of a plotnine ggplot object if no global
    height of the arrangement is provided in the `.show()` and `.save()`
    functions.
base_aspect_ratio : float
    ratio that (along with base_height) defines underlying minimum width
    of a plotnine ggplot object if no global width of the arrangement is
    provided in the `.show()` and `.save()` functions. This ratio is the
    golden ratio.
"""
