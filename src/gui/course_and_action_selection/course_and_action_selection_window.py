import tkinter
from tkinter import ttk
import canvasapi

from typing import Any

from src.gui.course_and_action_selection.course_selection.course_selection_frame import CourseSelectionFrame
from src.gui.convenience.resizeable_window import ResizeableWindow


class CourseAndActionSelectionWindow(ResizeableWindow):

    def __init__(self, canvas_connection: canvasapi.Canvas,
                 master=None,
                 cnf: dict = None, **kw: Any):
        cnf = cnf if cnf is not None else {}
        super().__init__(master, cnf, **kw)
        self.title('Canvas Helpers - Course and Action Selection')
        self.canvas_connection = canvas_connection
        self.courses = CourseSelectionFrame(canvas_connection, master=self)
        self.courses.grid(row=0, column=0, sticky=tkinter.NSEW)

        self.enable_resizing()
