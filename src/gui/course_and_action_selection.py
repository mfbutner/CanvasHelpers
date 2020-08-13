import tkinter
from tkinter import ttk
import canvasapi

from typing import Any

from .course_selection_tree import CourseSelectionTree


class CourseAndActionSelectionWindow(tkinter.Toplevel):

    def __init__(self, canvas_connection: canvasapi.Canvas,
                 master=None,
                 cnf: dict = None, **kw: Any):
        cnf = cnf if cnf is not None else {}
        super().__init__(master, cnf, **kw)
        self.canvas_connection = canvas_connection
        self.courses = CourseSelectionTree(canvas_connection, master=self, selectmode='browse')
        self.courses.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.courses.scroll_bar.grid(row=0, column=1, sticky=tkinter.NS)
