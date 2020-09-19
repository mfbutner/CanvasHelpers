import tkinter
from tkinter import ttk
from tkinter import messagebox

from typing import Optional

import canvasapi

from .kudo_point_assignment_creation_window import KudoPointAssignmentCreationWindow

class CourseActionsFrame(ttk.LabelFrame):

    def __init__(self, canvas_course: Optional[canvasapi.course.Course] = None, master=None, **kw):
        super().__init__(master, **kw)
        self._canvas_course = canvas_course
        self.kudo_point_actions = KudoPointActionsFrame(master=self, text='Kudo Point Actions')
        self.place_contents()

    @property
    def canvas_course(self) -> canvasapi.course.Course:
        return self._canvas_course

    @canvas_course.setter
    def canvas_course(self, value: Optional[canvasapi.course.Course]) -> None:
        self._canvas_course = value

    def place_contents(self) -> None:
        self.kudo_point_actions.grid(row=0, column=0, sticky=tkinter.NSEW)


class KudoPointActionsFrame(ttk.LabelFrame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.kudo_point_giving_assignment_button = self.create_kudo_point_assignment_button()
        self.evaluate_kudo_point_assignment_button = self.create_evaluate_kudo_point_assignment_button()
        self.place_contents()

    @property
    def canvas_course(self) -> canvasapi.course.Course:
        return self.master.canvas_course

    # gui ------------------------------

    def create_kudo_point_assignment_button(self) -> ttk.Button:
        return ttk.Button(master=self, text='Create Kudo Point Giving Assignment',
                          command=self.create_kudo_point_giving_assignment)

    def create_evaluate_kudo_point_assignment_button(self) -> ttk.Button:
        return ttk.Button(master=self, text='Evaluate Kudo Point Assignment',
                          command=self.evaluate_kudo_point_giving_assignment)

    def place_contents(self) -> None:
        self.kudo_point_giving_assignment_button.grid(row=0, column=0)
        self.evaluate_kudo_point_assignment_button.grid(row=0, column=1)

    # logic -------------------------------------------

    def create_kudo_point_giving_assignment(self, *args):
        if self.canvas_course is None:
            self.request_course_selection()
        else:
            KudoPointAssignmentCreationWindow(self.canvas_course,self)

    def evaluate_kudo_point_giving_assignment(self, *args):
        if self.canvas_course is None:
            self.request_course_selection()
        else:
            ...

    @staticmethod
    def request_course_selection():
        messagebox.showinfo('Select a Course', 'Please select a course before choosing an action.')
