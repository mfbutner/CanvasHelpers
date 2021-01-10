import datetime
import tkinter
from tkinter import ttk

from .time_picker import TimePicker
from .date_picker import DateEntry


class DateTimePicker(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.date_picker = DateEntry(self)
        self.time_picker = TimePicker(self)
        self.place_contents()

    def place_contents(self) -> None:
        self.date_picker.grid(row=0, column=0)
        self.time_picker.grid(row=0, column=1)

    def get_datetime(self) -> datetime.datetime:
        date = self.date_picker.get_date()
        time = self.time_picker.get_time()
        return datetime.datetime(date.year, date.month, date.day, time.hour, time.minute)

    def set_datetime(self, date_and_time: datetime.datetime) -> None:
        self.date_picker.set_date(date_and_time)
        self.time_picker.set_time(date_and_time)
