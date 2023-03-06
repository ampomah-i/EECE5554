from bagpy import bagreader
import pandas as pd
import seaborn as sea
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import csv


# LocationA = bagreader('LocationA.bag')
# LocationD = bagreader('LocationD.bag')
# LocationB = bagreader('LocationB.bag')
# LocationC = bagreader('LocationC.bag')

csvfiles = []


# for t in LocationB.topics:
#     data1 = LocationB.message_by_topic(t)
#     csvfiles.append(data1)

# for t in LocationD.topics:
#     data2 = LocationD.message_by_topic(t)
#     csvfiles.append(data2)

# for t in LocationC.topics:
#     data3 = LocationC.message_by_topic(t)
#     csvfiles.append(data3)

# for t in LocationA.topics:
#     data4 = LocationA.message_by_topic(t)
#     csvfiles.append(data4)

LocationB_df = pd.read_csv('LocationB/vectornav.csv')
LocationA_df = pd.read_csv('LocationA/vectornav.csv')
LocationC_df = pd.read_csv('LocationC/vectornav.csv')
LocationD_df = pd.read_csv('LocationD/vectornav.csv')

vectornav_string_list = LocationB_df['data'].values.tolist()
time = LocationB_df['Time'].values.tolist()
print(len(time))
print(len(vectornav_string_list))

bad_data = []
yaw = []
pitch = []
roll = []
magX = []
magY = []
magZ = []
accX = []
accY = []
accZ = []
gyroX = []
gyroY = []
gyroZ = []

j = -1
for data in vectornav_string_list:
    j += 1
    if type(data) == str:
        entry = data.split(',')
        if len(entry) == 13:
            yaw.append(float(entry[1]))
            pitch.append(float(entry[2]))
            roll.append(float(entry[3]))
            magX.append(float(entry[4]))
            magY.append(float(entry[5]))
            magZ.append(float(entry[6]))
            accX.append(float(entry[7]))
            accY.append(float(entry[8]))
            accZ.append(float(entry[9]))
            gyroX.append(float(entry[10]))
            gyroY.append(float(entry[11]))
            if entry[12][0:9] == '+00.00.00':
                gyroZ.append(0)
            else:
                gyroZ.append(float(entry[12][0:9]))
        else:
            time.pop(j)
    else:
        time.pop(j)

#print(bad_data)

first_time_value = time[0]
i = 0

for values in time:
    time[i] = time[i] - first_time_value
    i += 1

df2 = pd.DataFrame({'time(s)':time,
                    'yaw':yaw,
                    'pitch': pitch,
                    'roll': roll,
                    'magX': magX,
                    'magY': magY,
                    'magZ': magZ,
                    'accX': accX,
                    'accY': accY,
                    'accZ': accZ,
                    'gyroX': gyroX,
                    'gyroY': gyroY,
                    'gyroZ': gyroZ})

fs = 40
ts = 1.0/fs
# Allan deviation section
def AllanDeviation(dataArr, fs, maxNumM=100):
    ts = 1.0/fs
    N = len(dataArr)
    Nmax = 2**np.floor(np.log2(N/2))
    M = np.logspace(np.log10(1), np.log10(Nmax), num=maxNumM)
    M = np.ceil(M)  # Round up to integer
    M = np.unique(M)  # Remove duplicates
    taus = M * ts  # Compute 'cluster durations' tau

    # Compute Allan variance
    allanVar = np.zeros(len(M))
    for i, mi in enumerate(M):
        twoMi = int(2 * mi)
        mi = int(mi)
        allanVar[i] = np.sum(
            (dataArr[twoMi:N] - (2.0 * dataArr[mi:N-mi]) + dataArr[0:N-twoMi])**2
        )
    
    allanVar /= (2.0 * taus**2) * (N - (2.0 * M))

    # print('Rate random walk (K):', K)
    # print('Angle random walk (N):', N)
    # print('Bias stability (B):', B)
    return (taus, np.sqrt(allanVar))  # Return deviation (dev = sqrt(var))

gx = gyroX # [deg/s]
gy = gyroY 
gz = gyroZ

