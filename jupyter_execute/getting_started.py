#!/usr/bin/env python
# coding: utf-8

# # Getting Started
# 
# TODO: update this into a getting started document
# 
# To use `cowpatch` in a project:

# In[1]:


import cowpatch as cow


# In[2]:


import plotnine as p9
import plotnine.data as p9_data
import numpy as np


# In[3]:


# creation of some some ggplot objects
g0 = p9.ggplot(p9_data.mpg) +    p9.geom_bar(p9.aes(x="hwy")) +    p9.labs(title = 'Plot 0')

g1 = p9.ggplot(p9_data.mpg) +    p9.geom_point(p9.aes(x="hwy", y = "displ")) +    p9.labs(title = 'Plot 1')

g2 = p9.ggplot(p9_data.mpg) +    p9.geom_point(p9.aes(x="hwy", y = "displ", color="class")) +    p9.labs(title = 'Plot 2')


# In[4]:


vis_patch = cow.patch(g0,g1,g2)
vis_patch += cow.layout(design = np.array([[0,0,0,1,1,1], 
                                            [0,0,0,2,2,2],
                                            [0,0,0,2,2,2]]))


# In[5]:


vis_patch.show(width = 11, height = 7)


# ## grammar combination

# In[6]:


g0p = cow.patch(g0)
g1p = cow.patch(g1)
g2p = cow.patch(g2)


# In[7]:


g01 = g0p + g1p
g02 = g0p + g2p
g012 = g0p + g1p + g2p
g012_2 = g01 + g2p


# In[8]:


g01.show(width = 11, height = 7)

