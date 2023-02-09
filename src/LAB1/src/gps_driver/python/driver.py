#!/usr/bin/env python3
# link to GPGGA fields https://www.hemispheregnss.com/technical-resource-manual/Import_Folder/GPGGA_Message.htm

import rospy
import serial
import utm
from gps_driver.msg import gps_msg
from datetime import date, datetime


def latlong_to_decimal(latlong):
    # Store digit section of latlong
    nums = latlong[0]
    decimal_break = nums.split(".")
    pre_decimal = decimal_break[0]
    minutes = float(pre_decimal[-2:]+'.'+decimal_break[1])/60
    degrees = int(pre_decimal[:-2])

    indicator = latlong[1]

    # Convert to decimal
    decimal = round((degrees + minutes), 6)
    if indicator == 'W':
        return decimal * (-1)
    
    elif indicator == "S":
         return decimal * (-1)

    else:
        return decimal

    print(decimal)

# Helper function to convert GPGGA time to seconds and nanosec integers
def UTC_to_sec_nsec(utc):
    counter = 0
    split_time = utc.split(".")
    hhmmss = split_time[0]
    hh = int(hhmmss[0]+hhmmss[1])
    mm = int(hhmmss[2]+hhmmss[3])
    ss = int(hhmmss[4]+hhmmss[5])

    secs = hh*3600+mm*60+ss
    nsecs = int(split_time[1])
    sec_list = [secs, nsecs]

    return sec_list


# Current datetime
date = str(date.today())
# print(date)
date_list = date.split("-")
# print(date_list)
year = int(date_list[0])
# print(year)
month = int(date_list[1])
# print(month)
day = int(date_list[2])
# print(day)

dt = datetime(year, month, day, 0, 0)
# Epoch time
epoch_time = datetime(1970,1,1)
delta = (dt - epoch_time)
# print(delta)

UTC_secs = delta.total_seconds()
# print(UTC_secs)
# print(type(UTC_secs))

#return UTC_secs

# print("done 1")


if __name__ == "__main__":

    # parser = argparse.ArgumentParser(description='Take in port name')    
    # args = parser.parse_args((rospy.myargv()[1:]))

    # portname = args.port
    portnam = rospy.get_param(rospy.myargv()[1])
    print(portnam)
    SENSOR_NAME = "GPS1_FRAME"
    rospy.init_node('driver')
    serial_port = rospy.get_param('~port', portnam)
    serial_baud = rospy.get_param('~baudrate',4800)
    sampling_rate = rospy.get_param('~sampling_rate', 1.0)

    DATA = gps_msg()
    DATA.Header.frame_id = "GPS1_FRAME"
    # Open serial port
    ser = serial.Serial(serial_port, serial_baud)

    # Log messages
    rospy.logdebug("Using gps puch on port " +serial_port+ " at " +str(serial_baud))

    # Publisher
    gps_publish = rospy.Publisher("gps", gps_msg, queue_size=5)

    # print("Done 2")

    while True:
            while not rospy.is_shutdown():
                # Reading serial messages
                puck_message = ser.readline()
                # Decoding serial messages into string
                decoded_puck_message = puck_message.decode()
                # print("Done 3")

                if 'GPGGA' in decoded_puck_message:
                    # Storing message as a list of values
                    message_list = decoded_puck_message.split(",")
                    # print("Done 4")

                    # Extract GPGGA Lat and Long
                    latitude = [message_list[2], message_list[3]]
                    longitude = [message_list[4], message_list[5]]
                    # print("Done 5")

                    # Convert Lat and Long to decimal
                    lat_decimal = latlong_to_decimal(latitude)
                    long_decimal = latlong_to_decimal(longitude)
                    # print(lat_decimal)
                    # print(long_decimal)

                    # Convert Lat and Long to UTM
                    latlong_to_utm = utm.from_latlon(lat_decimal,long_decimal)
                    # print("Done 7")

                    # Convert UTC time from GPGGA to secs and nsecs
                    time_in_seconds = UTC_to_sec_nsec(message_list[1])
                    # print("Done 8")

                    # Assign all values to message fields
                    DATA.Header.stamp.secs = time_in_seconds[0]
                    DATA.Header.stamp.nsecs = time_in_seconds[1]
                    DATA.Header.seq+=1
                    DATA.Latitude = lat_decimal
                    DATA.Longitude = long_decimal
                    DATA.Altitude = float(message_list[9])
                    DATA.HDOP = float(message_list[7])
                    DATA.UTM_easting = latlong_to_utm[0]
                    DATA.UTM_northing = latlong_to_utm[1]
                    DATA.Zone = latlong_to_utm[2]
                    DATA.Letter = latlong_to_utm[3]                    
                    DATA.UTC = UTC_secs + time_in_seconds[0]
                    # print("Done 9")

                    gps_publish.publish(DATA)
                    print(DATA)
                    print(puck_message)
                    print(latlong_to_utm)
                    # print(HDOP)
                    # print(message_list[1])
