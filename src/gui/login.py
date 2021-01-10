import tkinter
from tkinter import messagebox
from tkinter import ttk

import canvasapi
import requests

from src.gui.convenience.labeled_entry import LabeledEntry
from src.gui.course_and_action_selection.course_and_action_selection_window import CourseAndActionSelectionWindow
from .convenience.resizeable_window import ResizeableWindow


class LoginWindow(ResizeableWindow):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title('Canvas Helpers - Login')

        # the content of the login window
        self.content = LoginFrame(self)
        self.bind("<Key-Return>", self.content.login)

        self.content.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.enable_resizing()


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
        label_and_entry = LabeledEntry(self, 'Canvas API Key')
        label_and_entry.entry['width'] = 70
        return label_and_entry

    def create_canvas_url(self) -> LabeledEntry:
        label_and_entry = LabeledEntry(self, 'Canvas URL', 'https://canvas.ucdavis.edu/')
        label_and_entry.entry['width'] = 70
        return label_and_entry

    def place_widgets(self) -> None:
        # label_length = max(self.canvas_key.label['text'], self.canvas_url.label['text'])
        # self.canvas_key.label['width'] = label_length
        # self.canvas_url.label['width'] = label_length
        self.canvas_key.grid(row=0, column=0, sticky=tkinter.EW)
        self.canvas_url.grid(row=1, column=0, sticky=tkinter.EW)
        self.place_buttons()

    def place_buttons(self) -> None:
        self.button_frame.grid(row=2, column=0)
        self.login_button.grid(row=0, column=0)
        self.quit_button.grid(row=0, column=1)

    def login(self, *args):
        try:
            canvas_connection = canvasapi.Canvas(self.canvas_url.entry.get(), self.canvas_key.entry.get())
            canvas_connection.get_current_user()
            CourseAndActionSelectionWindow(canvas_connection)
            self.master.destroy()

        except requests.exceptions.ConnectionError:
            messagebox.showinfo(title='Bad URL',
                                message=f'Cannot connect to {self.canvas_url.entry.get()}.\n'
                                        f'Please check you entered the correct url.')
        except (canvasapi.exceptions.ResourceDoesNotExist, canvasapi.exceptions.InvalidAccessToken):
            messagebox.showinfo(title='Bad API Key',
                                message=f'Cannot connect to Canvas with the given API Key.\n'
                                        f'Please check that you entered your API Key correctly.')
