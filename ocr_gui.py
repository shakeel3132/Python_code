# -*- coding: utf-8 -*-
# pylint: disable=no-member

##############################################################################
###    Module to trigger GUI and capture the video frame and find text.   ###
##############################################################################

"""

Created on Fri Aug  27 11:40:31 2021

@author          : Aravind Pandi S (aravind.pandi@mind-infotech.com)
* title          : ocr_gui.py
* description    : This module will trigger GUI and access video capture using
                   python.
* version        : v0.1
* revision_notes : 0.1 (Aravind Pandi S, Created GUI & sniffed video frames)
* file
  dependencies   : filter_text.py
* module
  dependencies   : os, tkinter, cv2 (open-cv), PIL (Pillow), threading, queue,
                   numpy.
* python_version : 3.9.6

"""

import os
import shutil
import tkinter
from tkinter import Label, Text, END, font
import time
import threading
from threading import Thread
from queue import Queue
import cv2
import PIL.Image
import PIL.ImageTk
import filter_text

# import train_datasets

class App:
    """
        * GUI Class.
    """
    def __init__(self, window, window_title, video_source=0):

        self.take_snap = 0
        self.video_source = video_source
        self.time_stamp = None
        self.but_name = None
        self.box_var = 0

        self.window = window
        self.window.title(window_title)
        self.window.geometry("1000x550+120+50")
        self.window.configure(bg='#232023')
        self.window.resizable(0,0)


        # Queue to pass & validate image
        self.req_queue = Queue(maxsize=0)

        # Queue to get result for validated image
        self.res_queue = Queue(maxsize=0)

        # Event
        self.validate_event = threading.Event()

        # Object for filter_text.py
        self.txt_obj = filter_text.Ocr(self)


        # Button Font
        self.button_font = font.Font(family='Cornerstone', size=10, \
                                    weight='bold')


        self.play_but = tkinter.Button(window, text="Play Text", width=15,\
                    bg='#FF8C00', activebackground="#FFA500",\
                        font=self.button_font, \
                            command=self.txt_obj.speaker_func)


        self.play_but.place(x=670, y=510)
        #self.play_but.config(state="disabled")

        # Verify images thread
        self.verify_thread = Thread(target=self.txt_obj.verify_image,\
                                    args=(self.req_queue, self.res_queue, \
                                    self.validate_event))
        self.verify_thread.start()

        # Employee details thread
        self.details = Thread(target=(self.employee_details))

        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(window, highlightthickness=1,\
                      highlightbackground="black", width = self.vid.width,\
                      height = self.vid.height)
        self.canvas.pack(anchor=tkinter.SW)


        # Get Text Button that lets the user take a snapshot
        self.log_out=tkinter.Button(window, text="Get Text", width=15,\
                    bg='#FF8C00', activebackground="#FFA500",\
                        font=self.button_font, \
                            command=lambda: self.snapshot("Log-Out"))
        self.log_out.place(x=512, y=510)
        self.log_out.config(state="normal")

        employee = Label(window, text = "TEXT BOARD", font='Cornerstone 12 bold',\
                    bg='#232023', fg='blue')
        employee.place(x=765, y=20)

        # Text widget

        self.textbox = Text(window, height=20, width=37)
        self.textbox.place(x=670, y=157)

        # image = PIL.Image.open(r'temp\play.png')

        # # Reszie the image using resize() method
        # resize_image = image.resize((30, 30))

        # self.speaker = PhotoImage(file=resize_image)
        # self.speaker.resize((30, 30))
        # self.speaker_but = tkinter.Button(window, image=resize_image, \
        #                                   command=self.txt_obj.speaker_func)


        self.details.start()

        # After it is called once, the update method will be automatically
        # called every delay milliseconds
        self.delay = 5
        self.update()

        self.label = None

        window.protocol('WM_DELETE_WINDOW', self.flush)
        window.mainloop()

    def snapshot(self, login_type):

        """
            * When Log-In or Log-Out button pressed
              this function would be called.
        """

        # print(time.strftime("%Y-%m-%d-%H-%M-%S"))
        self.log_out.config(state="disabled")
        #self.play_but.config(state="disabled")
        self.txt_obj.say_txt = ""
        if self.label:
            self.label.destroy()
        self.but_name = login_type
        self.textbox.delete("1.0", END)
        self.take_snap = 1
        # Get a frame from the video source
        ret, frame = self.vid.get_frame(self.take_snap)

        if ret:
            self.time_stamp = time.strftime("%Y-%m-%d-%H:%M:%S")
            cv2.imwrite("Images/frame" + ".jpg", \
                        cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            # img = PIL.Image.fromarray()
            self.req_queue.put((r"Images/frame" + ".jpg", self.but_name, \
                                self.time_stamp))
        self.take_snap = 0

    def employee_details(self):

        """
            * To enter details into Employee board.
        """

        while not self.validate_event.isSet():
            if not self.res_queue.empty():
                self.play_but.config(state="normal")
                index = 1.0
                self.textbox.delete(index, END)
                # self.textbox1 = Text(self.window, height=10, width=37)
                value = self.res_queue.get() # tuple
                # Read the Image
                image = PIL.Image.open(r"Images\frame" + ".jpg")

                # Reszie the image using resize() method
                resize_image = image.resize((150, 100))
                img = PIL.ImageTk.PhotoImage(image=resize_image)

                # create label and add resize image
                self.label = Label(image=img)
                self.label.image = img
                self.label.place(x=742, y=45)
                for data in value:
                    index = index+1
                    self.textbox.insert(index, " "+data+"\n")

                print(time.strftime("%Y-%m-%d-%H-%M-%S"))
                self.log_out.config(state="normal")

            else:
                time.sleep(0.2)


    def update(self):

        """
            * To show the video frame from the camera continously.
        """
        # print("Update")
        # Get a frame from the video source
        ret, frame = self.vid.get_frame(self.take_snap)

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = \
                                                PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, \
                                     anchor = tkinter.NW)

        self.window.after(self.delay, self.update)


    def flush(self):

        """
            * Function to handle when GUI close button pressed.
        """

        self.validate_event.set()

        if self.details.is_alive():
            self.details.join()

        if self.verify_thread.is_alive():
            self.verify_thread.join()

        shutil.rmtree("Images")
        os.mkdir("Images")

        self.vid.__del__()
        self.window.destroy()


class MyVideoCapture():
    """
        * Video Capture Class.
    """
    def __init__(self, video_source=0):

        # Open the video source
        self.vid = cv2.VideoCapture(video_source, cv2.CAP_DSHOW)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)


    def get_frame(self, take_snap):

        """
            * Function to handle each frame in camera.
        """

        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                ret, frame = self.vid.read()
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (None, None)
        else:
            return (None, None)

    # Release the video source when the object is destroyed
    def __del__(self):

        """
            * Function to delete the video source object.
        """

        if self.vid.isOpened():
            self.vid.release()

# Create a window and pass it to the Application object
App(tkinter.Tk(), "Textract")
