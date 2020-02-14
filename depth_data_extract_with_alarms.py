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

2.1.20 EC: Took the averaged range information inside the target box defined by 
dimensions meas_width and meas_height and stacked the result in a 'distance bar'
to be displayed in the same window as the color image.
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

#configure the realsense's color and depth stream given dimensions for width and height
config.enable_stream(rs.stream.depth, orig_width, orig_height, rs.format.z16, fps)
config.enable_stream(rs.stream.color, orig_width, orig_height, rs.format.bgr8, fps)

#Defining parameters for target measure area. We are going to measure a box with
#dimensions box_width by box_height centered in the image and average the 
#range information inside that box. This is for phase 1 of the project. The simple
#arithmetic mean performed here can lead to inaccurate distance measurements

box_width = 75
box_height = 75

#defining measure area/box coordinates within image
box_width_min = int((orig_width - box_width)//2 -1)        #coordinates to center box within image. This is the first horizontal coordinate for the measure box
box_height_min = int((orig_height - box_height)//2 -1)     #y-coordinate to center box within image

box_width_max = int(box_width_min + box_width)
box_height_max = int(box_height_min + box_height)

#start streaming
profile = pipeline.start(config)

"""
#debugging. 

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

#get data scale from the realsense to convert distance to meters
depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()

#alarm distance boundaries - We can give these variables more meaningful names
alarm_dist1 = 2.50
alarm_dist2 = 1.75
alarm_dist3 = 1.0

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
        resized_depth_image = resized_depth_image * depth_scale
        
        #averaging range information inide the measurement box at center of image
        avg_dist = cv2.mean(resized_depth_image)
        
        #converting average distance information/measurement to a string to be printed onto the screen
        avg_dist_str = str('%0.3f'%(avg_dist[0])) 
        avg_dist_float = float('%0.5f'%(avg_dist[0]))
        #print(f"Object detected at average distance: {avg_dist[0]} meters")
                
        
        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha = 0.03), cv2.COLORMAP_JET)
        
        #print rectangle on color image for cyclist's benefit
        cv2.rectangle(color_image, (box_width_min, box_height_min), 
             (box_width_max, box_height_max), (0, 255, 0), 2)
        
        #BGR values for green (0,255,0)
        #BGR values for green (255,255,255) 
        
        #creating an 'image' with dimensions as shown below to display the distance information stacked below the color image
        dist_bar_height = 100
        distance_bar = np.zeros([dist_bar_height,orig_width,3], dtype=np.uint8)     #numpy array that will represent the 'image' or bar to print the distance measurement 

        #filling up numpy array with 255's to create a white background
        distance_bar.fill(255)

        #print distance measurement onto the distance bar image 
        cv2.putText(distance_bar, "Distance to object: "+avg_dist_str +" m", 
            (100,80),
            cv2.FONT_HERSHEY_COMPLEX, 0.75, (255,0,0))
        
        
        #Distance Alarm Code
        
       
        if avg_dist_float > alarm_dist2 and avg_dist_float < alarm_dist1:
            text_color_tuple = (0,165,255)  #orange
            cv2.putText(distance_bar, f"Warning: Object is within {alarm_dist2}m and {alarm_dist1}m!", 
            (60,50),
            cv2.FONT_HERSHEY_COMPLEX, 0.75, text_color_tuple)
            
            #Changing rectangle color
            cv2.rectangle(color_image, (box_width_min, box_height_min), 
             (box_width_max, box_height_max), (0,165,255), 2)
        
        elif avg_dist_float > alarm_dist3 and avg_dist_float < alarm_dist2:
            text_color_tuple = (0,0,255)  #red
            cv2.putText(distance_bar, f"Warning: Object is within {alarm_dist3}m and {alarm_dist2}m!", 
            (60,50),
            cv2.FONT_HERSHEY_COMPLEX, 0.75, text_color_tuple)
            
            #Changing rectangle color
            cv2.rectangle(color_image, (box_width_min, box_height_min), 
             (box_width_max, box_height_max), (0,0,255), 2)
            
        #stack images vertically for displaying
        images = np.vstack((color_image,distance_bar))
        
        
        #Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        #cv2.imshow('Realsense', color_image)
        cv2.imshow('Realsense', images)
        cv2.waitKey(1)
        
        
        
        '''
        Commented out code that was used throughout script development
        
        # Stack both images horizontally
        #images = np.hstack((color_image,depth_colormap))
        
        #creating rectangle/monitor region in image
        #cv2.rectangle(depth_colormap, (box_width_min, box_height_min), 
             #(box_width_max, box_height_max), (255, 255, 255), 2)
             
        #distance_bar = np.zeros([100,orig_width,3], dtype=np.uint8)
        #distance_bar.fill(255)
        
        
        #cv2.rectangle(color_image, (box_width_min, box_height_min), 
             #(box_width_max, box_height_max), (255, 255, 255), 2)
        
                #cv2.putText(color_image, "Average distance to object: "+avg_dist_str +" m", 
            #(box_width_min, box_height_min - 5),
            #cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,255))
        
        #images = np.vstack((depth_colormap,distance_bar))
        
        '''
        
        
        
finally:
    # Stop streaming
    pipeline.stop()
