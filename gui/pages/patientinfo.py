import subprocess
import tkinter as tk
import threading
from functools import partial
from tkinter import BOTH, LEFT, TOP, BOTTOM, RIGHT, X, CENTER
from communication.serialcomm import tray_procedure, calibration_procedure
# to avoid circular import, TYPE_CHECKING is always False.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mainapp import App


class PatientInfoPage(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: 'App'):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.arduino = controller.arduino

        self.configure(bg=controller.widget_params["bg"])
        # variables
        self.patient_info = {}
        # widgets
        self.patient_information_frame = PatientInformationFrame(self)
        self.button_frame = tk.Frame(self, bg=controller.widget_params["bg"])
        self.back_button = tk.Button(self.button_frame, text="Back to Menu", command=self.show_homepage,
                                     **controller.widget_params)
        self.start_scan_button = tk.Button(self.button_frame, text="Next - Scan Page", command=self.show_scan_page,
                                           **controller.widget_params)

        self.tray_button = tk.Button(self.button_frame, text="Open Tray", command=self.tray_state,
                                     **controller.widget_params)

        error_label_params = self.patient_information_frame.label_params.copy()
        error_label_params["font"] = ("Helvetica", 10)
        self.error_label = tk.Label(self.button_frame,
                                    textvariable=tk.StringVar(value=f"Invalid Input!"),
                                    **error_label_params)
        # display widgets
        self.patient_information_frame.pack(side=TOP, fill=X, expand=True, padx=10, pady=10)
        self.button_frame.pack(side=BOTTOM, fill=X, padx=50, pady=10)
        self.back_button.pack(side=LEFT, padx=10)
        self.tray_button.pack(side=LEFT, padx=10)
        self.start_scan_button.pack(side=RIGHT, padx=10)

    def tray_state(self):
        if self.tray_button.cget("text") == "Open Tray":
            self.patient_information_frame.start_tray_procedure(False)
            self.tray_button.config(text="Close Tray")

        else:
            self.patient_information_frame.start_tray_procedure(True)
            self.tray_button.config(text="Open Tray")

    def save_patient_info(self) -> bool:
        self.patient_info = self.patient_information_frame.get_patient_info()
        # TODO: save the information that is entered in the patient_information_frame into the database
        return len(self.patient_info.keys()) != 0

    def show_homepage(self):
        self.pack_forget()
        self.controller.title("Homepage")
        self.controller.show_page(self.controller.home_page)

    def show_scan_page(self):
        if not self.save_patient_info():
            self.error_label.pack(anchor="center", padx=10, pady=10)
            return
        # Start Calibration
        #self.patient_information_frame.start_calibration_procedure()
        self.pack_forget()
        self.controller.show_page(self.controller.scan_page, "- Calibration")

    def show(self, *args):
        self.controller.title("Scan " + args[0] if args else "")
        self.pack(fill=BOTH, expand=True)


