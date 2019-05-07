# USAGE
# python real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel --picamera 1 --time 1 --detections 0

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
        subject = 'Security Alert From Raspberry Pi!'
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


def run(net, confidenceThreshold, camera, timeOfClips, outputPath, classificationType, CLASSES, COLORS, VideoStream):
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


def idle(net, confidenceThreshold, camera, timeOfClips, outputPath, classificationType, CLASSES, COLORS):
        print("[INFO] System turned on.")
        print("[INFO] Initiating idle state...")
        local_tz = get_localzone() 
        tz = pytz.timezone(str(local_tz))
        while True:
                now = datetime.now().strftime('%H:%M:%S')
                #print(now)
                if(str(now) == '05:50:00' or str(now) == '18:00:00'):
                        VideoStream = initVideoStream(camera)
                        run(net, confidenceThreshold, camera, timeOfClips, outputPath, classificationType, CLASSES, COLORS, VideoStream)
                        print("[INFO] Video Stream Finished.")           
                global onOffSwitch
                if (onOffSwitch == False):
                        closeVideoStream(VideoStream)
                        print("[INFO] System turned off.")
                        break


def main():

        # construct the argument parse and parse the arguments
        ap = argparse.ArgumentParser()
        ap.add_argument("-p", "--prototxt", required=True,
                help="path to Caffe 'deploy' prototxt file")
        ap.add_argument("-m", "--model", required=True,
                help="path to Caffe pre-trained model")
        ap.add_argument("-c", "--confidence", type=float, default=0.2,
                help="minimum probability to filter weak detections")
        ap.add_argument("-r", "--picamera", type=int, default=1,
                help="whether or not the Raspberry Pi camera should be used")
        ap.add_argument("-t", "--time",type=int, default=60,
                help="time in seconds")
        ap.add_argument("-o", "--outputPath", default='test.avi',
                help="output video file path")
        ap.add_argument("-f", "--detections", type=int, default=0,
                help="0 will only detect people, 1 will detect all the net is capable of")
        args = vars(ap.parse_args())

        prototxt = args["prototxt"]
        model = args["model"]
        confidenceThreshold = args["confidence"]
        camera = args["picamera"]
        timeOfClips = args['time']
        outputPath = args['outputPath']
        classificationType = args["detections"]

	net = 0

        # initialize the list of class labels MobileNet SSD was trained to
        # detect, then generate a set of bounding box colors for each class
        CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                "sofa", "train", "tvmonitor"]
        COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
        
  
        idle(net, confidenceThreshold, camera, timeOfClips, outputPath, classificationType, CLASSES, COLORS)




def server_response(reponse):
         # pause 5.5 seconds
        print('Sleeping...')
        global PHONE
        global PORT_PHONE
        print('[INFO] Connecting to HOST: ' + str(PHONE) + ', on PORT: ' + str(PORT_PHONE))
        
        # create a client socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
                # bind socket to Host and Port
                s.connect((PHONE, PORT_PHONE))
        except socket.error as err:
                print('[ERROR] Bind Failed, Error Code: ' + str(err))
                sys.exit()
        # send reponse
        s.send(reponse)
        s.close()

def listen_client():
        global PI
        global PORT_PI
        print('[INFO] Connecting to HOST: ' + str(PI) + ', on PORT: ' + str(PORT_PI))
        
        # create a server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
               # bind socket to Host and Port      
                server_socket.bind((PI, PORT_PI))
        except socket.error as err:
                print('[ERROR] Bind Failed, Error Code: ' + str(err))
                sys.exit()
        #listen(): This method sets up and start TCP listener.
        server_socket.listen(10)
        while True:
                conn, addr = server_socket.accept()
                buf = conn.recv(1024)
                if(buf != None):
                        global onOffSwitch
                        if(onOffSwitch == True):
                                onOffSwitch = False
                                server_response('OFF')
                                B["text"] = "OFF"
                        elif(onOffSwitch == False):
                                onOffSwitch = True
                                thread = threading.Thread(target=main)  
                                thread.start() 
                                server_response('ON')
                                B["text"] = "ON"
        server_socket.close()





def callBack():
        global onOffSwitch
        if onOffSwitch == False:
                onOffSwitch = True
                thread = threading.Thread(target=main)  
                thread.start() 
                B["text"] = "ON"
        elif onOffSwitch == True:
                onOffSwitch = False
                B["text"] = "OFF"

# global swtich
onOffSwitch = False

# local host
PI = ''
PORT_PI = 8889
 
# phone
PHONE = ''
PORT_PHONE = 8888

t = threading.Thread(target=listen_client)
t.start()

top = Tkinter.Tk()

B = Tkinter.Button(top, text ="OFF", command = callBack)
B.pack()
top.mainloop()    
