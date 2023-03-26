from bagpy import bagreader
import pandas as pd
import seaborn as sea
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares
import scipy.integrate as integrate
from scipy.signal import butter, filtfilt
import math

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
gpsDF = pd.read_csv('data_driving/gnss.csv')


#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#Hard Iron Calibration
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

x_offset = (circlesDF.max(axis=0)['mag_field.magnetic_field.x']
            + circlesDF.min(axis=0)['mag_field.magnetic_field.x'])/2

y_offset = (circlesDF.max(axis=0)['mag_field.magnetic_field.y']
            + circlesDF.min(axis=0)['mag_field.magnetic_field.y'])/2

def scale(dataframe):
    row = dataframe[0:1]
    time_scale = row.iloc[0]['Time']

    dataframe['Time'] -= time_scale

    return(dataframe)

def hard_iron_calibration(dataframe):
    dataframe['mag_field.magnetic_field.x'] -= x_offset
    dataframe['mag_field.magnetic_field.y'] -= y_offset
    return(dataframe)

# ax1 = circlesDF.plot(x = 'mag_field.magnetic_field.x', y = 'mag_field.magnetic_field.y',
#                c = 'green', xlabel='Magnetic Field X [gauss]', ylabel='Magnetic Field Y [gauss]',
#                kind = 'scatter')

circles_calibrated_hard = hard_iron_calibration(circlesDF)
# circles_calibrated_hard.plot(ax = ax1, x = 'mag_field.magnetic_field.x', y = 'mag_field.magnetic_field.y',
#                c = 'blue', xlabel='Magnetic Field X [gauss]', ylabel='Magnetic Field Y [gauss]',
#                kind = 'scatter')
# ax1.legend(['Raw MagField', 'Hard Iron Calibrated MagField'])
# ax1.set_title('Magnetometor X vs Y Hard Iron Calibration')
# ax1.axis('equal')

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#Soft Iron Calibration
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
x = circles_calibrated_hard['mag_field.magnetic_field.x'].values
y = circles_calibrated_hard['mag_field.magnetic_field.y'].values
circles_calibrated_hard['r'] = np.sqrt(circles_calibrated_hard['mag_field.magnetic_field.x']**2
                                +circles_calibrated_hard['mag_field.magnetic_field.y']**2)
avg_delta_x = (max(x) - min(x)) / 2
avg_delta_y = (max(y) - min(y)) / 2
avg_delta = (avg_delta_x + avg_delta_y) / 2
scale_x = avg_delta / avg_delta_x
scale_y = avg_delta / avg_delta_y

corrected_x = x * scale_x
corrected_y = y * scale_y

print(avg_delta_x)
print(avg_delta_y)

#This function describes my mapping from measured data back to a circle
def distortion_model(X_meas, dist_params):
    x = dist_params[0] * (X_meas[0] - dist_params[4]) + dist_params[1]*(X_meas[1] - dist_params[5])
    y = dist_params[2] * (X_meas[0] - dist_params[4]) + dist_params[3]*(X_meas[1] - dist_params[5])
    X = np.array([x,y])
    return X

#Completely made up data set for magnetometer readings
field_strength = .206
angle = np.linspace(-np.pi, np.pi, len(x))
x_mag = field_strength * np.cos(angle) 
y_mag = field_strength * np.sin(angle) 
X_mag = np.array([x_mag, y_mag])
print(len(x_mag))

#This function finds the difference between a circle and my transformed measurement
# def residual(p, X_mag, X_meas):
#     return (X_mag - distortion_model(X_meas, p)).flatten()

X_meas = np.array([x , y])

# Define the equation for a circle
def circle_equation(x, y, a, b, r):
    return (x - a)**2 + (y - b)**2 - r**2

# Define a function to optimize
def optimize_circle(p, x, y):
    a, b, r = p
    return circle_equation(x, y, a, b, r)

# Initial guess for the parameters
p0 = [np.mean(x), np.mean(y), 1.0]

# Fit the circle using least squares optimization
res = least_squares(optimize_circle, p0, args=(corrected_x, corrected_y))

# Extract the optimized parameters
a, b, r = res.x

theta = np.linspace(0, 2*np.pi, 100)
circx = a + r*np.cos(theta)
circy = b + r*np.sin(theta)
# fig, ax2 = plt.subplots()
# ax2.scatter(X_meas[0],X_meas[1])
# ax2.scatter(corrected_x,corrected_y)
# ax2.legend(['Soft Iron Calibrated MagField', 'MagField Post Hard Iron Calibration'])

# ax2.plot(circx, circy, color='black')
# ax2.set_xlabel('Magnetic Field X [gauss]')
# ax2.set_ylabel('Magnetic Field Y [gauss]')
# ax2.set_title('Magnetometor X vs Y Soft Iron Calibration')
# ax2.axis('equal')

# ax1.legend(['Uncalibrated','Calibrated'])
# ax1.axis('equal')
# plt.title('Magnetic Field X vs Y')

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Calibrate Driving Data
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
scale(drivingDF)
time = (drivingDF['Time'].values)
driving_raw_data = drivingDF['VNYMR'].values
driving_mag_x_uncalibrated = drivingDF['mag_field.magnetic_field.x'].values
driving_mag_y_uncalibrated = drivingDF['mag_field.magnetic_field.y'].values
gyro_z = drivingDF['imu.angular_velocity.z'].values

driving_yaw = []
uncalibrated_magnetometer_yaw = np.degrees(np.arctan2(driving_mag_x_uncalibrated,driving_mag_y_uncalibrated))

for data in driving_raw_data:
    split = data.split(",")
    driving_yaw.append(float(split[1]))

