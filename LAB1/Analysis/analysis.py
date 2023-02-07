#!/usr/bin/env python3

import bagpy
from bagpy import bagreader
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

stationary_open_area = bagreader('stationary_open_area.bag')
occluded_area = bagreader('occluded_area.bag')
walking = bagreader('walking.bag')


#print(stationary_open_area.topic_table)

def scale(data):
    get_scale = data[:1] # Get first value
    get_northing_scale = get_scale.iloc[0]['UTM_northing']
    get_easting_scale = get_scale.iloc[0]['UTM_easting']

    # print(get_easting_scale)
    data["UTM_northing"] -= get_northing_scale
    data["UTM_easting"] -= get_easting_scale
    # print(data)
    return data

csvfiles = []
for t in stationary_open_area.topics:
    data = stationary_open_area.message_by_topic(t)
    csvfiles.append(data)

for t in occluded_area.topics:
    data = occluded_area.message_by_topic(t)
    csvfiles.append(data)

for t in walking.topics:
    data = walking.message_by_topic(t)
    csvfiles.append(data)

stationary_open_area_csv = pd.read_csv('stationary_open_area/gps.csv')
occluded_area_csv = pd.read_csv('occluded_area/gps.csv')
walking_csv = pd.read_csv('walking/gps.csv')

'''fig, ax = bagpy.create_fig(1)
ax[0].scatter(x = 'Easting', y = 'Northing', data = stationary_open_area_csv,
s = 1, label = 'Haahaa')

for axis in ax:
    axis.legend()
    axis.set_xlabel('Easting')'''

scale(stationary_open_area_csv)
scale(occluded_area_csv)
scale(walking_csv)

stationary_open_area_csv.plot(kind='scatter', x='UTM_easting', y='UTM_northing', title='Open Area Stationary Northing vs Easting', s = 1)
occluded_area_csv.plot(kind='scatter', x='UTM_easting', y='UTM_northing', title='Occluded Area Northing vs Easting', s = 1)
walking_csv.plot(kind='scatter', x='UTM_easting', y='UTM_northing', title='Walking Northing vs Easting', s = 1)

stationary_open_area_csv.plot(kind='scatter', x='Time', y='Altitude', title='Open Area Altitude vs Time', s = 1)
occluded_area_csv.plot(kind='scatter', x='Time', y='Altitude', title='Occluded Area Stationary Altitude vs Time', s = 1)
walking_csv.plot(kind='scatter', x='Time', y='Altitude', title='Walking Altitude vs Time', s = 1)

plt.show()