library(cowplot)
library(tidyverse)



p0 = ggplot(mtcars) +
  geom_bar(aes(x=gear)) +
  facet_wrap(~cyl) +
  labs(title = 'Plot 0') + theme(plot.title = element_text(hjust = .5))

p1 = ggplot(mtcars) +
  geom_boxplot(aes(x=gear,y= disp, group = gear)) +
  labs(title = 'Plot 1') + theme(plot.title = element_text(hjust = .5))

p2 = ggplot(mtcars) +
  geom_point(aes(x=hp, y=wt, color = mpg)) +
  labs(title = 'Plot 2') + theme(plot.title = element_text(hjust = .5))

p3 = ggplot(mtcars) +
      geom_point(aes(x = mpg, y=disp)) +
      labs(title = 'Plot 3') + theme(plot.title = element_text(hjust = .5))


setwd("/Users/benjaminleroy/Documents/CMU/research/cowpatch/notes/Rimages")

option0 = plot_grid(plotlist = list(plot_grid(p1,p3,NULL,NULL, nrow = 1),
                                    plot_grid(p0,p2, nrow = 1)), nrow = 2)
cowplot::save_plot(option0, filename = "none_labeled.jpg", base_height = 6, base_width = 10)


option1 = plot_grid(plotlist = list(plot_grid(p1,p3,NULL,NULL, nrow = 1),
                                   plot_grid(p0,p2, nrow = 1)), nrow = 2,labels = "auto")

option1.1 = plot_grid(plotlist = list(plot_grid(p1,p3,NULL,NULL, nrow = 1),
                                    plot_grid(p0,p2, nrow = 1)), nrow = 2,labels = c("a","b"))
cowplot::save_plot(option1, filename = "rows_labeled.jpg", base_height = 6, base_width = 10)

option2 = plot_grid(plotlist = list(plot_grid(p1,p3,NULL,NULL, nrow = 1, labels = c("a", "b", NULL, NULL)),
                                    plot_grid(p0,p2, nrow = 1, labels = c("c", "d"))), nrow = 2)
cowplot::save_plot(option2, filename = "each_labeled.png", base_height = 6, base_width = 10)

option3 = plot_grid(plotlist = list(plot_grid(p1,p3,NULL,NULL, nrow = 1),
                                    plot_grid(p0,p2, nrow = 1)), nrow = 2,labels = c("this is very long label, what will it do, will it overlap things?", 
                                                                                     "this is also a long label, let's see"))
cowplot::save_plot(option3, filename = "long_row_labeled.jpg", base_height = 6, base_width = 10)
