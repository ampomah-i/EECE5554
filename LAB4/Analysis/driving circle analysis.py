from bagpy import bagreader
import pandas as pd
import seaborn as sea
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares
import scipy.integrate as integrate
from scipy.signal import butter, filtfilt
from scipy.spatial.transform import Rotation as R
from scipy.ndimage import rotate
from scipy.interpolate import interp1d

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

radii = circles_calibrated_hard['r'].values

theTaa = np.arcsin(max(y)/max(radii))
Rotation = np.array([[np.cos(theTaa), np.sin(theTaa)], 
              [-np.sin(theTaa), np.cos(theTaa)]])
xymatrix = np.column_stack((x,y))

v1 = np.dot(Rotation, xymatrix.T)

avg_delta_x = (max(x) - min(x)) / 2
avg_delta_y = (max(y) - min(y)) / 2
avg_delta = (avg_delta_x + avg_delta_y) / 2
scale_x = avg_delta / avg_delta_x
scale_y = avg_delta / avg_delta_y

corrected_x = v1[0] * scale_x
corrected_y = v1[1] * scale_y

print(avg_delta_x)
print(avg_delta_y)

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

uncalibrated_magnetometer_yaw = np.degrees(np.arctan2(-driving_mag_y_uncalibrated,driving_mag_x_uncalibrated))

driving_yaw = []

for data in driving_raw_data:
    split = data.split(",")
    driving_yaw.append(float(split[1]))

driving_matrix = np.column_stack(((driving_mag_x_uncalibrated - x_offset/2), (driving_mag_y_uncalibrated - y_offset/2)))
driving_rotated = np.dot(Rotation, driving_matrix.T)

driving_x_calibrated = driving_rotated[0] * scale_x
driving_y_calibrated = driving_rotated[1] * scale_y


integrated_yaw = np.degrees(integrate.cumulative_trapezoid(gyro_z, time, initial = 0))
corrected_yaw = np.mod(integrated_yaw + 180, 360) - 180
calibrated_magnetometer_yaw = np.degrees(np.arctan2(-driving_y_calibrated,driving_x_calibrated))
calibrated_magnetometer_yaw = calibrated_magnetometer_yaw - calibrated_magnetometer_yaw[0]

# fid, ax3 = plt.subplots()
# ax3.plot(time, calibrated_magnetometer_yaw)
# ax3.plot(time, uncalibrated_magnetometer_yaw)
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
lpf_mag = filtfilt(b, a, calibrated_magnetometer_yaw)
lpf_mag = lpf_mag - lpf_mag[0]
comp_filter = hpf + lpf_mag

# ax9 = plt.subplot()
# ax9.plot(time, lpf_mag)
# ax9.plot(time, hpf)
# ax9.plot(time, comp_filter)
# ax9.legend(['Low Pass Filter on Mag Yaw', 'High Pass Filter on Gyro Yaw', 'Complimentary Filter'])
# ax9.set_title('Low Pass, High Pass and Complimentary Filters')
# ax9.set_xlabel('Time [sec]')
# ax9.set_ylabel('Yaw [degrees]')
driving_yaw = np.array(driving_yaw) + 32

ax10 = plt.subplot()
ax10.plot(time, comp_filter)
ax10.plot(time, calibrated_magnetometer_yaw)
ax10.plot(time, corrected_yaw)
ax10.plot(time, driving_yaw)
ax10.legend(['Complimentary Filter', 'Magnetometer Yaw', 'Integrated Gyro Yaw', 'IMU Yaw'])
ax10.set_title('Magnetometer, Integrated Gyro, Complementary filter and IMU Yaw Angles')
ax10.set_xlabel('Time [sec]')
ax10.set_ylabel('Yaw [degrees]')

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
corrected_acc = forward_acc - acc_correction

# Define the filter parameters
order = 2
cutoff = .1  # Hz
fs = 1 / np.mean(np.diff(time))

# Create the filter coefficients
nyquist = 0.5 * fs
normal_cutoff = cutoff / nyquist
b, a = butter(order, normal_cutoff, btype='low', analog=False)

# Apply the filter to the data
filtered_data = filtfilt(b, a, forward_acc)
filtered_data = filtered_data - np.mean(filtered_data)
# Apply the moving average filter

filtered_vel = integrate.cumulative_trapezoid(filtered_data, time, initial = 0)

forward_vel = integrate.cumulative_trapezoid(forward_acc, time, initial = 0)
corrected_forward_vel = integrate.cumulative_trapezoid(corrected_acc, time, initial = 0)
gps_easting = gpsDF['UTM_easting'].values
gps_easting = gps_easting - gps_easting[0]
gps_northing = gpsDF['UTM_northing'].values
gps_northing = gps_northing - gps_northing[0]

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

# Apply a moving average filter
window_size = 100
window = np.ones(window_size) / window_size
filtered_acceleration = np.convolve(corrected_acc, window, mode='same')
filtered_forward_vel = integrate.cumulative_trapezoid(filtered_acceleration, time, initial = 0)

# fig, ax = plt.subplots()
# ax.plot(time, filtered_data)
# ax.plot(time, filtered_vel)

