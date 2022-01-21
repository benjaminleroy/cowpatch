# Package development

Statistical python package development has changed since I entered graduate
school mostly for the better, but also some parts for the more complicated. In
generally it used to be the wild west, but now people from UW have proposed
an approach with similar wrappings to `R`'s `devtools` called
[`py-pkgs`](https://github.com/py-pkgs).

It's actually a quick read (and might even be useful to create a dummy package
to get some understanding of the process). Note that `py-pkgs` is still being
developed. I've see 3 pretty different iterations. This has costs, but hopefully
you're getting in when it's closer to stable.

## Constraints (package manager)

This package's approach is to manage dependencies with `poetry`. `poetry` has
similar uses as `conda` and `pip` (aka it manages dependencies) but with
different structural uses. Additionally it doesn't actually play that nicely
with the other too (whereas `conda` and `pip` always respected each-other).
My recommendation would to make a virtual env (using `conda` or `pip`) and then
don't install things on it - just let `poetry` do the package management.

## General thoughts (working with `poetry`)

### editable package (like `pip install -e .`)

`poetry` **does** install an editable version of the package. So every time you
launch a `python`[^1] you will get the most up-to-date version of the package
you have.

[^1]: after the first time running `poetry install` (see comments in usage)...

### usage

`poetry` manages things slightly different than other package managers but also
provides our new package clean ways to understand it's dependencies and more.
*As of Jan 20, I haven't cleaned up the `pyproject.toml` file but we could need
to clean it up a bit since it started when I was assuming `.png` structure. I'm
deal with that.* Here are some general commands (which need to be run at the
root folder (where the `pyproject.toml` file is)).

- `poetry add package_name`:
    this adds `package_name` as a dependency for the package (so if people use
    the package they'll need `package_name` downloaded as well). Sometimes there
    will be conflicts but they shouldn't be too hard to figure out (and `poetry`
    does do a good job with this generally). *Note that if you accidently do
    some `pip` or `conda` installing this might not be easy to resolve.*
- `poetry add --dev package_name`:
    this addes `package_name` as a package for your environment when working on
    the package, but **not** as a dependency. Generally I use this if I need a
    package for testing but not for the package itself (I'm not 100% other
    uses...). Apparently this approach is recommended in
    [`py-pkgs`](https://github.com/py-pkgs) to installing `pytest` since
    it's used to test the package but not needed to be included in it...
- `poetry install`:
    this updates the package with respect to new dependencies you (or I) may
    have added. This means you **do** need to run it after doing
    `poetry add ...`, etc.

### disclaimer

I am still struggling with understanding `poetry`'s power, so it's possible
something I said above isn't correct (or is a misinterpretation).


