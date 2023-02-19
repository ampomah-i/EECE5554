import bagpy
from bagpy import bagreader
import pandas as pd
import seaborn as sea
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

occluded_s = bagreader('occluded_s.bag')
open_s = bagreader('open_s.bag')
occluded_m = bagreader('occluded_m.bag')
open_m = bagreader('open_m.bag')

csvfiles = []

def scale(dataframe):
    row = dataframe[0:1]
    easting_scale = row.iloc[0]['UTM_easting']
    northing_scale = row.iloc[0]['UTM_northing']
    time_scale = row.iloc[0]['Time']

    dataframe['UTM_easting']-= easting_scale
    dataframe['UTM_northing'] -= northing_scale
    dataframe['Time'] -= time_scale

    return(dataframe)

for t in occluded_m.topics:
    data1 = occluded_m.message_by_topic(t)
    csvfiles.append(data1)

for t in open_s.topics:
    data2 = open_s.message_by_topic(t)
    csvfiles.append(data2)

for t in open_m.topics:
    data3 = open_m.message_by_topic(t)
    csvfiles.append(data3)

for t in occluded_s.topics:
    data4 = occluded_s.message_by_topic(t)
    csvfiles.append(data4)

occluded_m_df = pd.read_csv('occluded_m/gps.csv')
occluded_s_df = pd.read_csv('occluded_s/gps.csv')
open_m_df = pd.read_csv('open_m/gps.csv')
open_s_df = pd.read_csv('open_s/gps.csv')

scale(occluded_m_df)
scale(open_m_df)
scale(open_s_df)
scale(occluded_s_df)

# plot1 = sea.scatterplot(x = 'UTM_easting', y = 'UTM_northing', data = open_s_df).set(title = 'RTK Stationary Easting vs Northing Open')
# plot2 = sea.scatterplot(x = 'UTM_easting', y = 'UTM_northing', data = occluded_s_df).set(title = 'RTK Stationary Easting vs Northing Occluded')
# plot3 = sea.scatterplot(x = 'Time', y = 'Altitude', data = open_s_df).set(title = 'RTK Stationary Altitude vs Time Open')
# plot4 = sea.scatterplot(x = 'Time', y = 'Altitude', data = occluded_s_df).set(title = 'RTK Stationary Altitude vs Time Occluded')
# plot5 = sea.scatterplot(x = 'Time', y = 'Altitude', data = open_m_df).set(title = 'RTK Walking Altitude vs Time Open')
# plot6 = sea.scatterplot(x = 'Time', y = 'Altitude', data = open_m_df).set(title = 'RTK Walking Altitude vs Time Occluded')
# plot2 = sea.regplot(x = 'UTM_easting', y = 'UTM_northing', data = open_s_df)

# ax = plot2
# ax.legend()
# leg = ax.get_legend()
# L_labels = leg.get_texts()
# slope, intercept, r_value, p_value, std_err = stats.linregress(open_m_df['UTM_easting'],open_m_df['UTM_northing'])
# ax.annotate("r-squared = {:.3f}".format(r_value), (-10, 32))
# ax.annotate("y={0:.2f}x{1:.2f}".format(slope,intercept), (-10, 29))
# ax.annotate("error = {:.3f}m".format(std_err), (-10, 26))


# label_line_1 = r'$y={0:.1f}x+{1:.1f}'.format(slope,intercept)
# label_line_2 = r'$R^2:{0:.2f}$'.format(r_value)
# L_labels.set_text(label_line_1)
# L_labels[2].set_text(label_line_2)

# open_s_easting_mean = open_s_df['UTM_easting'].mean()
# open_s_northing_mean = open_s_df['UTM_northing'].mean()
# open_s_mean_coord = [open_s_easting_mean, open_s_northing_mean]


# open_s_xlist = open_s_df['UTM_easting'].tolist()
# open_s_ylist = open_s_df['UTM_easting'].tolist()

occluded_s_easting_mean = occluded_s_df['UTM_easting'].mean()
occluded_s_northing_mean = occluded_s_df['UTM_northing'].mean()
occluded_s_mean_coord = [occluded_s_easting_mean, occluded_s_northing_mean]


occluded_s_xlist = occluded_s_df['UTM_easting'].tolist()
occluded_s_ylist = occluded_s_df['UTM_easting'].tolist()


error = []

i = 0
# while i < len(open_s_xlist):
#     error.append(((open_s_xlist[i] - open_s_easting_mean)**2 + (open_s_ylist[i] - open_s_northing_mean)**2)**.5)
#     i += 1

while i < len(occluded_s_xlist):
    error.append(((occluded_s_xlist[i] - occluded_s_easting_mean)**2 + (occluded_s_ylist[i] - occluded_s_northing_mean)**2)**.5)
    i += 1

nperror = np.array(error)
sea.histplot(data=nperror)
# print(nperror.mean())
# print(np.median(error))

#print(mean_coord)
plt.title('Occluded Stationary Error')
plt.xlabel('Position error in [m]')
# plt.ylabel('UTM_northing in [m]')

plt.show()