# fig, ax4 = plt.subplots()
# fig, ax5 = plt.subplots()
# ax4.plot(time, filtered_acceleration)
# ax4.set_title('Unadjusted Accelerometer Velociy Estimate')
# ax4.set_xlabel('Time [sec]')
# ax4.set_ylabel('Velocity [meters/sec]')

zer_adjusted_forward_vel = np.copy(filtered_forward_vel)
test_split1 = np.copy(filtered_forward_vel)
# Find the zero crossings of the velocity data
zero_crossings = np.where(np.diff(np.sign(zer_adjusted_forward_vel)))[0]

# Split the data in half
half = len(test_split1) // 2
data1, data2 = np.split(test_split1, [half])
print(min(data1))
print(np.where(data1 == min(data1)))

detrend_start = zero_crossings[6]

start1 = zero_crossings[1]
end1 = 14779
test_split1[start1:end1+1] = 0
test_split1[end1+2:] += 14.2

ZAF = np.copy(test_split1)
# Correct for negative velocity values
for i in range(1, len(ZAF)):
    if ZAF[i] < 0:
        ZAF[i] = max(ZAF[i], ZAF[i-1])

print(len(ZAF))
print((len(ZAF)*(3/4)))
ZAF[26045:] -= 5.5

for i in range(1, len(ZAF)):
    if ZAF[i] < 0:
        ZAF[i] = max(ZAF[i], ZAF[i-1])

ZAF = ZAF *.75
ZAF_ = ZAF[:start1]*.85
ZAF[:start1] = ZAF_
ZAF = ZAF*1.2

# gps_time = gps_time[1:]
# fig, ax6 = plt.subplots()
# ax6.plot(gps_time, gps_velocity)
# ax6.set_xlabel('Time [sec]')
# ax6.set_ylabel('Velocity [meters/sec]')
# # ax6.plot(time, filtered_forward_vel)
# ax6.plot(time, ZAF)
# ax6.plot(time, corrected_forward_vel)
# # ax6.plot(time, zer_adjusted_forward_vel)
# ax6.set_title('Velocity Estimate')
# ax6.legend(['GPS Velocity Estimate','Adjusted Inertial Velocity Estimate',
#             'Unadjusted Velocity Estimate'])

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Dead Reckoning Estimation
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
y_acc = drivingDF['imu.linear_acceleration.y'].values
y_acc_correction = np.median(y_acc)
corrected_y_acc = forward_acc - acc_correction
calculated_Ydot = gyro_z*corrected_forward_vel

# Define the filter parameters
order = 2
cutoff = 1  # Hz
fs = 1 / np.mean(np.diff(time))

# Create the filter coefficients
nyquist = 0.5 * fs
normal_cutoff = cutoff / nyquist
b, a = butter(order, normal_cutoff, btype='low', analog=False)

# Apply the filter to the data
filtered_y = filtfilt(b, a, y_acc)
filtered_y = filtered_y - np.mean(filtered_y)
# Apply the moving average filter

filtered_y_vel = integrate.cumulative_trapezoid(filtered_y, time, initial = 0)
distance_y_from_integration = integrate.cumulative_trapezoid(filtered_y_vel, time, initial = 0)
distance_x_from_integration = integrate.cumulative_trapezoid(filtered_vel, time, initial = 0)
# distance = distance - distance[0]
fig, ax6 = plt.subplots()
ax6.plot(gps_time, distance)
ax6.set_title('Dead Reconing')

print(np.where(time > 300))
calculated_Ydot[12000:] *= -1
#-----------------------------------------------------------------------------------------------
#Detrending forward velocity
#-----------------------------------------------------------------------------------------------
window_size = 1
window = np.ones(window_size) / float(window_size)
smoothed_v = np.convolve(ZAF, window, 'same')

Ve = ZAF*np.cos(np.deg2rad(driving_yaw))
Vn = ZAF*np.sin(np.deg2rad(driving_yaw))

Xe = integrate.cumulative_trapezoid(Ve, time, initial = 0)
Xn = integrate.cumulative_trapezoid(Vn, time, initial = 0)
distance_imu = np.sqrt(Xe**2 + Xn**2)
rate = np.mean(np.diff(Xe))
ratey = np.mean(np.diff(Xn))

Xe += Xe*rate*-1
Xn += Xn*ratey*-1

yay = np.column_stack((Xe,Xn))
arr_diag = np.fliplr(np.rot90(yay))


# fig, ax7 = plt.subplots()
ax6.set_xlim(left = 0)
ax6.plot(time, distance_imu)
# ax7.plot(time, calculated_Ydot, c = 'blue')
# ax6.plot(arr_diag[0], arr_diag[1], c = 'black')
ax6.legend(['GPS Displacement', 'Integrated Displacement'])
ax6.set_title('GPS and Integrated Inertial Displacement')
ax6.set_xlabel('Time [sec]')
ax6.set_ylabel('Displacement [meters]')
ax6.grid(True, linestyle=':', linewidth=0.5, color='gray')

plt.show()

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Dead Reckoning Estimation
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
