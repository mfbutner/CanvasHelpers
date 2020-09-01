import tkinter
import datetime
from tkinter import ttk
from typing import List, Union


class TimePicker(ttk.Frame):
    AM = datetime.time(2).strftime('%p')
    PM = datetime.time(14).strftime('%p')
    TIME_CHANGED = '<<TIME_CHANGED>>'

    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.hour_picker = ttk.Spinbox(self, width=2, values=self.n_digit_number_range(2, 1, 13, 1), wrap=True)
        self.hour_picker.set(self.hour_picker['values'][0])
        self.hour_picker.bind('<FocusOut>', lambda event: self.force_to_n_digits(event, 2))
        self.bind_time_changing_events(self.hour_picker)

        self.minute_picker = ttk.Spinbox(self, width=2, values=self.n_digit_number_range(2, 0, 61, 1), wrap=True)
        self.minute_picker.set(self.minute_picker['values'][0])
        self.minute_picker.bind('<FocusOut>', lambda event: self.force_to_n_digits(event, 2))
        self.bind_time_changing_events(self.minute_picker)

        self.separator = ttk.Label(self, text=':')
        self.am_pm_picker = ttk.Spinbox(self, width=4, values=(self.AM, self.PM), state='readonly',
                                        wrap=True)
        self.am_pm_picker.set(self.am_pm_picker['values'][0])
        self.bind_time_changing_events(self.am_pm_picker)

        self.place_contents()

    @property
    def hour(self) -> int:
        cur_hour = self.hour_picker.get()
        am_pm = self.am_pm_picker.get()
        return datetime.datetime.strptime(cur_hour + am_pm, '%I%p').hour

    @property
    def minute(self) -> int:
        return datetime.datetime.strptime(self.minute_picker.get(), '%M').minute

    def place_contents(self):
        self.hour_picker.grid(row=0, column=0)
        self.separator.grid(row=0, column=1)
        self.minute_picker.grid(row=0, column=2)
        self.am_pm_picker.grid(row=0, column=3)

    @staticmethod
    def n_digit_number_range(num_digits: int, start: int, stop: int, step: int) -> List[str]:
        return [TimePicker.make_number_n_digits(num, num_digits) for num in range(start, stop, step)]

    @staticmethod
    def make_number_n_digits(number: int, num_digits: int) -> str:
        str_num = str(number)
        return '0' * (num_digits - len(str_num)) + str_num

    @staticmethod
    def force_to_n_digits(event, num_digits: int):
        contents = event.widget.get()
        if len(contents) < num_digits:
            event.widget.set(TimePicker.make_number_n_digits(int(contents), num_digits))

    @staticmethod
    def fixed_with_str_int_to_int(str_num: str) -> int:
        if len(str_num) > 1:
            str_num = str_num.lstrip('0')
        return int(str_num)

    def bind_time_changing_events(self, spinbox: ttk.Spinbox) -> None:
        time_changing_events = ('<KeyRelease>', 'Backspace', '<<Increment>>', '<<Decrement>>')
        for event in time_changing_events:
            spinbox.bind(event, self.generate_time_change_event, add=True)

    def generate_time_change_event(self, event:tkinter.Event) -> None:

        self.event_generate(self.TIME_CHANGED, data=str(self.get_time()), when='tail')

    def get_time(self) -> datetime.time:
        return datetime.time(self.hour, self.minute)

    def set_time(self, time: Union[datetime.time, datetime.datetime]) -> None:
        self.hour_picker.set(time.strftime('%I'))
        self.minute_picker.set(time.strftime('%M'))
        self.am_pm_picker.set(time.strftime('%p'))
