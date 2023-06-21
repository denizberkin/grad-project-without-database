import tkinter as tk

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mainapp import App


class DeviceInformation(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: 'App'):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.widget_params = controller.widget_params.copy()
        self.widget_params.pop("padx"), self.widget_params.pop("pady"), self.widget_params.pop("font")
        self.widget_params.pop("highlightthickness"), self.widget_params.pop("highlightcolor")
        self.widget_params.update({"borderwidth": 0})

        self.configure(bg=controller.widget_params["bg"])

        self.widget_params.update({"font": ("Helvetica", 32, "bold")})
        self.device_id = tk.Label(self, text="Device: AISAM",
                                  **self.widget_params)
        self.widget_params.update({"font": ("Helvetica", 20, "bold")})
        self.serial_number = tk.Label(self, text="Serial Number: 3b1a185e-9505-11ed-a1eb-11ed",
                                      **self.widget_params)
        self.widget_params.update({"font": ("Helvetica", 16, "bold")})
        self.software_version = tk.Label(self, text="Software Version: v0.2",
                                         **self.widget_params)
        self.back_button = tk.Button(self, text="Back", command=self.show_homepage,
                                     **controller.widget_params)

        self.device_id.place(relx=0.5, rely=0.3, anchor="center")
        self.serial_number.place(relx=0.5, rely=0.45, anchor="center")
        self.software_version.place(relx=0.5, rely=0.55, anchor="center")
        self.back_button.place(relx=0.5, rely=0.9, anchor="center")

    def show(self):
        self.controller.title("Device Information")
        self.pack(fill="both", expand=True)

    def show_homepage(self):
        self.pack_forget()
        self.controller.title("Homepage")
        self.controller.show_page(self.controller.home_page)
