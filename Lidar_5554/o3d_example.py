#A link, as always, to the documentation: http://www.open3d.org/docs/release/

import open3d as o3d
import numpy as np

point_data = o3d.io.read_point_cloud("bunny.pcd")
print(point_data)
geom = o3d.geometry.PointCloud()
geom.points = o3d.utility.Vector3dVector(point_data.points)
o3d.visualization.draw_geometries([geom])