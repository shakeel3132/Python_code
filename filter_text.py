# -*- coding: utf-8 -*-
##############################################################################
###               Module to find text from video frame.                    ###
##############################################################################

"""

Created on Fri Aug  27 11:50:12 2021

@author          : Aravind Pandi S (aravind.pandi@mind-infotech.com)
* title          : filter_text.py
* description    : This module will find text on frame from video capture using
                   python.
* version        : v0.1
* revision_notes : 0.1 (Aravind Pandi S, Implemented Text recognition)
* file
  dependencies   : filter_text.py
* module
  dependencies   : time.
* python_version : 3.9.6

"""

import time
import pyttsx3
import ctypes

class Ocr:
    """
        * Class to Filter Text.
    """
    def __init__(self, main_obj):
        print(main_obj)
        self.main_obj = main_obj
        self.results = ""
        self.engine = pyttsx3.init()
        self.say_txt = ""
        self.speack_flag = False
        # self.voices = self.engine.getProperty('voices')
        # self.engine.setProperty('voice', self.voices.id)


    def verify_image(self, req_queue, res_queue, val_event):
        """
            * Get image and find text.
        """
        # print(time.strftime("%Y-%m-%d-%H-%M-%S"))
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False)
        self.main_obj.log_out.config(state="normal")
        
        # print(time.strftime("%Y-%m-%d-%H-%M-%S"))
        while not val_event.isSet():
            if not req_queue.empty():
                datas = req_queue.get(block=False)
                self.results = reader.readtext(datas[0], detail = 0, \
                                               paragraph=False)
                print(self.results)
                self.speack_flag = True
                if self.results:
                    self.say_txt = self.results
                    res_queue.put(self.results)
                    ctypes.windll.user32.MessageBoxW(0, self.results[0], "Text", 1)
                else:
                    self.say_txt = ["No Text Found"]
                    res_queue.put(["\n\t    No Text Found"])
            else:
                time.sleep(0.2)

    def speaker_func(self):
        """
            * Loud out the text extracted from Image.
        """
        
        if self.speack_flag is True:
            print(self.say_txt)
            self.main_obj.play_but.config(state="disabled")
            if self.say_txt:
                for txt in self.say_txt:
                    self.engine.say(txt)
            self.engine.runAndWait()
            self.main_obj.play_but.config(state="normal")
            self.speack_flag = False
        else:
            self.main_obj.play_but.config(state="disabled")
            self.say_txt = self.main_obj.textbox.get(1.0, "end-1c")
            pyttsx3.speak(self.say_txt)
            self.main_obj.play_but.config(state="normal")
            self.speack_flag = False


        