driving_x_calibrated = (driving_mag_x_uncalibrated - x_offset) * scale_x
driving_y_calibrated = (driving_mag_y_uncalibrated - y_offset) * scale_y

integrated_yaw = np.degrees(integrate.cumulative_trapezoid(gyro_z, time, initial = 0))
corrected_yaw = np.mod(integrated_yaw + 180, 360) - 180

calibrated_magnetometer_yaw = np.degrees(np.arctan2(driving_x_calibrated,driving_y_calibrated))
cal_magnetometer_yaw = calibrated_magnetometer_yaw - calibrated_magnetometer_yaw[0]
cal_magnetometer_yaw = np.mod(calibrated_magnetometer_yaw + 180, 360) - 180

calibrated_magnetometer_yaw = calibrated_magnetometer_yaw - calibrated_magnetometer_yaw[0]
uncal_magnetometer_yaw = uncalibrated_magnetometer_yaw - uncalibrated_magnetometer_yaw[0]
uncal_magnetometer_yaw = np.mod(uncalibrated_magnetometer_yaw + 180, 360) - 180


# fid, ax3 = plt.subplots()
# ax3.plot(time, cal_magnetometer_yaw)
# ax3.plot(time, uncal_magnetometer_yaw)
# ax3.plot(time, corrected_yaw)
# ax3.legend(['Calibrated Mag Yaw Estimate','Uncalibrated Mag Yaw Estimate', 'Gyro Integrated Yaw Estimate'])
# ax3.set_xlabel('Time [sec]')
# ax3.set_ylabel('Yaw [degrees]')
# ax3.set_title('Yaw Estimation')

# Design the Butterworth low-pass filter
fs = 40
cutoff_frequency = .1  # Cutoff frequency for the low-pass filter
order = 4  # Order of the Butterworth filter
nyquist_frequency = 0.5 * fs
normalized_cutoff_frequency = cutoff_frequency / nyquist_frequency
b, a = butter(order, normalized_cutoff_frequency, btype='low')

# Design the Butterworth high-pass filter
cutoff_frequency = .000001  # Cutoff frequency for the high-pass filter
order = 1  # Order of the Butterworth filter
nyquist_frequency = 0.5 * fs
normalized_cutoff_frequency = cutoff_frequency / nyquist_frequency
c, k = butter(order, normalized_cutoff_frequency, btype='high')

# Apply the filter to the signal with DC offset
hpf = filtfilt(c, k, corrected_yaw)
hpf = hpf - hpf[0]

# Apply the filter to the noisy signal
lpf_mag = filtfilt(b, a, cal_magnetometer_yaw)
comp_filter = hpf + lpf_mag

ax9 = plt.subplot()
ax9.plot(time, lpf_mag)
ax9.plot(time, hpf)
ax9.plot(time, comp_filter)
ax9.legend(['Low Pass Filter on Mag Yaw', 'High Pass Filter on Gyro Yaw', 'Complimentary Filter'])
ax9.set_title('Low Pass, High Pass and Complimentary Filters')
ax9.set_xlabel('Time [sec]')
ax9.set_ylabel('Yaw [degrees]')

# ax10 = plt.subplot()
# ax10.plot(time, comp_filter)
# ax10.plot(time, uncalibrated_magnetometer_yaw)
# ax10.plot(time, corrected_yaw)
# ax10.plot(time, driving_yaw)
# ax10.legend(['Complimentary Filter', 'Magnetometer Yaw', 'Integrated Gyro Yaw', 'IMU Yaw'])
# ax10.set_title('Magnetometer, Integrated Gyro, Complementary filter and IMU Yaw Angles')
# ax10.set_xlabel('Time [sec]')
# ax10.set_ylabel('Yaw [degrees]')

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Estimate the forward velocity
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------
scale(gpsDF)

forward_acc = drivingDF['imu.linear_acceleration.x'].values
acc_correction = np.median(forward_acc)
print(acc_correction)
corrected_acc = forward_acc - acc_correction

forward_vel = integrate.cumulative_trapezoid(forward_acc, time, initial = 0)
corrected_forward_vel = integrate.cumulative_trapezoid(corrected_acc, time, initial = 0)
gps_easting = gpsDF['UTM_easting'].values
gps_northing = gpsDF['UTM_northing'].values
gps_time = gpsDF['Time'].values
distance = np.sqrt(gps_easting**2 + gps_northing**2)

delta_position = abs(np.diff(distance))
delta_time = np.diff(gps_time)
gps_velocity = delta_position / delta_time

# gps_time = gps_time[1:]

# Fit a linear regression model to the data
coefficients = np.polyfit(time, forward_vel, deg=1)
trend_line = np.poly1d(coefficients)
print(coefficients)

# Calculate the trend for each data point
trend_data = trend_line(time)

# Detrend the data by subtracting the trend from the original data
detrended_data = forward_vel - trend_data

# fig, ax4 = plt.subplots()
# fig, ax5 = plt.subplots()
# ax4.plot(time, forward_vel, c = 'green')
# ax4.set_title('Unadjusted Accelerometer Velociy Estimate')
# ax5.plot(time, corrected_forward_vel)
# ax5.set_title('Adjusted Accelerometer Velociy Estimate')

# fig, ax6 = plt.subplots()
# ax6.plot(gps_time, gps_velocity)
# ax6.set_title('GPS Velociy Estimate')

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Dead Reckoning Estimation
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
distance_from_integration = integrate.cumulative_trapezoid(detrended_data, time, initial = 0)
distance = distance - distance[0]
# fig, ax6 = plt.subplots()
# ax6.plot(gps_time, distance)
# ax6.plot(time, distance_from_integration)
# ax6.set_title('Distance Estimate')

plt.show()