import tkinter as tk
from PIL import ImageTk, Image

from tkinter import BOTH, CENTER

# to avoid circular import, TYPE_CHECKING is always False.
from typing import TYPE_CHECKING

from gui.pages import LOGO_PATH
from communication.serialcomm import calibration_procedure

if TYPE_CHECKING:
    from mainapp import App


class Homepage(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: 'App'):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.arduino = self.controller.arduino

        self.configure(bg="#f2e6d9")
        # widgets
        left_frame = tk.Frame(self)
        right_frame = tk.Frame(self)
        left_frame.configure(bg="#f2e6d9")
        right_frame.configure(bg="#f2e6d9")

        button_width = 20
        # create widgets
        # create a widget to display the logo.png of the program
        # print(os.getcwd())
        self.logo = ImageTk.PhotoImage(Image.open(LOGO_PATH).resize((360, 75), Image.ANTIALIAS))
        self.logo_label = tk.Label(self, image=self.logo, bg="#f2e6d9")

        self.manual_calibration_button = tk.Button(left_frame, text="Manual Calibration",
                                                   command=self.show_manual_calibration,
                                                   **controller.widget_params, width=button_width)
        self.scan_button = tk.Button(right_frame, text="Scanning", command=self.show_scan_page,
                                     **controller.widget_params, width=button_width)
        self.auto_calibration_button = tk.Button(left_frame, text="Auto Calibration", command=self.show_auto_calibration,
                                                 **controller.widget_params, width=button_width)
        self.device_info_button = tk.Button(right_frame, text="Device Information", command=self.show_device_info,
                                            **controller.widget_params, width=button_width)

        # display widgets
        padx = 10
        pady = 10
        self.logo_label.place(relx=0.5, rely=0.15, anchor="n")

        left_frame.place(relx=0.3, rely=0.5, anchor=CENTER)
        self.manual_calibration_button.pack(padx=padx, pady=pady)
        self.scan_button.pack(padx=padx, pady=pady)

        right_frame.place(relx=0.7, rely=0.5, anchor=CENTER)
        self.auto_calibration_button.pack(padx=padx, pady=pady)
        self.device_info_button.pack(padx=padx, pady=pady)

    def show_device_info(self):
        self.pack_forget()
        self.controller.show_page(self.controller.device_information_page)

    def show_auto_calibration(self):
        self.pack_forget()
        self.controller.show_page(self.controller.auto_calibration_page)

    def show_scan_page(self):
        self.pack_forget()
        self.controller.show_page(self.controller.patient_info_page, "- Patient Information")

    def show_manual_calibration(self):
        self.pack_forget()
        self.controller.show_page(self.controller.manual_calibration_page)

    def show(self):
        self.pack(fill=BOTH, expand=True)
