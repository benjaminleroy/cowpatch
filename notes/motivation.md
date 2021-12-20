# Package and Package motivation

## Introduction

In `R` now-a-days, `ggplot2` is a very commonly used package (I might even lean
into the idea that it might be more used than the base plot functionality in
`R`). In `python`, there were a few attempts to create Grammar of Graphics style
plots, but it appears as if `plotnine` (around since mid-2017) is the pythonic
equivalent. As will be seen in a later section, `plotnine` is pretty highly used,
and I personally use it and enjoy using it more than `matplotlib` (or `seaborn`).

### Gap

Discussed over text...

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

|package   |       year|     month|
|:---------|----------:|---------:|
|ggplot2   | 25,170,000| 2,920,000|
|gridExtra |  3,900,000|   400,000|
|cowplot   |  3,450,000|   310,000|
|patchwork |    890,000|   110,000|


|package                              |       year|     month|
|:------------------------------------|----------:|---------:|
|ggplot2                              | 25,170,000| 2,920,000|
|sum of gridExtra, cowplot, patchwork |  8,230,000|   820,000|

#### Python downloads

We then examine the number of downloads of `python`'s `plotnine` package (just
using `pip`, not `conda`). These values are calculated with respect to 11/2021
(and days prior to that)[^2].

|package |source|       year|   month|
|:-------|:-----|----------:|-------:|
|plotnine| PyPi | 1,100,000 | 180,000|


[^2]: This was done using the using `python` package `pypistats` and the website
https://pypistats.org/packages/plotnine.


<!--
# pip install pypistats
pypistats overall plotnine -sd 2020-11 -ed 2021-11
-->


<!--
|plotnine| [Conda]()
-->

<!--
### Conda code:

```python
# conda install -c conda-forge condastats
from condastats.cli import overall

overall("plotnine",month="2021-11")
condastats overall plotnine --start_month 2020-11 --end_month 2019-03
```
-->

#### Projection

If we view `R` `ggplot2` users as exchangeable with `python` `plotnine` users,
one could imagine that there exists a potential for around 352,000 annual
downloads and 57,600 monthly downloads (with respect to the month of 11/2021 and
the year before 12/01/2021). This doesn't examine expected growth in demand
(as `plotnine`'s version of `ggplot` is much younger than `ggplot2`) or
accounting for different qualities of packages (or package will probably of a
lower quality, and people may downloads `gridExtra`, `cowplot` and `patchwork`).


## Proposed Solution

The solution I have in mind has a few structures.

1. provide functionality that reflexs capabilities of `gridExtra`, `cowplot`
and `patchwork`
    a. I have mapped out some of this functionality and highlighted overlaps -
    but I imagine we definitely discuss this and how it might best be
    implemented
2. Use png (now probably svg?) representations of each plot image as a base and
then "sew" them together into a quilt


### Functional needs

1. matrix structure formating, e.g.
```
np.array([[0,0,1,2],
          [0,0,1,1]])
```
2. nested (e.g. so plot 0 could actual be a non square set of plots)
3. correctly or approximately correctly scale texts and figure sizes to be
consistance (e.g. so plot 2 and plot 0 have themes that describe things in a
similar way)



