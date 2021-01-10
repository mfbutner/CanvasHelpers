import tkinter
import calendar
import datetime
from tkinter import ttk
from tkinter import messagebox

from typing import Union


class DateEntry(ttk.Frame):

    def __init__(self, master=None, ordering=('month', 'day', 'year'), **kw):
        super().__init__(master, **kw)
        self.ordering = {
            ordering[0]: 0,
            ordering[1]: 1,
            ordering[2]: 2
        }

        self.entry_1 = ttk.Entry(self, **kw)
        self.label_1 = ttk.Label(self, text='/', **kw)
        self.entry_2 = ttk.Entry(self, **kw)
        self.label_2 = ttk.Label(self, text='/', **kw)
        self.entry_3 = ttk.Entry(self, **kw)

        self.entry_1.pack(side=tkinter.LEFT)
        self.label_1.pack(side=tkinter.LEFT)
        self.entry_2.pack(side=tkinter.LEFT)
        self.label_2.pack(side=tkinter.LEFT)
        self.entry_3.pack(side=tkinter.LEFT)

        self.entries = [self.entry_1, self.entry_2, self.entry_3]
        self.month_entry['width'] = 2
        self.day_entry['width'] = 2
        self.year_entry['width'] = 4

        self.month_entry.bind('<KeyRelease>', lambda e: self._check(e, self.ordering['month'], 2))
        self.day_entry.bind('<KeyRelease>', lambda e: self._check(e, self.ordering['day'], 2))
        self.year_entry.bind('<KeyRelease>', lambda e: self._check(e, self.ordering['year'], 4))

        month_entry_validation = self.register(
            lambda number_text: self.is_number_between_or_empty(number_text, 1, 12, int))
        self.month_entry.configure(validate='key', validatecommand=(month_entry_validation, '%P'))

        day_entry_validation = self.register(
            lambda number_text: self.is_number_between_or_empty(number_text, 1, 31, int))
        self.day_entry.configure(validate='key', validatecommand=(day_entry_validation, '%P'))

        year_entry_validation = self.register(
            lambda number_text: self.is_positive_number_or_empty(number_text, int))
        self.year_entry.configure(validate='key', validatecommand=(year_entry_validation, '%P'))

        # message uses if they leave in a bad date
        self.bind('<FocusOut>', self.notify_bad_date_entered)

    @property
    def day_entry(self) -> ttk.Entry:
        return self.entries[self.ordering['day']]

    @property
    def month_entry(self) -> ttk.Entry:
        return self.entries[self.ordering['month']]

    @property
    def year_entry(self) -> ttk.Entry:
        return self.entries[self.ordering['year']]

    def check_legal_date_entered(self):
        month = self.month_entry.get()
        day = self.day_entry.get()
        year = self.year_entry.get()

        if not all((month, day, year)):
            return True  # not every field entered things are still ok

        month = int(month)
        day = int(day)
        year = int(year)
        # year legal, month legal, day legal
        # I'm choosing not to all years in BC. Remove the first condition if you don't want it
        return year > 0 and \
               month in range(1, 13) and \
               day in range(1, calendar.monthrange(year, month)[1] + 1)

    def notify_bad_date_entered(self, event):
        if not self.check_legal_date_entered():
            date = '/'.join((entry.get() for entry in self.entries))
            messagebox.showinfo('Bad Date', f'{date} does not exist. Please enter a valid date')

    @staticmethod
    def is_positive_number_or_empty(number_text: str, number_type=int) -> bool:
        if number_text:
            try:
                number = number_type(number_text)
                return number > 0
            except ValueError:
                return False
        else:
            return True

    @staticmethod
    def is_number_between_or_empty(number_text: str, min_value, max_value, number_type=int) -> bool:
        if number_text:
            try:
                number = number_type(number_text)
                return min_value <= number <= max_value
            except ValueError:  # text could not be converted to number
                return False
        else:
            return True

    def _check(self, event, index, size):
        entry = self.entries[index]
        next_index = index + 1
        next_entry = self.entries[next_index] if next_index < len(self.entries) else None
        data = entry.get()

        if len(data) >= size and next_entry:
            next_entry.focus()

    def get_date(self) -> datetime.date:
        return datetime.date(int(self.year_entry.get()), int(self.month_entry.get()), int(self.day_entry.get()))

    def set_date(self, date: Union[datetime.date, datetime.datetime]) -> None:
        self.month_entry.delete(0, tkinter.END)
        self.month_entry.insert(0, str(date.month))

        self.day_entry.delete(0, tkinter.END)
        self.day_entry.insert(0, str(date.day))

        self.year_entry.delete(0, tkinter.END)
        self.year_entry.insert(0, str(date.year))
