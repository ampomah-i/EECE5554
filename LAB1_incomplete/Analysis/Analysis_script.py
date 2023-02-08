import bagpy
from bagpy import bagreader
import pandas as pd
import seaborn as sea
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

walking = bagreader('walking.bag')
stationary_open = bagreader('stationary_open_area.bag')
occluded = bagreader('occluded.bag')

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

for t in walking.topics:
    data1 = walking.message_by_topic(t)
    csvfiles.append(data1)

for t in stationary_open.topics:
    data2 = stationary_open.message_by_topic(t)
    csvfiles.append(data2)

for t in occluded.topics:
    data3 = occluded.message_by_topic(t)
    csvfiles.append(data3)

walking_df = pd.read_csv('walking/gps.csv')
stationary_open_df = pd.read_csv('stationary_open_area/gps.csv')
occluded_df = pd.read_csv('occluded/gps.csv')

scale(stationary_open_df)
scale(walking_df)
scale(occluded_df)

plot = sea.lmplot(x = 'Time', y = 'Altitude', data = walking_df, line_kws={'label':"Linear Reg"}, legend= True)

ax = plot.axes[0,0]
ax.legend()
leg = ax.get_legend()
L_labels = leg.get_texts()
slope, intercept, r_value, p_value, std_err = stats.linregress(walking_df['UTM_easting'],walking_df['UTM_northing'])
label_line_1 = r'$y={0:.1f}x+{1:.1f}'.format(slope,intercept)
label_line_2 = r'$R^2:{0:.2f}$'.format(r_value)
L_labels[0].set_text(label_line_2)
#L_labels[1].set_text(label_line_2)

#stationary_open_df.plot(kind='scatter', x= 'UTM_easting', y='UTM_northing', title='Sationary Open Area Easting vs Northing')
'''sea.regplot(x= walking_df['Time'],
            y = walking_df['Altitude']).set(title='Walking Altitude(m) vs Time(s)')'''
'''sea.regplot(x= stationary_open_df['UTM_easting'],
            y =stationary_open_df['UTM_northing']).set(title='Open Area Northing vs Easting in Meters')'''
#sea.regplot(x= walking_df['UTM_easting'], y =walking_df['UTM_northing']).set(title='Walking Easting vs Northing')
#sea.regplot(x= occluded_df['UTM_easting'], y =occluded_df['UTM_northing']).set(title='Occluded Area Easting vs Northing')
easting_mean = occluded_df['UTM_easting'].mean()
northing_mean = occluded_df['UTM_northing'].mean()
#mean_coord = [easting_mean, northing_mean]

'''xlist = stationary_open_df['UTM_easting'].tolist()
ylist = stationary_open_df['UTM_easting'].tolist()'''

'''xlist = occluded_df['UTM_easting'].tolist()
ylist = occluded_df['UTM_easting'].tolist()'''
xlist = occluded_df['UTM_easting'].tolist()
ylist = occluded_df['UTM_easting'].tolist()

distance = []
actual = []

i = 0
while i < len(xlist):
    distance.append((((xlist[i] - easting_mean)**2) + ((ylist[i] - northing_mean)**2))**.5)
    actual.append(0.1)
    i += 1


'''
hist_data = np.array(distance)

print(hist_data.mean())
print(np.median(distance))'''

'''fig, ax = plt.subplots(figsize =(10, 7))
ax.hist(hist_data, bins = [4,5,6,7,8,9,10])'''

#print(mean_coord)
#plt.title('Open area error histogram in Meters.')
plt.show()