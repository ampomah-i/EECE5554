import numpy as np
import matplotlib.pyplot as plt

# Define the vertices of the trapezoid
trapezoid = np.array([(1, 1), (3, 3), (5, 3), (7, 1)])

# Compute the width and height of the rectangle
width = np.max(trapezoid[:, 0]) - np.min(trapezoid[:, 0])
height = np.max(trapezoid[:, 1]) - np.min(trapezoid[:, 1])

# Compute the rotation angle of the rectangle
dx = trapezoid[1, 0] - trapezoid[0, 0]
dy = trapezoid[1, 1] - trapezoid[0, 1]
angle = np.arctan2(dy, dx)

# Compute the scaling factors for the x-axis and y-axis
scale_x = width / np.abs(dx)
scale_y = height / np.abs(dy)

# Define the affine transformation matrix
M = np.array([[np.cos(angle) * scale_x, -np.sin(angle) * scale_y, -np.min(trapezoid[:, 0]) * np.cos(angle) * scale_x + np.min(trapezoid[:, 1]) * np.sin(angle) * scale_y],
              [np.sin(angle) * scale_x, np.cos(angle) * scale_y, -np.min(trapezoid[:, 0]) * np.sin(angle) * scale_x - np.min(trapezoid[:, 1]) * np.cos(angle) * scale_y]])

# Apply the affine transformation to the trapezoid
trapezoid_transformed = np.hstack([trapezoid, np.ones((len(trapezoid), 1))]).dot(M.T)[:, :2]

# Plot the original and transformed trapezoids
fig, ax = plt.subplots(1, 2, figsize=(10, 5))
ax[0].plot(trapezoid[:, 0], trapezoid[:, 1], 'r--')
ax[0].set_title('Original Trapezoid')
ax[1].plot(trapezoid_transformed[:, 0], trapezoid_transformed[:, 1], 'b--')
ax[1].set_title('Transformed Rectangle')
plt.show()