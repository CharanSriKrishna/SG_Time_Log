# Copyright (c) 2020 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
import ctypes
from threading import Thread
import time
from datetime import datetime, timedelta
import sys

sys.path.append('PATH_TO_PYNPUT_MODULE')
from pynput import keyboard, mouse

HookClass = sgtk.get_hook_baseclass()


class TimeLoger(HookClass):
    """
    Hook called to perform an operation with the
    current scene
    """

    def execute(
        self,
        operation,
        context,
        app,
        **kwargs
    ):
        """
        Main hook entry point

        :param operation:       String
                                Scene operation to perform

        :param context:         Context
                                The context the file operation is being
                                performed in.
        
        :param app:             App
                                The App bundle that is running this code    

        :returns:               None
        """

        if operation == "start_timer":
            app.time_thread = time_loger_data(app, context)
        elif operation == "save_timer":
            app.time_thread.save_timer()

# Define the softwares here 
software = ["maya","nuke"]

class time_loger_data():
    """
    Class to for the time log it has all necessary functions and variables to calculate the time log
    """
    def __init__(self, app, context):
        """
        :param context:         Context
                                The context the file operation is being
                                performed in.
        
        :param app:             App
                                The App bundle that is running this code 
        """

        self.app = app
        # get task and project from context
        self.task_id = int(context.task['id']) 
        self.project_id = int(context.project['id'])

        # setting up the variables related to time 
        self.start_time = datetime.now()            # time log start time 
        self.last_movement = datetime.now()         # time of last movement
        self.total_time = self.set_time()           # total time the task was open 
        self.idle_time = self.set_time()            # the amount of time spent idle
        self.idle_limit = self.set_time(minutes=5)  # idle time limit 

        self.sg_timer_id = None
        self.start_timer_sg()

        # setting up variables to store the window details 
        self.window_name = None                     # the name of the window the task is done 
        self.same_window = True                     # boolean indicating if the current window same as the main window

        # Thread that is running to check the active window
        self.window_thread = Thread(target = self.check_window_with_interval)
        self.window_thread.start()

        # defining mouse and keyboard listeners
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        self.mouse_listener.start()
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press
        )
        self.keyboard_listener.start()

    def start_timer_sg(self):
        """
        Function to add the log to shotgrid (flow production tracking)
        """
        # creating time log data
        sg = self.app.shotgun
        data = {
                "project": {"type": "Project", "id": self.project_id},
                "code":"timelog",
                "sg_start_time": self.start_time,
                }
        self.sg_timer_id = sg.create('CustomEntity07', data)
        # linking the task 
        data = {
            "sg_time_log":[self.sg_timer_id]
        }
        sg.update("Task", self.task_id, data, {'sg_time_log': 'add'})
        
    def set_time(self, days=0, hours=0, minutes=0, seconds=0):
        """
        Function to create a time varible 
        """
        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    def find_window(self):
        """
        Function to find the current active window 
        """
        GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        hwnd = GetForegroundWindow()
        length = GetWindowTextLength(hwnd) + 1
        buffer = ctypes.create_unicode_buffer(length)
        GetWindowText(hwnd, buffer, length)
        title = buffer.value
        values = title.strip().split(' - ')
        window_title = values[-1].strip().lower()
        for i in software:
            if i in window_title:
                return i 
            else:
                return "Unknown"
            
    def update_timer_sg(self, end_time):
        """
        Function to update the log in shotgrid (flow production tracking)
        """
        sg = self.app.shotgun
        data = {
            "sg_end_time": end_time,
            "sg_total_time":float((end_time - self.start_time).total_seconds()/60),
            "sg_productive_time":float(self.total_time.total_seconds()/60),
        }
        sg.update("CustomEntity07", self.sg_timer_id['id'], data)

    # redefined keyboard and mouse listeners to calculate time log 
    def on_press(self, key):
        self.calculate_idle_time()
        # check if "Ctrl + S" is presed then update to Shotgrid
        if key == keyboard.KeyCode.from_char('\x13'):
            self.save_timer()

    def on_click(self, x, y, button, pressed):
        self.calculate_idle_time()

    def on_scroll(self, x, y, dx, dy):
        self.calculate_idle_time()

    def calculate_idle_time(self):
        """
        Function to calculate the idle time 
        """
        now = datetime.now()
        cur_time = now - self.last_movement
        if cur_time > self.idle_limit or not self.same_window:
            self.idle_time += cur_time
        self.last_movement = now

    def check_window_with_interval(self):
        """
        Function to continue checking the active window with regular intervals 
        """
        time.sleep(5)
        self.window_name = self.find_window()
        while True:
            time.sleep(60)
            cur_window = self.find_window()
            if cur_window == self.window_name:
                self.same_window = True
            else:
                self.same_window = False

    def calculate_effective_time(self, endtime):
        """
        Function to calculate the effective time spent 
        """
        total_time = endtime - self.start_time
        self.total_time = total_time - self.idle_time

    def save_timer(self):
        """
        Function to update the time log details to Shotgrid   
        """
        end_time = datetime.now()
        self.calculate_idle_time()
        self.calculate_effective_time(end_time)
        print(self.start_time, end_time, self.total_time)
        self.update_timer_sg(end_time)