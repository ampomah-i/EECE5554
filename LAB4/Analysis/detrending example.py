import numpy as np
import matplotlib.pyplot as plt

# Sample data
time_data = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
position_data = np.array([0, 3, 6, 10, 15, 21, 28, 36, 45, 55])

# Fit a linear regression model to the data
coefficients = np.polyfit(time_data, position_data, deg=1)
trend_line = np.poly1d(coefficients)

# Calculate the trend for each data point
trend_data = trend_line(time_data)

# Detrend the data by subtracting the trend from the original data
detrended_data = position_data - trend_data

# Plot original data, trend, and detrended data
plt.figure()
plt.plot(time_data, position_data, label="Original Data")
plt.plot(time_data, trend_data, label="Trend Line")
plt.plot(time_data, detrended_data, label="Detrended Data")
plt.legend()
plt.show()