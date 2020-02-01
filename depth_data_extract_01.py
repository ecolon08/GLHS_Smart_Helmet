# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 18:58:51 2020

@author: Ernesto
"""

"""
Example Code to stream color and depth data from the RealSense Camera
and display them. Script relies on OpenCV and Numpy

1.31.20 EC: I am going to try to extract depth data for a subset of the entire array
returned by the camera. That is, I want a centered box and report range info
"""

import pyrealsense2 as rs
import numpy as np
import cv2

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
orig_width = 640
orig_height = 480
fps = 30
config.enable_stream(rs.stream.depth, orig_width, orig_height, rs.format.z16, fps)
config.enable_stream(rs.stream.color, orig_width, orig_height, rs.format.bgr8, fps)

meas_width = 200
meas_height = 200
box_width_min = int((orig_width - meas_width)//2 -1)
box_height_min = int((orig_height - meas_height)//2 -1)

box_width_max = int(box_width_min + meas_width)
box_height_max = int(box_height_min + meas_height)

#start streaming
profile = pipeline.start(config)

"""
#debugging

frames = pipeline.wait_for_frames()
depth_frame = frames.get_depth_frame()
color_frame = frames.get_color_frame()

depth_image = np.asanyarray(depth_frame.get_data())
color_image = np.asanyarray(color_frame.get_data())
        
#view depth data (as a matrix/array) of a meas_width x meas_height box in the center of the image
resized_depth_image = depth_image[box_height_min : box_height_max : 1, box_width_min : box_width_max : 1]
print(resized_depth_image)

pipeline.stop()

"""

depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()
try:
    while True:
    #for i in range(0,10):
        #wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        #if not depth_frame or not color_frame:
            #continue
        
        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        
        #view depth data (as a matrix/array) of a meas_width x meas_height box in the center of the image
        resized_depth_image = depth_image[box_height_min : box_height_max : 1, box_width_min : box_width_max : 1].astype(float)
        
        # Get data scale from the device and convert to meters
        #depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()
        resized_depth_image = resized_depth_image * depth_scale
        avg_dist = cv2.mean(resized_depth_image)
        print(f"Object detected at average distance: {avg_dist[0]} meters")
        #print(resized_depth_image)
        
        
        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha = 0.03), cv2.COLORMAP_JET)
        
        # Stack both images horizontally
        #images = np.hstack((color_image,depth_colormap))
        
        #creating rectangle/monitor region in image
        cv2.rectangle(depth_colormap, (box_width_min, box_height_min), 
             (box_width_max, box_height_max), (255, 255, 255), 2)
        
        
        #Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Realsense', depth_colormap)
        cv2.waitKey(1)
        
finally:
    # Stop streaming
    pipeline.stop()
