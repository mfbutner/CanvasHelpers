import datetime

import tkinter
from tkinter import ttk

from src.gui.convenience.date_time_picker import DateTimePicker
from src.gui.convenience.tool_tip import CreateToolTip


class AssignmentDates(ttk.LabelFrame):
    def __init__(self, master=None, text='Dates', **kw):
        super().__init__(master, text=text, **kw)

        self.unlock_date = DateTimePicker(self)
        self.unlock_date_label = ttk.Label(self, text='Unlock Date')
        CreateToolTip(self.unlock_date, 'The time the assignment will be revealed to the student.')

        self.due_date = DateTimePicker(self)
        self.due_date_label = ttk.Label(self, text='Due Date')
        CreateToolTip(self.due_date, 'The time the assignment is due.')

        self.lock_date = DateTimePicker(self)
        self.lock_date_label = ttk.Label(self, text='Lock Date')
        CreateToolTip(self.lock_date, 'The latest date a student can submit the assignment.')
        self.place_contents()

    def place_contents(self) -> None:
        self.unlock_date_label.grid(row=0, column=0, )
        self.unlock_date.grid(row=0, column=1, sticky=tkinter.EW)

        self.due_date_label.grid(row=1, column=0)
        self.due_date.grid(row=1, column=1, sticky=tkinter.EW)

        self.lock_date_label.grid(row=2, column=0)
        self.lock_date.grid(row=2, column=1, sticky=tkinter.EW)

    def set_default_dates(self) -> None:
        """
        Unlocked now
        Due a week from now
        Locked on due date (a week from now)
        :return:
        """
        now = datetime.datetime.now()
        week_from_now = now + datetime.timedelta(days=7)
        self.unlock_date.set_datetime(now)
        self.due_date.set_datetime(week_from_now)
        self.lock_date.set_datetime(week_from_now)

