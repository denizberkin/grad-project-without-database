import os
import threading
import tkinter as tk

import numpy as np
import cv2
from functools import partial
from PIL import ImageTk, Image

from ai.utils import object_detection
from communication.serialcomm import move_motor, scanning_procedure, tray_procedure, calibration_procedure, autofocus
from firebase.databasev2 import Firestore
from gui.pages import MODEL_PATH, STEP_SIZE, MIN_STEPS, MAX_STEPS, MICRO_DELAY, CAPTURE

from ai import utils
from tkinter import BOTH, LEFT, BOTTOM, RIGHT, X, TOP

# to avoid circular import, TYPE_CHECKING is always False.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mainapp import App


class ScanPage(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: 'App'):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.configure(bg=controller.widget_params["bg"])

        self.is_scanning = False
        # widgets
        self.scan_button_frame = ScanButtonFrame(self)
        self.cam_frame = ScanCamFrame(self)

        # display widgets
        self.cam_frame.pack(side=TOP, fill=BOTH, expand=1, padx=20, pady=20)
        self.scan_button_frame.pack(side=BOTTOM, fill=X, expand=True, padx=10)

    def show_homepage(self):
        self.pack_forget()
        self.cam_frame.stop_camera_stream()
        self.controller.title("Homepage")
        self.controller.show_page(self.controller.home_page)

    def show_patient_page(self):
        self.pack_forget()
        self.cam_frame.stop_camera_stream()
        self.controller.show_page(self.controller.patient_info_page, "- Patient Information")

    def show(self, *args):
        self.controller.title("Scan " + args[0] if args else "")
        self.pack(fill=BOTH, expand=True)
        self.cam_frame.start_camera_stream()


