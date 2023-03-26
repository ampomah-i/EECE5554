import numpy as np
import matplotlib.pyplot as plt

from bagpy import bagreader
import pandas as pd
import seaborn as sea
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy.optimize import least_squares
import math
import csv
from fitter import Fitter, get_common_distributions, get_distributions

# data_drivingB = bagreader('data_driving.bag')
# data_going_in_circleB = bagreader('data_going_in_circles.bag')                        

# csvfiles = []


# for t in data_drivingB.topics:
#     data1 = data_drivingB.message_by_topic(t)
#     csvfiles.append(data1)

# for t in data_going_in_circleB.topics:
#     data2 = data_going_in_circleB.message_by_topic(t)
#     csvfiles.append(data2)

drivingDF = pd.read_csv('data_driving/imu.csv')
circlesDF = pd.read_csv('data_going_in_circles/imu.csv')

ax = circlesDF.plot(x = 'mag_field.magnetic_field.x', y = 'mag_field.magnetic_field.y',
               c = 'green', xlabel='Magnetic Field X [gauss]', ylabel='Magnetic Field Y [gauss]',
               kind = 'scatter')

x_offset = (circlesDF.max(axis=0)['mag_field.magnetic_field.x']
            + circlesDF.min(axis=0)['mag_field.magnetic_field.x'])/2

y_offset = (circlesDF.max(axis=0)['mag_field.magnetic_field.y']
            + circlesDF.min(axis=0)['mag_field.magnetic_field.y'])/2

def hard_iron_calibration(dataframe):
    dataframe['mag_field.magnetic_field.x'] -= x_offset
    dataframe['mag_field.magnetic_field.y'] -= y_offset
    return(dataframe)

circles_calibrated = hard_iron_calibration(circlesDF)
circles_calibrated['r'] = np.sqrt(circles_calibrated['mag_field.magnetic_field.x']**2
                        + circles_calibrated['mag_field.magnetic_field.y']**2)

rMax = circles_calibrated.max(axis=0)['r']
rMin = circles_calibrated.min(axis=0)['r']

print(circles_calibrated)
print(rMax)
print(rMin)

circles_calibrated.plot(ax = ax, x = 'mag_field.magnetic_field.x', y = 'mag_field.magnetic_field.y',
               c = 'blue', xlabel='Magnetic Field X [gauss]', ylabel='Magnetic Field Y [gauss]',
               kind = 'scatter')

x = circles_calibrated['mag_field.magnetic_field.x'].values
y = circles_calibrated['mag_field.magnetic_field.y'].values

# Calculate the centroid of the ellipse
centroid = np.array([np.mean(x), np.mean(y)])

# Calculate the semi-major and semi-minor axes of the ellipse
covariance = np.cov(x, y)
eigenvalues, eigenvectors = np.linalg.eig(covariance)
semi_major_axis = np.sqrt(eigenvalues[0])
semi_minor_axis = np.sqrt(eigenvalues[1])

# Scale the x and y coordinates to transform the ellipse to a circle
x_scaled = (x - centroid[0]) * semi_minor_axis / semi_major_axis + centroid[0]
y_scaled = (y - centroid[1]) * semi_major_axis / semi_minor_axis + centroid[1]

# Plot the original ellipse and the transformed circle
fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(8, 4))
ax1.plot(x, y)
ax1.axis('equal')
ax1.set_title('Original Ellipse')
ax2.plot(x_scaled, y_scaled)
ax2.axis('equal')
ax2.set_title('Transformed Circle')
plt.show()