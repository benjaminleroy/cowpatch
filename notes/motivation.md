# Package and Package motivation

## Introduction

In `R` now-a-days, `ggplot2` is a very commonly used package (I might even lean
into the idea that it might be more used than the base plot functionality in
`R`). In `python`, there were a few attempts to create Grammar of Graphics style
plots, but it appears as if `plotnine` (around since mid-2017) is the pythonic
equivalent. As will be seen in a later section, `plotnine` is pretty highly used,
and I personally use it and enjoy using it more than `matplotlib` (or `seaborn`).
At the same time, `plotnine` still has a lot of room to grow --or at least
that's one way to put it-- in getting a larger user base. Naturally, one could
imagine that a large amount of the users of `plotnine` may have been interested
as they were also users of `R`. Hopefully, as `plotnine` ages, the value of
the grammar of graphics framework might prove valuable to the larger `python`
userbase (note only 139 plotnine posts on
[stack exchange](https://stackoverflow.com/questions/tagged/plotnine) exist).
Still, there is a constraint to using `plotnine` that may be holding back it's
adoption among both users who have knowledge about `R` and `ggplot2` and those
without such knowledge.

### Gap

One large gap in the `plotnine` toolkit is combining images. In `R` demand for
this type of tool might be estimated at 28% relative to demand for the general
plotting tool (if we compare relative downloads, a shitty metric -- see below).
Three major `R` packages have been developed to combine `ggplot` graphics
together. This is missing in the `python` implimentation.

There are some signal that such a thing would be desirable.

plotnine github issues:
1. [issue 46: how to draw subplots?](https://github.com/has2k1/plotnine/issues/46)
2. [issue 443: combined pdf images](https://github.com/has2k1/plotnine/issues/443)
3. [issue 373: combining plotnine figures](https://github.com/has2k1/plotnine/issues/373)

Moreover, these issues suggest that people are working on data science pipelines
that transition the visualization part to `R` to leverage the larger toolkit
([1](https://github.com/has2k1/plotnine/issues/373#issuecomment-1002204659),
[2](https://github.com/has2k1/plotnine/issues/46#issuecomment-416880143),
[3](https://github.com/has2k1/plotnine/issues/46#issuecomment-444220936),
[4](https://github.com/has2k1/plotnine/issues/46#issuecomment-718723840),
[5](https://github.com/has2k1/plotnine/issues/457#issuecomment-727200970),
[6](https://github.com/has2k1/plotnine/issues/46#issuecomment-1002209781)).



We also provide tools to solve:
1. [issue 374: figure size incorrect](https://github.com/has2k1/plotnine/issues/374).
We actually have the solution for this problem...
([Kavi Gupta blogpost](https://kavigupta.org/2019/05/18/Setting-the-size-of-figures-in-matplotlib/))

We are technically "racing" against `kas2k1` (the developer of `plotnine`) who
is looking at to figure out a way to solve this problem (but often runs into
structure issues and `matplotlib`'s "unwillingness"/"inability" to solve the
problems he's facing - which is w.r.t. how he processes the plot building with
legends and away from `fig.tight_layout`.)
1. [issue 390: utilize `tight_layout`](https://github.com/has2k1/plotnine/issues/390).


## Additional numerical information

### Examining potential demand

One can examine downloads of similar packages as the one proposed in `R`
and the amount of downloads of `R`'s `ggplot2` versus the number of downloads
of `python`'s `plotnine` to extroplate potential demand.

#### R downloads

Below we present the number of downloads of `ggplot2`, `gridExtra`, `cowplot`
and `patchwork` from CRAN. The numbers of downloads have been rounded are with
respect to 12/18/2021 (and days prior to that)[^1].

[^1]: This was done using the using `R` package `cranlogs` (which counts the
  number of CRAN-downloads).

<!--
### R code

```r
library(cranlogs)
library(tidyverse)
library(lubridate)
package_names <- c("ggplot2", "gridExtra","patchwork", "cowplot")

end_date <- as.Date("2021-12-18", format = c("%Y-%m-%d"))
month_cut <-  as.Date("2021-11-18", format = c("%Y-%m-%d"))

cran_download_info <- cranlogs::cran_downloads(packages = package_names,
                         from =  end_date-365,
                         to = end_date)

year_downloads <- cran_download_info %>% group_by(package) %>%
  summarize(year = sum(count))

last_month <- cran_download_info %>%
  filter(date >= month_cut) %>%
  group_by(package) %>%
  summarize(month = sum(count))

left_join(year_downloads, last_month, by = "package") %>%
  mutate(across(.cols = c(year,month), .fns =  ~round(.x,-4))) %>%
  mutate(across(.cols = c(year,month),
                .fns = ~prettyNum(.x,big.mark=",",scientific=FALSE))) %>%
  knitr::kable(align = "lrr")
```
-->

|package   |     month|
|:---------|---------:|
|ggplot2   | 2,920,000|
|gridExtra |   400,000|
|cowplot   |   310,000|
|patchwork |   110,000|


|package                              |     month|
|:------------------------------------|---------:|
|ggplot2                              | 2,920,000|
|sum of gridExtra, cowplot, patchwork |   820,000|

#### Python downloads

We then examine the number of downloads of `python`'s `plotnine` package (just
using `pip`, not `conda`). These values are calculated with respect to 11/2021
(and days prior to that)[^2].

|package    |source|      month |
|:----------|:-----|-----------:|
| plotnine  | PyPi |    170,000 |
| seaborn   | PyPi |  5,000,000 |
| matplotlib| PyPi | 26,000,000 |


[^2]: This was done using the using the websites
https://pypistats.org/packages/plotnine,
https://pypistats.org/packages/matplotlib,
https://pypistats.org/packages/seaborn.


## Proposed Solution (old comments - pre 1/20)

The solution I have in mind has a few structures.

1. provide functionality that reflexs capabilities of `gridExtra`, `cowplot`
and `patchwork`
    a. I have mapped out some of this functionality and highlighted overlaps -
    but I imagine we definitely discuss this and how it might best be
    implemented
2. Use png (now probably svg?) representations of each plot image as a base and
then "sew" them together into a quilt


### Functional needs (old comments - pre 1/20)

1. matrix structure formating, e.g.
```
np.array([[0,0,1,2],
          [0,0,1,1]])
```
2. nested (e.g. so plot 0 could actual be a non square set of plots)
3. correctly or approximately correctly scale texts and figure sizes to be
consistance (e.g. so plot 2 and plot 0 have themes that describe things in a
similar way)



