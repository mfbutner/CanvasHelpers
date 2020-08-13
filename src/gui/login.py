import tkinter
from tkinter import messagebox
from tkinter import ttk

import canvasapi
import requests

from .labeled_entry import LabeledEntry
from .course_and_action_selection import CourseAndActionSelectionWindow


class LoginWindow(tkinter.Toplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title('Canvas Helpers - Login')

        # the content of the login window
        self.content = LoginFrame(self)
        self.bind("<Key-Return>", self.content.login)

        self.content.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.rowconfigure(0, weight=1), self.columnconfigure(0, weight=1)

        self.size_grip = ttk.Sizegrip(self)
        self.size_grip.grid(row=999, column=999, sticky=tkinter.SE)


class LoginFrame(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.canvas_key = self.create_canvas_key()
        self.canvas_key.entry.focus()  # start the cursor in the entry for the key

        self.canvas_url = self.create_canvas_url()

        # login button
        self.button_frame = ttk.Frame(self)
        self.login_button = ttk.Button(self.button_frame, text='Login', command=self.login, default='active')

        # quit button
        self.quit_button = ttk.Button(self.button_frame, text='Quit', command=self.quit)

        self.place_widgets()

    def create_canvas_key(self) -> LabeledEntry:
        label = ttk.Label(self, text='Canvas API Key')
        entry = ttk.Entry(self, width=70)
        return LabeledEntry(label, entry)

    def create_canvas_url(self) -> LabeledEntry:
        label = ttk.Label(self, text='Canvas URL')
        entry_contents = tkinter.StringVar(value=r'https://canvas.ucdavis.edu/')
        entry = ttk.Entry(self, width=70, textvariable=entry_contents)
        return LabeledEntry(label, entry, entry_contents)

    def place_widgets(self)->None:
        for rows_cols in range(2):
            self.rowconfigure(rows_cols, weight=1), self.columnconfigure(rows_cols, weight=1)

        self.canvas_key.label.grid(row=0, column=0, sticky=tkinter.E)
        self.canvas_key.entry.grid(row=0, column=1, sticky=tkinter.EW)
        self.canvas_url.label.grid(row=1, column=0, sticky=tkinter.E)
        self.canvas_url.entry.grid(row=1, column=1, sticky=tkinter.EW)
        self.place_buttons()

    def place_buttons(self)->None:
        self.button_frame.grid(row=2, column=1, columnspan=2)
        self.login_button.grid(row=0, column=0)
        self.quit_button.grid(row=0, column=1)

    def login(self, *args):
        try:
            canvas_connection = canvasapi.Canvas(self.canvas_url.entry.get(), self.canvas_key.entry.get())
            canvas_connection.get_user('self') # attempt to get some info from canvas to see if we connected to it
            print('Connected')
            CourseAndActionSelectionWindow(canvas_connection)
        except requests.exceptions.ConnectionError:
            messagebox.showinfo(title='Bad URL',
                                message=f'Cannot connect to {self.canvas_url.entry.get()}.\n'
                                        f'Please check you entered the correct url.')
        except (canvasapi.exceptions.ResourceDoesNotExist, canvasapi.exceptions.InvalidAccessToken):
            messagebox.showinfo(title='Bad API Key',
                                message=f'Cannot connect to Canvas with the given API Key.\n'
                                        f'Please check that you entered your API Key correctly.')
