import tkinter
from tkinter import ttk
from tkinter import messagebox
import webbrowser
import canvasapi
import requests


class LoginWindow(tkinter.Toplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title('Canvas Helpers - Login')

        # the content of the login window
        self.content = LoginFrame(self)
        self.bind("<Return>", self.content.login)

        self.content.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.rowconfigure(0, weight=1), self.columnconfigure(0, weight=1)

        self.size_grip = ttk.Sizegrip(self)
        self.size_grip.grid(row=999, column=999, sticky=tkinter.SE)


class LoginFrame(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # create the attributes for the canvas api key
        self.canvas_key_label = ttk.Label(self, text='Canvas API Key:')
        self.canvas_key = tkinter.StringVar()
        self.canvas_key_entry = ttk.Entry(self, width=70, textvariable=self.canvas_key)
        self.canvas_key_entry.focus()

        # create the attributes for the canvas url
        self.canvas_url_label = ttk.Label(self, text='Canvas URL:')
        self.canvas_url = tkinter.StringVar(value=r'https://canvas.ucdavis.edu/')
        self.canvas_url_entry = ttk.Entry(self, width=70, textvariable=self.canvas_url)

        # login button
        self.button_frame = ttk.Frame(self)
        self.login_button = ttk.Button(self.button_frame, text='Login', command=self.login, default='active')

        # quit button
        self.quit_button = ttk.Button(self.button_frame, text='Quit', command=self.quit)

        self.place_widgets()

    def create_canvas_key(self):
        self.canvas_key_label = ttk.Label(self, text='Canavs API Key')
        self.canvas_key_entry = ttk.Entry(self, width=70)

    def create_canvas_url(self):
        self.canvas_url_label = ttk.Label(self, text='Canvas URL')
        self.canvas_url = tkinter.StringVar(value=r'https://canvas.ucdavis.edu/')
        self.canvas_url_entry = ttk.Entry(self, width=70, textvariable=self.canvas_url)

    def place_widgets(self):
        for rows_cols in range(2):
            self.rowconfigure(rows_cols, weight=1), self.columnconfigure(rows_cols, weight=1)

        self.canvas_key_label.grid(row=0, column=0, sticky=tkinter.E)
        self.canvas_key_entry.grid(row=0, column=1, sticky=tkinter.EW)
        self.canvas_url_label.grid(row=1, column=0, sticky=tkinter.E)
        self.canvas_url_entry.grid(row=1, column=1, sticky=tkinter.EW)
        self.place_buttons()
        # self.login_button.grid(row=2, column=0)
        # self.quit_button.grid(row=2, column=1)

    def place_buttons(self):
        self.button_frame.grid(row=2, column=1, columnspan=2)
        self.login_button.grid(row=0, column=0)
        self.quit_button.grid(row=0, column=1)

    def login(self, *args):
        try:
            canvas_connection = canvasapi.Canvas(self.canvas_url.get(), self.canvas_key.get())
            me = canvas_connection.get_user('self')
            print('Connected')
        except requests.exceptions.ConnectionError:
           messagebox.showinfo(title='Bad URL',
               message=f'Cannot connect to {self.canvas_url.get()}.\n'
                                               f'Please check you entered the correct url.')
        except canvasapi.exceptions.ResourceDoesNotExist as e:
            messagebox.showinfo(title='Bad API Key',
                message=f'Cannot connect to Canvas with the given API Key.\n'
                                        f'Please check that you entered your API Key correctly.')
