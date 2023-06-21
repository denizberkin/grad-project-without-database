import tkinter as tk
from tkinter import Tk
from tkinter import font as tkfont

import serial

from gui.pages.deviceinformation import DeviceInformation
from gui.pages.manuelcalibration import ManualCalibration
from gui.pages.homepage import Homepage
from gui.pages.autocalibration import AutoCalibrationPage
from gui.pages.patientinfo import PatientInfoPage
from gui.pages.scan import ScanPage
from gui.pages import *
from tkinter import BOTH

# add tkinter button
# #f8f7f3 light
# #0d2452 navy blue
# #eeebe2 mid grey


class App(Tk):
    def __init__(self):
        super().__init__()
        self.widget_params = {
            'bg': '#f2e6d9',
            'fg': '#0d2452',
            'padx': 20,
            'pady': 10,
            'activebackground': '#e6ccb3',
            'font': ('Helvetica', 14, 'bold'),
            'borderwidth': 1,
            'highlightthickness': 2,
            'highlightcolor': '#0d2452'
        }
        self.title_font = tkfont.Font(family="Helvetica", size=18, weight="bold", slant="italic")
        self.title("APP")
        self.configure(bg="#f8f7f3")
        if DEVICE == "pi":
            self.attributes("-fullscreen", True)
        else:
            self.width, self.height = 900, 500
            self.geometry(f"{self.width}x{self.height}")
        # self.resizable(False, False)    # disable resizing

        if ARDUINO_EXIST:
            self.arduino = serial.Serial(PORT_PATH, 9600, timeout=1)
        else:
            self.arduino = 0
        # widgets
        self.container = tk.Frame(self)
        self.home_page = Homepage(self.container, self)
        self.manual_calibration_page = ManualCalibration(self.container, self)
        self.patient_info_page = PatientInfoPage(self.container, self)
        self.scan_page = ScanPage(self.container, self)
        self.auto_calibration_page = AutoCalibrationPage(self.container, self)
        self.device_information_page = DeviceInformation(self.container, self)

        # display widgets
        self.container.pack(fill=BOTH, expand=True)
        self.home_page.pack(fill=BOTH, expand=True)
        self.manual_calibration_page.pack_forget()
        self.auto_calibration_page.pack_forget()
        self.patient_info_page.pack_forget()
        self.scan_page.pack_forget()
        self.device_information_page.pack_forget()

    @staticmethod
    def show_page(page, *args):
        page.show(*args)


if __name__ == "__main__":
    app = App()
    app.mainloop()
