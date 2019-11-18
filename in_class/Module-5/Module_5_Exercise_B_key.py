# -*- coding: utf-8 -*-
"""
GIS 5103
Module 5 Exercise B Key
Author: Brad Johnson
"""
# %% Imported libraries

import geopandas as gpd
import shapely
import matplotlib.pyplot as plt
from shapely.ops import unary_union
from pylab import rcParams

rcParams['figure.figsize'] = 10,10

# %% Defining base GeoDataFrame

# Importing PHX restaurants, adding geometry to GeoPandas dataframe, and projecting
rest = gpd.read_file("/home/brad/OneDrive/GIS 5103/Module 5/restaurants.csv")
rest['xy'] = list(zip(rest.longitude.astype(float), rest.latitude.astype(float)))
rest['geometry'] = rest['xy'].apply(shapely.geometry.Point)
rest.plot(alpha=0.2, markersize=2)
rest.crs = {'init': 'epsg:4326'}
rest_proj = rest.copy()
rest_proj.to_crs(epsg=2223, inplace=True)

# %% Defining secondary GeoDataFrame

# Importing and projecting lightrail stations
phx_lr = gpd.read_file("/home/brad/OneDrive/GIS 5103/Module 5/phx_lightrail_stations/XYstations_ordered.shp")
phx_lr.crs = {'init': 'epsg:2223'}
lr_proj = phx_lr.copy()
lr_proj.to_crs(epsg=2223, inplace=True)

# %%
# Plotting lightrail stations and downtown restaurants
ax = rest_proj.plot(color='blue', alpha=0.2, markersize=2)
lr_proj.plot(ax=ax, color='red', alpha=0.5, markersize=50)
ax.set(xlim=(600000,750000), ylim=(850000,950000))
plt.show()

# %% Determining accessible restaurants

# Create station buffers and intersecting restaurants located inside buffers
lr_buff = lr_proj.buffer(2640)  ## 2640 feet (per the projection) is one-half mile
restnearlr = rest_proj.loc[rest_proj.intersects(unary_union(lr_buff)),:]

#Plotting intersecting restaurants and 0.5 mile buffer around lightrail stations 
ax = restnearlr.plot(color='blue', alpha=0.2, markersize=2)
lr_proj.buffer(2640).plot(ax=ax, color='red', alpha=0.4)
ax.set(xlim=(600000,750000), ylim=(850000,950000))
plt.show()

# %%
# Plot all downtown restaurants, lightrail buffers, and restaurants located inside buffers
ax = restnearlr.plot(color='blue', alpha=0.9, markersize=5)
rest_proj.plot(ax=ax, color='grey', alpha=0.2, markersize=2)
lr_proj.buffer(2640).plot(ax=ax, color='red', alpha=0.4)
ax.set(xlim=(600000,750000), ylim=(850000,950000))
plt.show()

#%% Analyzing the data

# Additional stats
restnearlr.shape[0] # Total number of restaurants w/in 0.5 miles of lightrail stations
round(restnearlr.shape[0]/rest_proj.shape[0]*100, 2) # Percent of all restaurants near stations
round(restnearlr.shape[0]/lr_proj.shape[0], 2) # Average number of nearby restaurants per station
restnearlr.name[restnearlr.open == 'True'][restnearlr.stars >= 4.5] # Open nearby restaurants rated >= 4.5 stars

# %% A statistical thought problem
""" Is the average number of restaurants per station abnormally high for the Phoenix area?

    Randomly pick a point in the metro area
    Draw a half mile buffer around the point
    Count the number of points in the buffer
    Repeat the above steps 1000 times (keeping track of the value each time)
    Conduct a two-tailed test at the 95% confidence level
    Find the cutoff point (it's at the 97.5 percentile)
    If the average number of restaurants near the stations is larger than the cutoff, 
    then it is statistically significant
"""

import numpy as np
from shapely.geometry import Point
from scipy.stats import ttest_ind

xmin, xmax, ymin, ymax = 600000, 750000, 850000, 950000 ## Establish x,y limits
xran = (xmax - xmin) * np.random.random(1000) + xmin
yran = (ymax - ymin) * np.random.random(1000) + ymin
pts = gpd.GeoSeries([Point(x, y) for x, y in zip(xran, yran)])
buffrest = np.array([[]])
randrest = np.array([[]])

for i in range(len(lr_buff)):
    ind_buff = rest_proj.loc[rest_proj.intersects(lr_buff[i]),:].shape[0]
    buffrest = np.append(buffrest, ind_buff)
    
for i in range(len(pts)):
    rand_buff = rest_proj.loc[rest_proj.intersects(pts[i].buffer(2640)),:].shape[0]
    randrest = np.append(randrest, rand_buff)    

# List comprehension alternative
#randrest = [rest_proj.loc[rest_proj.intersects(unary_union(pts[i].buffer(2640))),:].shape[0] for i in range(len(pts))]
#%% Points to note

''' Depending on the method you choose to calculate the average number of nearby
    restaurants will change the result of the following two-sided T test. If 
    you use the consolidated unary_union to determine the total number of 
    restaurants, the null hypothesis is accepted. If you evaluate by `buffrest`
    above, it will be rejected because some restaurants are double-counted due 
    to their proximity to multiple rail stations.
'''

# Compares merged polygon count average to randomized 97.5% percentile proximity count
restnearlr.shape[0]/lr_proj.shape[0] > np.percentile(randrest, 97.5)

# Compares individual station buffer counts to randomized 97.5% percentile
# proximity counts
ttest_ind(buffrest, randrest)
buffrest.mean() > np.percentile(randrest, 97.5)