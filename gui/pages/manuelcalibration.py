import os
import threading
import tkinter as tk

import numpy as np
import cv2
from functools import partial
from PIL import ImageTk, Image

import ai.utils as utils
from gui.pages import MODEL_PATH, STEP_SIZE, MICRO_DELAY, CAPTURE, MIN_STEPS, MAX_STEPS
from communication.serialcomm import move_motor, autofocus

from tkinter import BOTH, LEFT, BOTTOM, RIGHT, X, TOP

# to avoid circular import, TYPE_CHECKING is always False.
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from mainapp import App


class ManualCalibration(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: 'App'):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.configure(bg=self.controller.widget_params["bg"])

        path = os.path.join(os.getcwd(), MODEL_PATH)
        self.model = utils.load_model(path)

        # create widgets
        self.cam_frame = ManualCamFrame(self)
        self.position_button_frame = PositionButtonFrame(self)

        # display widgets
        self.cam_frame.pack(side=TOP, fill=BOTH, expand=1, padx=20, pady=20)
        self.position_button_frame.pack(side=BOTTOM, fill=X, padx=50, pady=10)

    def show(self):
        self.controller.title("Manual Calibration")
        self.pack(fill=BOTH, expand=True)
        self.cam_frame.start_camera_stream()

    def back_to_menu(self):
        if self.cam_frame.is_running:
            self.cam_frame.stop_camera_stream()
        self.pack_forget()
        self.controller.show_page(self.controller.home_page)


class PositionButtonFrame(tk.Frame):
    def __init__(self, parent: ManualCalibration):
        super().__init__(parent, bg=parent.controller.widget_params["bg"])
        self.parent = parent
        self.arduino = parent.controller.arduino

        self.widget_params = parent.controller.widget_params.copy()
        self.widget_params.update({"font": ("Helvetica", 9, "bold")})

        # create a screenshot button next to the camera button.
        self.autofocus_button = tk.Button(self, text="Autofocus", command=self.start_autofocus,
                                          **self.widget_params)
        self.x_plus = tk.Button(self, text="x+", command=partial(self._raise_x, "X"),
                                **self.widget_params)
        self.x_minus = tk.Button(self, text="x-", command=partial(self._lower_x, "X"),
                                 **self.widget_params)
        self.y_plus = tk.Button(self, text="y+", command=partial(self._raise_y, "Y"),
                                **self.widget_params)
        self.y_minus = tk.Button(self, text="y-", command=partial(self._lower_y, "Y"),
                                 **self.widget_params)
        self.z_plus = tk.Button(self, text="z+", command=partial(self._raise_z, "Z"),
                                **self.widget_params)
        self.z_minus = tk.Button(self, text="z-", command=partial(self._lower_z, "Z"),
                                 **self.widget_params)
        self.back_button = self.back_button = tk.Button(self, text="Back", command=parent.back_to_menu,
                                                        **self.widget_params)

        self.back_button.pack(side=LEFT, padx=10)
        self.autofocus_button.pack(side=RIGHT, padx=10)
        self.z_minus.pack(side=RIGHT, padx=10)
        self.z_plus.pack(side=RIGHT, padx=10)
        self.y_plus.pack(side=RIGHT, padx=10)
        self.y_minus.pack(side=RIGHT, padx=10)
        self.x_plus.pack(side=RIGHT, padx=10)
        self.x_minus.pack(side=RIGHT, padx=10)

    def _raise_x(self, direction: str):
        move_motor_thread = threading.Thread(target=move_motor,
                                             args=(self.arduino, 4 * STEP_SIZE, direction, MICRO_DELAY * 1.2))
        move_motor_thread.start()

    def _lower_x(self, direction: str):
        move_motor_thread = threading.Thread(target=move_motor,
                                             args=(self.arduino, -4 * STEP_SIZE, direction, MICRO_DELAY * 1.2))
        move_motor_thread.start()

    def _raise_y(self, direction: str):
        move_motor_thread = threading.Thread(target=move_motor,
                                             args=(self.arduino, 5 * STEP_SIZE, direction, MICRO_DELAY * 1.2))
        move_motor_thread.start()

    def _lower_y(self, direction: str):
        move_motor_thread = threading.Thread(target=move_motor,
                                             args=(self.arduino, -5 * STEP_SIZE, direction, MICRO_DELAY * 1.2))
        move_motor_thread.start()

    def _raise_z(self, direction: str):
        move_motor_thread = threading.Thread(target=move_motor,
                                             args=(self.arduino, -STEP_SIZE * 16, direction, MICRO_DELAY * .005))
        move_motor_thread.start()

    def _lower_z(self, direction: str):
        move_motor_thread = threading.Thread(target=move_motor,
                                             args=(self.arduino, STEP_SIZE * 16, direction, MICRO_DELAY * .005))
        move_motor_thread.start()

    def start_autofocus(self):
        start_focus = threading.Thread(target=autofocus, args=(self.parent.cam_frame, self.arduino, STEP_SIZE * 16, MIN_STEPS, MAX_STEPS,))
        start_focus.start()


class ManualCamFrame(tk.Frame):
    def __init__(self, parent: ManualCalibration):
        super().__init__(parent, bg=parent.controller.widget_params["bg"])
        self.parent = parent

        # camera settings
        self.frame: np.ndarray = np.ndarray([])
        self.cap = CAPTURE
        try:
            self.cam_height, self.cam_width, _ = self.cap.read()[1].shape
        except AttributeError:
            self.cam_height, self.cam_width = 480, 320

        self.camera_stream = None
        self.is_running = False

        self.widget_params = parent.controller.widget_params.copy()
        self.widget_params.update({"font": ("Helvetica", 9, "bold")})

        self.canvas = tk.Canvas(self, bg=parent.controller.widget_params["bg"])
        self.canvas.config(width=507, height=380)
        self.ss_button = tk.Button(self, text="SS", command=self.take_screenshot,
                                   **self.widget_params)

        self.canvas.pack(side=LEFT, padx=10)
        self.ss_button.pack(side=RIGHT, padx=10)

    def take_screenshot(self):
        if not os.path.exists(f"images/test"):
            os.makedirs(f"images/test")
        im_index = 0
        while os.path.exists(f"images/test/{im_index}.png"):
            im_index += 1
        cv2.imwrite(f"images/test/{im_index}.png", self.get_frame())

    def start_camera_stream(self):
        self.is_running = True
        self.camera_stream = threading.Thread(
            target=self.get_stream)
        self.camera_stream.start()

    def stop_camera_stream(self):
        # set the camera stream object to None
        self.is_running = False
        self.canvas.photo = None

    def get_stream(self):
        # set up a loop to continuously read frames from the camera and display them in the canvas
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                break

            # convert the OpenCV BGR format to RGB
            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.transpose(self.frame, (1, 0, 2))
            frame = np.flip(frame, 0)
            # _, _ = utils.img_forward(self.model, frame)
            # resize the frame to fit the canvas
            canvas_img = cv2.resize(frame, (self.canvas.winfo_width(), self.canvas.winfo_height()))
            canvas_img = np.uint8(canvas_img)
            # print(canvas_img.shape)
            photo = ImageTk.PhotoImage(image=Image.fromarray(canvas_img))
            self.canvas.create_image(0, 0, anchor="nw", image=photo)
            self.canvas.photo = photo
            self.canvas.update()
            # time.sleep(1 / FPS)

    def get_frame(self):
        return self.frame
