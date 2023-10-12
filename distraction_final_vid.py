# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, too-many-locals, too-many-instance-attributes, no-member, line-too-long, too-many-branches, too-many-statements, broad-except
##############################################################################
###    Module to find faces and alert when person falls into drowsiness.   ###
##############################################################################

"""

@author          : Aravind Pandi S (aravind.pandi@mind-infotech.com)
* title          : drowsiness_yawn.py
* description    : This module will find drowsy face and alert using python.
* version        : v0.2, (01-06-2022)
* revision_notes : 0.1 (Aravind Pandi S, Load predictor, Detect face,
                                         Calculate EAR & MAR, alert, 20-05-2022)
                   0.2 (Aravind Pandi S, Updated on face detector &
                                      Improvement on Yawn detection, 01-06-2022)
* file
  dependencies   : -
* module
  dependencies   : argparse, time, imutils, numpy, dlib, opencv-python (cv2),
                   pyttsx3, threading.
* python_version : 3.9.6
* Pylint
  code_rating    : 10.00/10, Report attached (pylint_report.txt)

"""

# Libraries used
from threading import Thread
import argparse
import time
from math import hypot
import numpy as np
import imutils
from imutils.video import VideoStream
from imutils import face_utils
import dlib
import cv2
import pyttsx3

class Drowsinees:
    """
        * Find drowsiness and alert class.
    """
    def __init__(self) -> None:

        # Parser for command-line
        self.arg_parser = argparse.ArgumentParser()
        self.arg_parser.add_argument("-w", "--webcam", type=int, default=0,
                        help="index of webcam on system")
        self.args = vars(self.arg_parser.parse_args())

        print("-> Starting Video Stream")
        self.video_stream = VideoStream(src=self.args["webcam"]).start()
        #self.video_stream= VideoStream(usePiCamera=True).start()       //For Raspberry Pi

        # sleep for 1 sec
        time.sleep(1.0)

        # self.cap = cv2.VideoCapture(0)
        print("-> Loading the predictor and detector...")
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(r"shape_predictor_68_face_landmarks.dat")

        # Eye threshold value
        self.eye_thresh = 4.5

        # Mouth threshold value
        self.yawn_thresh = 15

        # Nose to Cheek threshold value
        self.NTC_thresh = 25
        
        # Alaram status
        self.alarm_status = False

        #A ... to detect side faces
        self.profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")

        self.time1=time.time()
        self.eye_count = 0
        self.yawn_count = 0
        self.NTC_count = 0
        self.count = 0
        self.s_count = 0
        self.f_count = 0
        self.c_count = 0
        self.VidCount = 0

        # Trigger the initial function
        self.trigger()
        self.timer1 = 0
        self.timer2 = 0

    def alarm(self, msg):
        """
            * Method to trigger alarm
        """
        # initialisation
        engine = pyttsx3.init()

        engine.say(msg)
        try:
            engine.runAndWait()
        except RuntimeError:
            pass
        self.alarm_status = False

    def mid(self, param1 ,param2):
        """
            * Method to find mid point on each eyes
        """
        return int((param1.x + param2.x)/2), int((param1.y + param2.y)/2)

    def eye_aspect_ratio(self, eye_landmark, face_roi_landmark):
        """
            * Method to calculate Eye aspect ratio
        """
        # compute the distance between the horizontal
        # eye landmark (x, y)-coordinates
        left_point = (face_roi_landmark.part(eye_landmark[0]).x,\
             face_roi_landmark.part(eye_landmark[0]).y)
        right_point = (face_roi_landmark.part(eye_landmark[3]).x,\
             face_roi_landmark.part(eye_landmark[3]).y)

        # compute the distances between the two sets of
        # vertical eye landmarks (x, y)-coordinates
        center_top = self.mid(face_roi_landmark.part(eye_landmark[1]),\
             face_roi_landmark.part(eye_landmark[2]))
        center_bottom = self.mid(face_roi_landmark.part(eye_landmark[5]),\
             face_roi_landmark.part(eye_landmark[4]))

        # Find final length on horizontal & vertical lines
        hor_line_length = hypot((left_point[0] - right_point[0]),\
             (left_point[1] - right_point[1]))
        ver_line_length = hypot((center_top[0] - center_bottom[0]),\
             (center_top[1] - center_bottom[1]))

        # Find the ration and return it
        ratio = hor_line_length / ver_line_length
        return ratio

    def lip_distance(self, shape):
        """
            * Method to calculate Mouth aspect ratio
        """
        # Top lip range from "self.predictor"
        top_lip = shape[50:53]
        
        top_lip = np.concatenate((top_lip, shape[61:64]))
        # print("toplip",top_lip)
        # Low lip range from "self.predictor"
        low_lip = shape[56:59]
        
        low_lip = np.concatenate((low_lip, shape[65:68]))
        # print("lowlip",low_lip)
        # Find mean value
        top_mean = np.mean(top_lip, axis=0)
        # print("top_mean",top_mean)
        low_mean = np.mean(low_lip, axis=0)
        # print("low_mean",low_mean)

        # Calculate the lip distance
        distance = abs(top_mean[1] - low_mean[1])
        return distance

    def nose_cheek_distance(self,shape):
        '''
            Method to calculate distance between nose and cheek
        '''
        #Left cheekm
        x_left_cheek = shape.part(2).x
        #Nose
        x_nose = shape.part(30).x
        #Right cheek
        x_right_cheek = shape.part(14).x
        
        d1=abs(x_left_cheek - x_nose)
        d2=abs(x_right_cheek - x_nose)
        return min(d1,d2)

    def side_detection(self,gray,gray_1,profile_cascade,time2,time1,count,font,s_count,f_count,VidCount,alarm_status,alarm,frame):
        faces_1 = self.profile_cascade.detectMultiScale(image=gray, scaleFactor=1.33, minNeighbors=4)
        faces_2 = self.profile_cascade.detectMultiScale(image=gray_1, scaleFactor=1.33, minNeighbors=4)

        for (x, y, w, h) in faces_1:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), thickness=2)

        for (x, y, w, h) in faces_2:
            cv2.rectangle(frame, (450 - x, y), (450 - x - w, y + h), (0, 255, 0), thickness=2)

        # Frame rate
        time_diff = time2 - self.time1

        # Display Frame Rate
        FR = self.count / time_diff
        cv2.putText(frame, "FR: " + str(FR)[:5], (300, 79), font, 0.6, (0, 0, 255))

        if not np.array_equal(faces_1,()) or not np.array_equal(faces_2,()):
            self.s_count = self.s_count + 1

        if np.array_equal(faces_1,()) and np.array_equal(faces_2,()):
            self.f_count = self.f_count + 1

        if self.f_count > 3:
            self.s_count = 0
            self.f_count = 0

        if self.s_count == 60:
            #Defining a video writer object
            VidCap = cv2.VideoWriter('filename'+str(self.VidCount)+'.avi', cv2.VideoWriter_fourcc(*'MJPG'),10,(450,337))
            self.VidCount = self.VidCount + 1
        #distraction timing
        if self.s_count > 5:
            cv2.putText(frame, "DISTRACTION ALERT!", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # if Alarm status is false
            if not self.alarm_status:
                self.alarm_status = True

                # Initiate a thread
                thread1 = Thread(target=self.alarm, args=('Distracted',))
                thread1.deamon = True

                # Start the thread
                thread1.start()
        
            VidCap.write(frame)   



    def alert_msg(self,frame,xface,yface,x1face,y1face,alarm_status,alarm,font,t_text):
        try:
            # Highlight "Drowsy State"
            cv2.rectangle(frame, (xface,yface), (x1face,y1face+20), (0, 255, 0), 2)
            cv2.putText(frame, "Sleepy", (xface, yface-5), font, 0.5, (0, 0, 255))

            # Put text on frame
            cv2.putText(frame, t_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    # Put text on frame
            cv2.putText(frame,t_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # if Alarm status is false
            if not self.alarm_status:
                self.alarm_status = True
                thread1 = Thread(target=self.alarm, args=('wake up sir',))
                thread1.deamon = True
                thread1.start()
        except:
            # Highlight the face
            cv2.rectangle(frame, (xface,yface), (x1face,y1face+20), (0, 255, 0), 2)

    def trigger(self):
        """
            * Find face and calculate EAR, MAR and alert.
        """
        # Define the font
        self.timer1 = time.time()
        thread4 = Thread(target=self.alarm, args=('You are under monitor',))
        # print("You are under monitor",thread4)
        thread4.deamon = True
        #Start the thread
        thread4.start()
        font = cv2.FONT_HERSHEY_TRIPLEX
        while True:
            time2 = time.time() + 0.001
            self.count = self.count + 1
            try:
                # Read the frame from camera
                frame = self.video_stream.read()

                # Resize the frame
                frame = imutils.resize(frame, width=450)
                # Object for gray colour convertion
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray_1 = cv2.flip(gray,1)

                # Find faces from the detector
                faces = self.detector(frame)

                #find no one in frame
                if time.time() - self.timer1 > 120 :
                    self.timer1 = time.time()
                    thread9 = Thread(target=self.alarm, args=('No Face Recongnised',))
                    thread9.deamon = True
                    #Start the thread
                    thread9.start()

                # Iterating through rectangles of detected faces
                for face_roi in faces:

                    self.timer1 = time.time()

                    # Find face co-ordinates from predictor
                    landmark_list = self.predictor(frame, face_roi)
                 

                    # Left eye ratio, Right eye ratio & Eye open ratio
                    left_eye_ratio = self.eye_aspect_ratio([36, 37, 38, 39, 40, 41], landmark_list)
                    right_eye_ratio = self.eye_aspect_ratio([42, 43, 44, 45, 46, 47], landmark_list)
                    eye_open_ratio = (left_eye_ratio + right_eye_ratio) / 2

                    # Put eye ratio value on frame
                    cv2.putText(frame, "EAR : "+str(eye_open_ratio)[:5], (300, 13), font, 0.6, (0, 0, 255))

                    # Normalize the predicted shape
                    shape = face_utils.shape_to_np(landmark_list)

                    #print("shape\n",shape)

                    # Draw on our image, all the finded cordinate points (x,y) 
                    #draw all  68 point facial unwanted
                    for (x, y) in shape:
                        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

                    # Call "nose_cheek_distance"
                    nc_distance = self.nose_cheek_distance(landmark_list)

                    #Frame rate
                    time_diff = time2 - self.time1

                    # Call "lip_distance" function
                    distance = self.lip_distance(shape)

                    # Put lip distance value on frame
                    cv2.putText(frame, "MAR : "+str(distance)[:5], (300, 35), font, 0.6, (0, 0, 255))

                    # Nose_Cheek distance on frame
                    cv2.putText(frame, "NTC: "+str(nc_distance)[:5], (300, 57), font, 0.6, (0, 0, 255))

                    # Display Frame Rate
                    FR=self.count/time_diff
                    cv2.putText(frame, "FR: "+str(FR)[:5], (300, 79), font, 0.6, (0, 0, 255))

                    # If distance between EYE & MOUTH & NTC increasing on threshold values
                    if distance > self.yawn_thresh:
                        self.yawn_count +=1
                    else:
                        self.yawn_count = 0

                    if eye_open_ratio > self.eye_thresh:
                        self.eye_count +=1
                    else:
                        self.eye_count = 0

                    if nc_distance < self.NTC_thresh:
                        self.NTC_count +=1
                        
                    else:
                        self.NTC_count = 0


                    # Left & Top Eye Corner
                    xface,yface = face_roi.left(), face_roi.top()
                    
                    # Right & Bottom Eye Corner
                    x1face,y1face = face_roi.right(), face_roi.bottom()

                    #cv2.rectangle(frame, (xface,yface), (x1face,y1face+20), (255, 255, 255), 2)

                    # Consecutive frames
                    if self.eye_count>10:
                        self.alert_msg(frame,xface,yface,x1face,y1face,self.alarm_status,self.alarm,font,"DROWSINESS ALERT!")

                    if self.yawn_count>10:
                        self.alert_msg(frame,xface,yface,x1face,y1face,self.alarm_status,self.alarm,font,"YAWN ALERT!")


                    if self.NTC_count == 100:
                        #Defining a video writer object
                        VidCap = cv2.VideoWriter('filename'+str(self.VidCount)+'.avi', cv2.VideoWriter_fourcc(*'MJPG'),10,(450,337))
                        self.VidCount = self.VidCount + 1

                    if self.NTC_count > 100:
                        # Highlight "Distraction State"
                        cv2.rectangle(frame, (xface,yface), (x1face,y1face+20), (0, 255, 0), 2)
                        cv2.putText(frame, "Distracted", (xface, yface-5), font, 0.5, (0, 0, 255))

                        # Put text on frame
                        cv2.putText(frame, "DISTRACTION ALERT!", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                        # Storing video
                        VidCap.write(frame)

                        # if Alarm status is false
                        if not self.alarm_status:
                            self.alarm_status = True

                            # Initiate a thread
                            thread1 = Thread(target=self.alarm, args=('Distracted',))
                            thread1.deamon = True

                            # Start the thread
                            thread1.start()
                    else:
                        # Highlight the face
                        cv2.rectangle(frame, (xface,yface), (x1face,y1face+20), (0, 255, 0), 2)

                # Detecting side faces
                if np.array_equal(tuple(faces),()) == True:
                    #print("np.array_equal(tuple(faces),())",np.array_equal(tuple(faces),()))
                    if np.array_equal(tuple(faces),()):
                        self.side_detection(gray,gray_1,self.profile_cascade,time2,self.time1,self.count,font,self.s_count,self.f_count,self.VidCount,self.alarm_status,self.alarm,frame)

                    
                if np.array_equal(tuple(faces),()):
                    self.c_count = self.c_count + 1

                if self.c_count > 20:
                    self.s_count = 0
                    self.c_count = 0

                # Show the frame
                cv2.imshow("img", frame)
                #cv2.imwrite("img.jpg", frame)

                # if the `esc` key was pressed, break from the loop
                key = cv2.waitKey(1)
                if key == 27:
                    thread2 = Thread(target=self.alarm, args=('drowsiness aborted',))
                    thread2.deamon = True
                    #Start the thread
                    thread2.start()
                    break
            except Exception:
                pass

        # self.cap.release()
        cv2.destroyAllWindows()
        # Stop the Video Stream
        self.video_stream.stop()

if __name__ == '__main__':
    OBJ = Drowsinees()

exit()
