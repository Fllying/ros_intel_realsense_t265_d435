#!/usr/bin/env python
import argparse
import rosbag
import rospy
import message_filters
import os
import datetime
from sensor_msgs.msg import Image, CameraInfo, Imu, PointCloud2
from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage
from message_filters import ApproximateTimeSynchronizer, Subscriber

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-p","--path", default=os.getcwd(), help="path to bag")
parser.add_argument("-b","--bag", default=datetime.datetime.now().strftime("%Y-%m%d-%H-%M-%S")+".bag", help="name of bag")
opt = parser.parse_args()


bagAbsPath = os.path.join(opt.path, opt.bag);
bag = rosbag.Bag(bagAbsPath, 'w')
rospy.init_node("sync_data")
rospy.logwarn("rosbag path:" + bagAbsPath)

topics = [
    "/d435/color/image_raw",
    "/d435/depth/image_rect_raw",
    "/d435/depth/color/points",
    "/d435/infra1/image_rect_raw",
    "/d435/infra2/image_rect_raw",
    "/t265/fisheye1/image_raw",
    "/t265/fisheye2/image_raw",
    "/t265/accel/sample",
    "/t265/gyro/sample",
    "/t265/odom/sample",
    "/tf",

    "/d435/color/camera_info",
    "/d435/depth/camera_info",
    "/d435/infra1/camera_info",
    "/d435/infra2/camera_info",
    "/t265/fisheye1/camera_info",
    "/t265/fisheye2/camera_info",
    "/tf_static"
]

static_init = False
def static_callback(*arg):
    global static_init
    if static_init:
        return
    try:
        for i, e in enumerate(arg):
            rospy.logwarn(topics[11+i])
            bag.write(topics[11+i], e)
        bag.flush()
        rospy.logwarn("statics finished...")
        static_init = True
    except Exception as e:
        print("#static#")
        rospy.logerr(e)

def callback(*arg):
    global static_init
    if not static_init:
        return
    try:
        for i, e in enumerate(arg):
            bag.write(topics[i], e)
        bag.flush()
        print(datetime.datetime.now())
    except Exception as e:
        rospy.logerr(e)


subscription = [
    Subscriber(topics[0], Image),
    Subscriber(topics[1], Image),
    Subscriber(topics[2], PointCloud2),
    Subscriber(topics[3], Image),
    Subscriber(topics[4], Image),
    Subscriber(topics[5], Image),
    Subscriber(topics[6], Image),
    Subscriber(topics[7], Imu),
    Subscriber(topics[8], Imu),
    Subscriber(topics[9], Odometry),
    Subscriber(topics[10], TFMessage)
]

subscription_static = [
    Subscriber(topics[11], CameraInfo),
    Subscriber(topics[12], CameraInfo),
    Subscriber(topics[13], CameraInfo),
    Subscriber(topics[14], CameraInfo),
    Subscriber(topics[15], CameraInfo),
    Subscriber(topics[16], CameraInfo),
    Subscriber(topics[17], TFMessage)
]

ts = ApproximateTimeSynchronizer(subscription, queue_size=11, slop=0.1, allow_headerless=True)
ts.registerCallback(callback)

ts_static = ApproximateTimeSynchronizer(subscription_static, queue_size=7, slop=0.1, allow_headerless=True)
ts_static.registerCallback(static_callback)

rospy.spin()

bag.close()
rospy.loginfo("saved.")