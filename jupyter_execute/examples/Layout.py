#!/usr/bin/env python
# coding: utf-8

# # Layouts

# In[1]:


import numpy as np
import cowpatch as cow

import plotnine as p9
import plotnine.data as p9_data


# In[2]:


mtcars = p9_data.mpg

g0 = p9.ggplot(p9_data.mpg) +    p9.geom_bar(p9.aes(x="hwy")) +    p9.labs(title = 'Plot 0')

g1 = p9.ggplot(p9_data.mpg) +    p9.geom_point(p9.aes(x="hwy", y = "displ")) +    p9.labs(title = 'Plot 1')

g2 = p9.ggplot(p9_data.mpg) +    p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +    p9.labs(title = 'Plot 2')

g3 = p9.ggplot(p9_data.mpg[p9_data.mpg["class"].isin(["compact",
                                                     "suv",
                                                     "pickup"])]) +\
    p9.geom_histogram(p9.aes(x="hwy"),bins=10) +\
    p9.facet_wrap("class")


# In[3]:


patch_obj = cow.patch(g0,g1,g2)
layout_obj = cow.layout(design = np.array([[0,0,0,1,1,1],
                                           [0,0,0,2,2,2],
                                           [0,0,0,2,2,2]]))


# In[4]:


vis = patch_obj + layout_obj
vis.show(width = 15, height = 9)

