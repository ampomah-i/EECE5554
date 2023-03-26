import numpy as np
import scipy.integrate as integrate
import matplotlib.pyplot as plt

#I create time and rate arrays here for the example. You would read these in from your rosbags
time = np.linspace(0, 1/40.0, 1000) #Create an array-like of time at "sampling frequency" of 40 Hz
rate = np.random.uniform(low = -1e-2, high = 1e-3, size = 1000)+1e-3 #Create list of random variables representing rotational rate
	
#Integrate using cumulative integration, trapezoidal method. This generates an array describing cumulative array for each timepoint
rotation = integrate.cumulative_trapezoid(rate, time, initial = 0)   

#Plot settings
plt.style.use("seaborn-dark")
fig, ax = plt.subplots()

ax.scatter(time, rate)
ax.scatter(time, rotation)
#ax.set(xlim = (0,np.amax(time)), ylim = (np.amin(rotation), np.amax(rotation)))
plt.xlabel('Time (s)')
plt.ylabel('Rotation (deg)')
plt.show()


