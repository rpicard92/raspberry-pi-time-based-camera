# USAGE
# python real_time_object_detection.py --picamera 1 --time 60

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
from smtp import EmailMessageBuilder
import pytz
from datetime import datetime
from tzlocal import get_localzone 
import Tkinter
import tkMessageBox
import threading
import socket
import sys


# Collect frames from a video stream
def collectFrames(VideoStream,numberOfFrames,fps):
        
        count = 0
        frameArray = []

        # collect frames
        while count < numberOfFrames:

                # grab the frame from the threaded video stream and resize it
                # to have a maximum width of 400 pixels, rotate to correct camera angle
                frame = VideoStream.read()
                frame = imutils.resize(frame, width=400)
                frame = imutils.rotate_bound(frame, 270)
                #frame = imutils.rotate_bound(frame, 180)

                # store frame
                frameArray.append(frame)
                count = count + 1

                # collect frame every 0.1 seconds
                time.sleep(fps)

                # logger
                print('[INFO] Frames Collected: ' + str(count) + ' frames, Timestamp: ' + str(time.time()) + ' seconds' )

        return frameArray


# write video from frames
def writeVideo(frameArray,outputPath):

        # codec        
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        writer = None
        frameCount = 0

        # loop frames and write to video
        for frame in frameArray:

                # initialize writer
                if writer is None:
                        (h, w) = frame.shape[:2]
                        writer = cv2.VideoWriter(outputPath,fourcc,20,(w, h),True)
               
                # write frame to video
                writer.write(frame);  
                frameCount = frameCount + 1
               
                # logger
                print('[INFO] Frames written: ' + str(frameCount) + ' frames' + ', Timestamp: ' + str(time.time()) + 'seconds')

def emailVideo(outputPath):
 
        local_tz = get_localzone() 
        tz = pytz.timezone(str(local_tz))
        now = datetime.now(tz)

        email = ''
        password = ''
        subject = 'Feeding Alert from the Cat Cam!'
        body = str(now)
        server = 'smtp.gmail.com'
        port = 587
        video = outputPath

        messageBuilder = EmailMessageBuilder()
        messageBuilder.buildMessage(email,email,subject,body,video)
        messageBuilder.buildSMTPServer(server,port)
        messageBuilder.sendMessage(email,password)

def initVideoStream(camera):
        # initialize the video stream, allow the cammera sensor to warmup,
        print("[INFO] starting video stream...")
        vs = VideoStream(usePiCamera=camera > 0).start()
        time.sleep(2.0)
        return vs

def closeVideoStream(VideoStream):
        print("[INFO] closing video stream...")
        cv2.destroyAllWindows()
        VideoStream.stop()


def run(camera, timeOfClips, outputPath, VideoStream):
        print('[INFO] Initiating Recording Protocol...')

        # Start Time
        startTime = time.time()
        
        fps = 0.1

        # main logic
        numberOfFrames = timeOfClips/fps
        frameArray = collectFrames(VideoStream,numberOfFrames,fps)
        writeVideo(frameArray,outputPath)   
        emailVideo(outputPath)

        # end time
        endTime = time.time()
        elapsedTime = endTime - startTime

        # logger
        print('[INFO] Recording Protocol Complete.')
        print('[INFO] Number Of Frames: ' + str(numberOfFrames) + ' frames')
        print('[INFO] Length Of Video: ' + str(timeOfClips) + ' seconds')
        print('[INFO] Path To Video: ' + str(outputPath))
        print('[INFO] Elapsed Time: ' + str(elapsedTime) + ' seconds')


def idle(camera, timeOfClips, outputPath):
        print("[INFO] System turned on.")
        print("[INFO] Initiating idle state...")
        local_tz = get_localzone() 
        tz = pytz.timezone(str(local_tz))
        VideoStream = initVideoStream(camera)
        while True:
                now = datetime.now().strftime('%H:%M:%S')
                #print(now)
                if(str(now) == '05:50:00' or str(now) == '18:00:00'):
                        print("[INFO] Frame Capture Started.")
                        run(camera, timeOfClips, outputPath, VideoStream)
                        print("[INFO] Frame Capture Finished.")
                        print("[INFO] Frame Capture Started.")
                        run(camera, timeOfClips, outputPath, VideoStream)
                        print("[INFO] Frame Capture Finished.")
                        print("[INFO] Frame Capture Started.")
                        run(camera, timeOfClips, outputPath, VideoStream)
                        print("[INFO] Frame Capture Finished.")
                        print("[INFO] Frame Capture Started.")
                        run(camera, timeOfClips, outputPath, VideoStream)
                        print("[INFO] Frame Capture Finished.")
                        print("[INFO] Frame Capture Started.")
                        run(camera, timeOfClips, outputPath, VideoStream)
                        print("[INFO] Frame Capture Finished.")

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()

ap.add_argument("-r", "--picamera", type=int, default=1,
        help="whether or not the Raspberry Pi camera should be used")
ap.add_argument("-t", "--time",type=int, default=60,
        help="time in seconds")
ap.add_argument("-o", "--outputPath", default='test.avi',
        help="output video file path")

args = vars(ap.parse_args())

camera = args["picamera"]
timeOfClips = args['time']
outputPath = args['outputPath']

idle(camera, timeOfClips, outputPath)
