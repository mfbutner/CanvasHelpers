import tkinter
from tkinter import ttk

import canvasapi

from .course_selection_tree import CourseSelectionTree


class CourseSelectionFrame(ttk.Frame):
    def __init__(self, canvas_connection: canvasapi.Canvas,
                 master=None, **kw):
        super().__init__(master, **kw)
        self.canvas_connection = canvas_connection
        self.course_tree = CourseSelectionTree(canvas_connection, master=self, selectmode='browse')
        self.refresh_button = self.create_refresh_button()
        self.place_contents()

    def create_refresh_button(self) -> ttk.Button:
        button = ttk.Button(master=self, text='Refresh Courses', command=self.course_tree.refresh)
        return button

    def place_contents(self) -> None:
        self.course_tree.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.course_tree.scroll_bar.grid(row=0, column=1, sticky=(tkinter.N, tkinter.S, tkinter.W))
        self.refresh_button.grid(row=1, column=0, sticky=(tkinter.N, tkinter.E, tkinter.W))
