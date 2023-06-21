import os
import threading
import time
import tkinter as tk

from tkinter import BOTH, BOTTOM, X, LEFT, TOP

import numpy as np
import cv2
from PIL import ImageTk, Image

# to avoid circular import, TYPE_CHECKING is always False.
from typing import TYPE_CHECKING

from communication.serialcomm import calibration_procedure
from gui.pages import CAPTURE

if TYPE_CHECKING:
    from mainapp import App


class AutoCalibrationPage(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: 'App'):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.arduino = self.controller.arduino

        self.configure(bg=controller.widget_params["bg"])

        # widgets
        # create two buttons with the same visuals as the homepage
        self.button_frame = tk.Frame(self, bg=self.controller.widget_params["bg"])
        self.back_button = tk.Button(self.button_frame, text="Back to Menu", command=self.show_homepage,
                                     **self.controller.widget_params)
        self.start_auto_calibration_button = tk.Button(self.button_frame, text="Start Calibration",
                                                       command=self.start_auto_calibration,
                                                       **self.controller.widget_params)
        self.cam_frame = AutoCamFrame(self)

        # place the buttons in the bottom center of the page
        self.button_frame.pack(side=BOTTOM, fill=X, expand=True, padx=10, pady=10)
        self.back_button.pack(side=LEFT, padx=10, pady=10)
        self.start_auto_calibration_button.pack(side=LEFT, padx=10, pady=10)
        self.cam_frame.pack(fill=BOTH, expand=True)
        # place the listbox in the center of the page

    def start_auto_calibration(self):
        start_calibration = threading.Thread(target=calibration_procedure, args=(self.arduino,))
        start_calibration.start()

    def show_homepage(self):
        self.pack_forget()
        self.cam_frame.stop_camera_stream()
        self.controller.title("Homepage")
        self.controller.show_page(self.controller.home_page)

    def show(self):
        self.controller.title("Auto Calibration")
        self.pack(fill=BOTH, expand=True)
        self.cam_frame.start_camera_stream()


class AutoCamFrame(tk.Frame):
    def __init__(self, parent: AutoCalibrationPage):
        super().__init__(parent, bg=parent.controller.widget_params["bg"])
        self.parent = parent

        self.frame = np.ndarray([])
        self.cap = CAPTURE

        # camera and arduino
        self.arduino = parent.arduino

        try:
            self.cam_height, self.cam_width, _ = self.cap.read()[1].shape
        except AttributeError:
            self.cam_height, self.cam_width = 480, 320

        self.camera_stream = None
        self.is_running = False

        self.canvas = tk.Canvas(self, bg=parent.controller.widget_params["bg"])
        self.canvas.config(width=507, height=380)
        self.canvas.pack(side=TOP)

    def start_camera_stream(self):
        self.is_running = True
        self.camera_stream = threading.Thread(
            target=self.get_stream)
        self.camera_stream.start()

    def stop_camera_stream(self):
        self.is_running = False
        self.canvas.photo = None

    def get_frame(self):
        return self.frame

    def get_stream(self):
        # set up a loop to continuously read frames from the camera and display them in the canvas
        while self.is_running:
            ret, self.frame = self.cap.read()
            if not ret:
                break
            # convert the OpenCV BGR format to RGB
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

            # print(self.frame.shape)
            # _, _ = utils.img_forward(self.model, frame)
            self.frame = np.transpose(self.frame, (1, 0, 2))
            self.frame = np.flip(self.frame, 0)
            # print("scan frame: ", self.frame.shape)

            # resize the frame to fit the canvas
            canvas_img = cv2.resize(self.frame, (self.canvas.winfo_width(), self.canvas.winfo_height()))
            canvas_img = np.uint8(canvas_img)
            # print(canvas_img.shape)
            photo = ImageTk.PhotoImage(image=Image.fromarray(canvas_img))
            self.canvas.create_image(0, 0, anchor="nw", image=photo)
            self.canvas.photo = photo
            self.canvas.update()
            # time.sleep(1 / DETECTION_FPS)