class PatientInformationFrame(tk.Frame):
    def __init__(self, parent: PatientInfoPage, number_of_slides=3):
        super().__init__(parent, bg=parent.controller.widget_params["bg"])
        self.parent = parent
        self.widget_params = parent.controller.widget_params.copy()
        self.widget_params.update({"font": ("Helvetica", 10, "bold")})
        self.button_params = self.widget_params.copy()
        self.box_params = self.widget_params.copy()
        self.label_params = self.widget_params.copy()

        self.number_of_slides = number_of_slides

        self.box_params.pop("padx"), self.box_params.pop("pady"), self.box_params.pop("activebackground")
        self.box_params.update({"borderwidth": 1, "highlightthickness": 1})
        self.label_params.update({"borderwidth": 0, "highlightthickness": 0, "padx": 0, "pady": 5,
                                  "font": ("Helvetica", 12, "bold")})
        self.button_params.update({"highlightthickness": 0, "borderwidth": 0, "padx": 0, "pady": 5})
        self.numpad_button_params = self.widget_params.copy()
        self.numpad_button_params.update({"width": 4, "height": 2, "font": ("Helvetica", 12, "bold")})
        # widgets
        self.arduino = parent.controller.arduino

        self.sub_frames = []
        self.checkbuttons = []
        self.labels = []
        self.entry_boxes = []

        self.main_frame = tk.Frame(self, bg=parent.controller.widget_params["bg"])
        self.slide_frame = tk.Frame(self.main_frame, bg=parent.controller.widget_params["bg"])
        self.numpad_frame = tk.Frame(self.main_frame, bg=parent.controller.widget_params["bg"])
        self.numpad_buttons = list()
        self.numpad_frames = list()
        for i in range(4):
            if i == 3:
                self.numpad_frames.append(tk.Frame(self.numpad_frame, bg=parent.controller.widget_params["bg"]))
                self.numpad_buttons.append(tk.Button(self.numpad_frames[i],
                                                     text="0", command=partial(self.numpad_input, 0),
                                                     **self.numpad_button_params))
                break

            self.numpad_frames.append(tk.Frame(self.numpad_frame, bg=parent.controller.widget_params["bg"]))
            for j in range(3):
                self.numpad_buttons.append(tk.Button(self.numpad_frames[i],
                                                     text=str(i * 3 + j + 1), command=partial(self.numpad_input, i * 3 + j + 1),
                                                     **self.numpad_button_params))

        self.checkbutton_var = [[tk.IntVar(), tk.StringVar()] for _ in range(self.number_of_slides)]
        self.id_text = tk.Label(self.slide_frame, text="Patient ID:", **self.label_params)

        self.main_frame.pack(side=TOP, fill=X, expand=True, padx=10, pady=10)
        self.slide_frame.pack(side=LEFT, fill=X, padx=10, pady=10)
        self.numpad_frame.pack(side=RIGHT, padx=10, pady=10)
        self.id_text.pack(side=TOP, padx=10, pady=10)

        for i in range(4):
            if i == 3:
                self.numpad_frames[i].pack(side=TOP, pady=3)
                self.numpad_buttons[9].pack(anchor=CENTER)
                break
            self.numpad_frames[i].pack(side=TOP, pady=3)
            for j in range(3):
                self.numpad_buttons[i * 3 + j].pack(side=LEFT, padx=3)

        for i in range(self.number_of_slides):
            txt_var = tk.StringVar(value=f"Slide #{i + 1}:")
            # create widgets
            sub_frame = tk.Frame(self.slide_frame, bg=self.widget_params["bg"])
            click_frame = tk.Frame(sub_frame, bg=self.widget_params["bg"], cursor="hand2")
            command = self.show_entry_box(i)
            checkbuttons = tk.Checkbutton(click_frame, variable=self.checkbutton_var[i][0], command=command,
                                          **self.button_params)
            label = tk.Label(click_frame, textvariable=txt_var,
                             **self.label_params)
            click_frame.bind("<Button-1>", func=command)
            label.bind("<Button-1>", func=command)
            entry_box = tk.Entry(sub_frame, textvariable=self.checkbutton_var[i][1], **self.box_params)

            # append widgets
            self.sub_frames.append(sub_frame)
            self.checkbuttons.append(checkbuttons)
            self.labels.append(label)
            self.entry_boxes.append(entry_box)
            # display widgets
            sub_frame.pack(side=TOP, fill=X, padx=10, pady=10, anchor="w")
            click_frame.pack(side=tk.LEFT, anchor="w")
            checkbuttons.pack(side=tk.LEFT, padx=10, pady=0)
            label.pack(side=tk.LEFT, padx=10, pady=0)
            # entry_box.pack(side=tk.LEFT, padx=10, pady=0)

    def numpad_input(self, i):
        for j in range(3):
            if self.entry_boxes[j].focus_get() == self.entry_boxes[j]:
                self.checkbutton_var[j][1].set(self.checkbutton_var[j][1].get() + str(i))
                self.entry_boxes[j].icursor(len(self.checkbutton_var[j][1].get()))

    def get_patient_checkbutton_info(self):
        return [(i[0].get(), i[1].get()) for i in self.checkbutton_var]

    def show_entry_box(self, i):
        def show_ith(*args):
            if len(args):
                self.checkbutton_var[i][0].set(1 - self.checkbutton_var[i][0].get())
            if self.checkbutton_var[i][0].get() == 1:
                self.entry_boxes[i].pack(side=tk.LEFT, padx=10, pady=0, fill=X, expand=True)
                self.entry_boxes[i].focus_set()
            else:
                self.entry_boxes[i].pack_forget()

        return show_ith

    def get_patient_info(self) -> dict:
        # print([i[0].get() for i in self.checkbutton_var])
        # return a dictionary of patient information
        patient_info = {}
        for i in range(self.number_of_slides):
            if self.checkbutton_var[i][0].get() == 1:
                if self.entry_boxes[i].get() == "" or not self.entry_boxes[i].get().isdigit():
                    return {}
                else:
                    self.parent.error_label.pack_forget()
                patient_info[f"slide{i + 1}"] = self.entry_boxes[i].get()
        return patient_info

    def start_tray_procedure(self, direction: int):
        #tray_procedure(arduino, direction)
        start_tray = threading.Thread(target=tray_procedure, args=(self.arduino, direction, ))
        start_tray.start()
