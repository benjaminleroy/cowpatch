# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

## Types of Contributions

### Report Bugs

If you are reporting a bug, please make sure you provide

* A reproducible data example (including all package imports, data imports and
full code). This may mean that you will need to "dumb"-down your problem.

Beyond that, please provide

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it. If you are fixing bugs please
add additional tests to capture what the bug was.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it. Additionally, if you
see anything in the future goals that looks interesting to develop please feel
free to reach out to Ben via email to connect.

### Write Documentation

You can never have enough documentation! Please feel free to contribute to any
part of the documentation, such as the official docs, docstrings, or even 
on the web in blog posts, articles, and such.

We'll be explaining this section to describe how we automate this process (and
highlight the easy of contributing to documentation) soon. We're taking "pages"
from [Anne Gentle](https://www.docslikecode.com/about/) who has writes
[books](https://www.docslikecode.com) on
good continuous integration style documentation and gives
[talks](https://www.youtube.com/watch?v=vM4vw2L-mG0&list=PL2k86RlAekM99X06brRLLp8Is1Jexw5wd&index=14)
on things like simple github based documentation pages. An additional useful
resource to what types of docs do we need might be writethedocs.org's [guide](https://www.writethedocs.org/guide/).

### Write Additional Tests

Generally speaking, the more tests the better. Additionally, given this was
developed as a "statistical package", many functions and classes were not
created in a "test-driven" fashion, so capturing additional use cases/edge case
is looking upon favorably.

To test `svg` and general objects we use the `pytest-regressions` package (and
specifically it's `image_regression` tools. A member of the development team
gave a talk at PyCon 2020 which can be found on youtube
[here](https://youtu.be/YBuVGx3EYSY?t=1423). Beyond this talk and
package [documentation](https://pytest-regressions.readthedocs.io/) don't
capture how to use the tool clearly enough please see the `test/` folder's
tests.

Given this is a "statistical package" (in some sense), we are also leveraging
the [`hypothesis`](https://hypothesis.readthedocs.io/en/latest/) python package.

### Submit Feedback

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `cowpatch` for local development.

1. Download a copy of `cowpatch` locally.
2. Install `cowpatch` using `poetry`:

    ```console
    $ poetry install
    ```

3. Use `git` (or similar) to create a branch for local development and make your changes:

    ```console
    $ git checkout -b name-of-your-bugfix-or-feature
    ```

4. When you're done making changes, check that your changes conform to any code formatting requirements and pass any tests.

5. Commit your changes and open a pull request.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include additional tests if appropriate.
2. If the pull request adds functionality, the docs should be updated.
3. The pull request should work for all currently supported operating systems and versions of Python (a subset of these will be checked with Github actions).

## Code of Conduct

Please note that the `cowpatch` project is released with a 
Code of Conduct. By contributing to this project you agree to abide by its terms.
