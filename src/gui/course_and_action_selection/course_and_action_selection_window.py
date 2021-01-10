import tkinter
from tkinter import ttk
import canvasapi

from typing import Any

from src.gui.course_and_action_selection.course_selection.course_selection_frame import CourseSelectionFrame
from src.gui.convenience.resizeable_window import ResizeableWindow
from .actions.actions_frame import CourseActionsFrame

from .course_selection import course_selection_tree


class CourseAndActionSelectionWindow(ResizeableWindow):

    def __init__(self, canvas_connection: canvasapi.Canvas,
                 master=None,
                 cnf: dict = None, **kw: Any):
        cnf = cnf if cnf is not None else {}
        super().__init__(master, cnf, **kw)
        self.title('Canvas Helpers - Course and Action Selection')
        self.canvas_connection = canvas_connection
        self.courses = CourseSelectionFrame(canvas_connection, master=self)
        self.actions = CourseActionsFrame(master=self, text='Course Actions')

        self.place_contents()
        self.enable_resizing()
        self.bind(course_selection_tree.COURSE_PICKED_EVENT, self.notify_children_of_course_select)
        self.bind(course_selection_tree.COURSES_REFRESHED_EVENT, self.notify_children_of_course_select)

    def place_contents(self):
        self.courses.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.actions.grid(row=0, column=1, sticky=tkinter.NSEW)

    def notify_children_of_course_select(self, event) -> None:
        self.actions.canvas_course = self.courses.selected_course
