1 #!/usr/bin/env python

import rospy
import numpy as np
from imu_driver.srv import convert_to_quaternion, convert_to_quaternionResponse

def convert(req):
    #def orientation(roll=req.a, pitch=req.b, yaw=req.c):   #Convert an Euler angle to a quaternion.
    roll = req.roll*(np.pi/180)
    pitch = req.pitch*(np.pi/180)
    yaw = req.yaw*(np.pi/180)

    qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
    qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)
    qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    
    return convert_to_quaternionResponse(qx, qy, qz, qw)
  
def convert_to_quaternions():
    rospy.init_node('convert_to_quaternions_service')
    s = rospy.Service('convert_to_quaternion', convert_to_quaternion, convert)
    rospy.spin()
  
if __name__ == "__main__":
    convert_to_quaternions()