# Calculate gyro angles
thetax = np.cumsum(gx) * ts  # [deg]
thetay = np.cumsum(gy) * ts
thetaz = np.cumsum(gz) * ts

# Compute Allan deviations
(taux, adx) = AllanDeviation(thetax, fs, maxNumM=200)
(tauy, ady) = AllanDeviation(thetay, fs, maxNumM=200)
(tauz, adz) = AllanDeviation(thetaz, fs, maxNumM=200)


# --------------------------------------------------------------------------
# Finding ANGLE RANDOM WALK N
# Find the index where the slope of the log-scaled Allan deviation is equal
# to the slope specified
slopen = -0.5
logtau = np.log10(taux)
logadev = np.log10(adx)
dlogadev = np.diff(logadev)/np.diff(logtau)
i = np.argmin(np.abs(dlogadev-slopen))

# Find the y-intercept of the line
b = logadev[i] - slopen*logtau[i]

logN = slopen*np.log(1) + b
N = 10**logN

# Plot data on log-scale
tauN = 1
lineN = N / ((taux)**0.5)
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
# Finding RATE RANDOM WALK K
slopek = 0.5
logtau = np.log10(taux)
logadev = np.log10(adx)
dlogadev = np.diff(logadev)/np.diff(logtau)
i = np.argmin(np.abs(dlogadev-slopek))

# Find the y-intercept of the line
b = logadev[i] - slopek*logtau[i]

logK = slopek*np.log10(3) + b
K = 10**logK

# Plot data on log-scale
tauK = 3
lineK = K * ((taux/3)**0.5)
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
# Finding BIAS INSTABILITY B
slopeb = 0
logtau = np.log10(taux)
logadev = np.log10(adx)
dlogadev = np.diff(logadev)/np.diff(logtau)
i = np.argmin(np.abs(dlogadev-slopeb))

# Find the y-intercept of the line
b = logadev[i] - slopeb*logtau[i]

# Determine the bias instability coefficient from the line
scfb = np.sqrt(2*np.log(2)/np.pi)
logB = b - np.log10(scfb)
B = 10**logB

# Plot data on log-scale
tauB = taux[i]
lineB = B * scfb * np.ones(np.size(taux))

# plt.figure()
# plt.title('GyroX Allan Deviations - Location C')
# plt.plot(taux, adx, label=r'$\sigma$ (rad/sec)')
# plt.plot(taux, lineN, label = r'$\sigma_{N}$ (rad/sec)/$\sqrt{Hz}$', linestyle='dashed')
# plt.plot(tauN, N, 'o', ms=15, mec='green', mfc='none', mew=2)
# plt.annotate('N',xy=(tauN, N), xytext=(tauN+40, N+5),
#    textcoords='offset points',
#    color='black', size='large', arrowprops=dict(
#       arrowstyle='simple,tail_width=0.3,head_width=0.8,head_length=0.8',
#       facecolor='b', shrinkB=10))

# plt.plot(taux, lineK, label = r'$\sigma_{K}$ (rad/sec)/$\sqrt{Hz}$', linestyle='dashed')
# plt.plot(tauK, K, 'o', ms=15, mec='red', mfc='none', mew=2)
# plt.annotate('K',xy=(tauK, K), xytext=(tauK+35, K-35),
#    textcoords='offset points',
#    color='black', size='large', arrowprops=dict(
#       arrowstyle='simple,tail_width=0.3,head_width=0.8,head_length=0.8',
#       facecolor='b', shrinkB=10))

# plt.plot(taux, lineB, label = r'$\sigma_{B}$ (rad/sec)', linestyle='dashed')
# plt.plot(tauB, scfb*B, 'o', ms=15, mec='red', mfc='none', mew=2)
# plt.annotate('0.664B',xy=(tauB, scfb*B), xytext=(1, scfb*B-50),
#    textcoords='offset points',
#    color='black', size='large', arrowprops=dict(
#       arrowstyle='simple,tail_width=0.3,head_width=0.8,head_length=0.8',
#       facecolor='b', shrinkB=10))

#print(f'B = {scfb*B}')