class ScanButtonFrame(tk.Frame):
    def __init__(self, parent: ScanPage):
        super().__init__(parent, bg=parent.controller.widget_params["bg"])
        self.parent = parent
        self.arduino = parent.controller.arduino

        path = os.path.join(os.path.dirname(__file__), "..", "..", MODEL_PATH)
        self.model = utils.load_model(path)
        self.database = Firestore()

        self.patient_information_frame = parent.controller.patient_info_page.patient_information_frame
        self.back_button = tk.Button(self, text="Back", command=self.parent.show_homepage,
                                     **self.parent.controller.widget_params)
        self.scan_button = tk.Button(self, text="Start Scanning", command=self.scanning,
                                     **self.parent.controller.widget_params)

        self.predict_button = tk.Button(self, text="Predict", command=self.prediction_start,
                                        **self.parent.controller.widget_params)
        self.widget_params = parent.controller.widget_params.copy()
        self.widget_params.update({"font": ("Helvetica", 10, "bold")})

        self.x_plus = tk.Button(self, text="x+", command=partial(self._raise, "X"),
                                **self.widget_params)
        self.x_minus = tk.Button(self, text="x-", command=partial(self._lower, "X"),
                                 **self.widget_params)
        self.y_plus = tk.Button(self, text="y+", command=partial(self._raise, "Y"),
                                **self.widget_params)
        self.y_minus = tk.Button(self, text="y-", command=partial(self._lower, "Y"),
                                 **self.widget_params)
        self.z_plus = tk.Button(self, text="z+", command=partial(self._raise_z, "Z"),
                                **self.widget_params)
        self.z_minus = tk.Button(self, text="z-", command=partial(self._lower_z, "Z"),
                                 **self.widget_params)

        self.back_button.pack(side=LEFT, padx=10)
        self.scan_button.pack(side=RIGHT, padx=10)
        self.x_minus.pack(side=LEFT, padx=10)
        self.x_plus.pack(side=LEFT, padx=10)
        self.y_minus.pack(side=LEFT, padx=10)
        self.y_plus.pack(side=LEFT, padx=10)
        self.z_minus.pack(side=LEFT, padx=10)
        self.z_plus.pack(side=LEFT, padx=10)

    def _raise(self, direction: str):
        move_motor_thread = threading.Thread(target=move_motor,
                                             args=(self.arduino, STEP_SIZE, direction, MICRO_DELAY * 2))
        move_motor_thread.start()

    def _lower(self, direction: str):
        move_motor_thread = threading.Thread(target=move_motor,
                                             args=(self.arduino, -STEP_SIZE, direction, MICRO_DELAY * 2))
        move_motor_thread.start()

    def _raise_z(self, direction: str):
        move_motor_thread = threading.Thread(target=move_motor,
                                             args=(self.arduino, -STEP_SIZE * 16, direction, MICRO_DELAY * .005))
        move_motor_thread.start()

    def _lower_z(self, direction: str):
        move_motor_thread = threading.Thread(target=move_motor,
                                             args=(self.arduino, STEP_SIZE * 16, direction, MICRO_DELAY * .005))
        move_motor_thread.start()

    def scanning(self):
        slide_indexes = []
        for idx, (checkbutton_label, checkbutton_id) in enumerate(self.patient_information_frame.get_patient_checkbutton_info()):
            if checkbutton_label:
                slide_indexes.append((idx, checkbutton_id))

        print(slide_indexes)
        self.unpack_buttons()
        self.parent.cam_frame.start_scanning_procedure(slide_indexes)

    def prediction_start(self):
        predict_thread = threading.Thread(target=self.predict)
        predict_thread.start()

    def predict(self):
        predictions = object_detection("images/scanned_images", "images/predicted")
        print("Got predictions!")
        bn = list()
        for i, pred in enumerate(predictions):
            print(pred)
            try:
                self.database.create_document(pred)
            except Exception as e:
                bn.append(i)
        print("Pushed to database!")
        self.pack_buttons()

    def unpack_buttons(self):
        self.back_button.pack_forget()
        self.scan_button.pack_forget()
        self.x_minus.pack_forget()
        self.x_plus.pack_forget()
        self.y_minus.pack_forget()
        self.y_plus.pack_forget()
        self.z_minus.pack_forget()
        self.z_plus.pack_forget()

    def pack_buttons(self):
        self.back_button.pack(side=LEFT, padx=10)
        self.x_minus.pack(side=LEFT, padx=10)
        self.x_plus.pack(side=LEFT, padx=10)
        self.y_minus.pack(side=LEFT, padx=10)
        self.y_plus.pack(side=LEFT, padx=10)
        self.z_minus.pack(side=LEFT, padx=10)
        self.z_plus.pack(side=LEFT, padx=10)
        self.scan_button.pack(side=RIGHT, padx=10)
        self.predict_button.pack_forget()


class ScanCamFrame(tk.Frame):
    def __init__(self, parent: ScanPage):
        super().__init__(parent, bg=parent.controller.widget_params["bg"])
        self.parent = parent
        self.button_frame = parent.scan_button_frame

        self.frame: np.ndarray = np.ndarray([])
        self.cap = CAPTURE

        # camera and arduino
        self.arduino = parent.controller.arduino
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

    def start_auto_focus(self):
        start_focus = threading.Thread(target=autofocus, args=(self, self.arduino, STEP_SIZE * 64, MIN_STEPS, MAX_STEPS))
        start_focus.start()
        # start_focus.join()

    def start_scanning_procedure(self, slide_indexes):
        start_scanning = threading.Thread(target=scanning_procedure, args=(self, self.arduino, slide_indexes, STEP_SIZE, MIN_STEPS, MAX_STEPS,))
        # start_scanning.start()
        self.check_scanning_status(start_scanning)

        # scanning_procedure(self, self.arduino, slide_indexes, STEP_SIZE, MIN_STEPS, MAX_STEPS)

    def check_scanning_status(self, thread):
        if thread.is_alive():
            self.after(500, self.check_scanning_status, thread)
        else:
            print("is not alive")
            self.button_frame.predict_button.pack_forget()
            self.button_frame.pack_buttons()


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
