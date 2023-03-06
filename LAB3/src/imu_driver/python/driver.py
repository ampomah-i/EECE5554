#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
import utm
import serial
import sys
import numpy as np
from datetime import datetime
from imu_driver.msg import *
from imu_driver.msg import imu_msg
from imu_driver.srv import convert_to_quaternion, convert_to_quaternionResponse


# def euler_quaternion(roll, pitch, yaw):
#     rospy.init_node("euler_quaternion_client_node")
#     rospy.wait_for_service("convert_to_quaternion")
    
#     while not rospy.is_shutdown():
#         try:
#             quaternions = rospy.ServiceProxy("convert_to_quaternion", convert_to_quaternion)
#             response = quaternions(roll, pitch, yaw)
#             rospy.loginfo(response.result)
#         except rospy.ServiceException as e:
#             print("Service call failed %s", e)    

def driver():
    pub = rospy.Publisher('imu', imu_msg, queue_size=10)
    rospy.init_node('imu_driver_node', anonymous=True)
    rospy.wait_for_service("convert_to_quaternion")

    msg = imu_msg()
    seq= 0

    args = rospy.myargv(argv = sys.argv)
    if len(args) != 2:
        print("error")
        sys.exit(1)

    connected_port = args[1]
    serial_port = rospy.get_param('~port', connected_port)
    serial_baud = rospy.get_param('~baudrate',115200)


    ser = serial.Serial(serial_port, serial_baud, timeout = 3)
    ser.write(b"$VNWRG,07,40*xx")
    while not rospy.is_shutdown():
        message = ser.readline()
        decoded_message = message.decode()
        seq = seq + 1
        
        # ensure reading of VNYMR
        if "VNYMR" in decoded_message:
            data = decoded_message.split(",")

            now = rospy.get_rostime()
            rospy.loginfo("Current time %i %i", now.secs, now.nsecs)

            yaw = float(data[1])
            pitch = float(data[2])
            roll = float(data[3])
            magX = float(data[4])
            magY = float(data[5])
            magZ = float(data[6])
            accX = float(data[7])
            accY = float(data[8])
            accZ = float(data[9])
            gyroX = float(data[10])
            gyroY = float(data[11])
            gyroZ = float(data[12][0:9])

            try:
                quaternions = rospy.ServiceProxy("convert_to_quaternion", convert_to_quaternion)
                response = quaternions(roll, pitch, yaw)
                #rospy.loginfo(response.qx)
            except rospy.ServiceException as e:
                print("Service call failed %s", e)   

            #msg.header.stamp = rospy.Time.from_sec(now)
            msg.header.seq = seq
            msg.header.stamp.secs = int(now.secs)
            msg.header.stamp.nsecs = int(now.nsecs)
            msg.header.frame_id = 'imu1_frame'

            msg.IMU.header.seq = seq
            msg.IMU.header.stamp.secs = int(now.secs)
            msg.IMU.header.stamp.nsecs = int(now.secs)
            msg.IMU.header.frame_id = 'imu1_frame'

            msg.MagField.header.seq = seq
            msg.MagField.header.stamp.secs = int(now.secs)
            msg.MagField.header.stamp.nsecs = int(now.secs)
            msg.MagField.header.frame_id = 'imu1_frame'

            msg.IMU.orientation.x = response.qx
            msg.IMU.orientation.y = response.qy
            msg.IMU.orientation.z = response.qz
            msg.IMU.orientation.w = response.qw
            msg.IMU.linear_acceleration.x = accX
            msg.IMU.linear_acceleration.y = accY
            msg.IMU.linear_acceleration.z = accZ
            msg.IMU.angular_velocity.x = gyroX
            msg.IMU.angular_velocity.y = gyroY
            msg.IMU.angular_velocity.z = gyroZ
            msg.MagField.magnetic_field.x = magX
            msg.MagField.magnetic_field.y = magY
            msg.MagField.magnetic_field.z = magZ

            pub.publish(msg)
            print(msg)
            #rate.sleep()

if __name__ == '__main__':
    try:
        driver()
    except rospy.ROSInterruptException:
        pass