# plt.plot(tauy, ady, label='gy')
# plt.plot(tauz, adz, label='gz')
# plt.xlabel(r'$\tau$ [sec]')
# plt.ylabel(r'$\sigma$ [rad/sec]')
# plt.grid(True, which="both", ls="-", color='0.65')
# plt.legend()
# plt.xscale('log')
# plt.yscale('log')
# plt.show()

print(B)
print(K)
print(N)
# df2.plot(x="time(s)", y=["gyroX", "gyroY", "gyroZ"],
#         kind="line", title="Gyro x,y,z vs Time Location D", ylabel='gyro (rad/s)').set_xlim(xmin=0, xmax=(time[len(time)-1]+1))

# plt.show()

# plot1 = sea.scatterplot(x = 'UTM_easting', y = 'UTM_northing', data = LocationD_df).set(title = 'RTK Stationary Easting vs Northing Open')
# plot2 = sea.scatterplot(x = 'UTM_easting', y = 'UTM_northing', data = LocationA_df).set(title = 'RTK Stationary Easting vs Northing Occluded')
# plot3 = sea.scatterplot(x = 'Time', y = 'Altitude', data = LocationD_df).set(title = 'RTK Stationary Altitude vs Time Open')
# plot4 = sea.scatterplot(x = 'Time', y = 'Altitude', data = LocationA_df).set(title = 'RTK Stationary Altitude vs Time Occluded')
# plot5 = sea.scatterplot(x = 'Time', y = 'Altitude', data = LocationC_df).set(title = 'RTK Walking Altitude vs Time Open')
# plot6 = sea.scatterplot(x = 'Time', y = 'Altitude', data = LocationC_df).set(title = 'RTK Walking Altitude vs Time Occluded')
# plot2 = sea.regplot(x = 'UTM_easting', y = 'UTM_northing', data = LocationD_df)

# ax = plot2
# ax.legend()
# leg = ax.get_legend()
# L_labels = leg.get_texts()
# slope, intercept, r_value, p_value, std_err = stats.linregress(LocationC_df['UTM_easting'],LocationC_df['UTM_northing'])
# ax.annotate("r-squared = {:.3f}".format(r_value), (-10, 32))
# ax.annotate("y={0:.2f}x{1:.2f}".format(slope,intercept), (-10, 29))
# ax.annotate("error = {:.3f}m".format(std_err), (-10, 26))


# label_line_1 = r'$y={0:.1f}x+{1:.1f}'.format(slope,intercept)
# label_line_2 = r'$R^2:{0:.2f}$'.format(r_value)
# L_labels.set_text(label_line_1)
# L_labels[2].set_text(label_line_2)

# LocationD_easting_mean = LocationD_df['UTM_easting'].mean()
# LocationD_northing_mean = LocationD_df['UTM_northing'].mean()
# LocationD_mean_coord = [LocationD_easting_mean, LocationD_northing_mean]


# LocationD_xlist = LocationD_df['UTM_easting'].tolist()
# LocationD_ylist = LocationD_df['UTM_easting'].tolist()

# LocationA_easting_mean = LocationA_df['UTM_easting'].mean()
# LocationA_northing_mean = LocationA_df['UTM_northing'].mean()
# LocationA_mean_coord = [LocationA_easting_mean, LocationA_northing_mean]


# LocationA_xlist = LocationA_df['UTM_easting'].tolist()
# LocationA_ylist = LocationA_df['UTM_easting'].tolist()


error = []

i = 0
# while i < len(LocationD_xlist):
#     error.append(((LocationD_xlist[i] - LocationD_easting_mean)**2 + (LocationD_ylist[i] - LocationD_northing_mean)**2)**.5)
#     i += 1

# while i < len(LocationA_xlist):
#     error.append(((LocationA_xlist[i] - LocationA_easting_mean)**2 + (LocationA_ylist[i] - LocationA_northing_mean)**2)**.5)
#     i += 1

# nperror = np.array(error)
# sea.histplot(data=nperror)
# print(nperror.mean())
# print(np.median(error))

#print(mean_coord)
# plt.title('Occluded Stationary Error')
# plt.xlabel('Position error in [m]')
# plt.ylabel('UTM_northing in [m]')

# plt.show()