import tkinter
from tkinter import ttk

import itertools

from typing import Union, Iterable, Dict, Any, List, Iterator, Tuple


class ButtonGroup(ttk.LabelFrame):
    def __init__(self, master=None, button_type: Union[ttk.Radiobutton, ttk.Checkbutton] = ttk.Radiobutton,
                 button_configs: Iterable[Dict[str, Any]] = (),
                 orientation: str = tkinter.VERTICAL, **kw):
        super().__init__(master, **kw)
        self.button_values = [tkinter.StringVar(self) for _ in button_configs] if button_type == ttk.Checkbutton else [
            tkinter.StringVar(self)]
        self.buttons = [button_type(self, variable=variable, **config) for config, variable in
                        zip(button_configs, itertools.cycle(self.button_values))]
        self.orientation = orientation
        self.place_contents()

    def place_contents(self) -> None:
        for i, button in enumerate(self.buttons):
            if self.orientation == tkinter.HORIZONTAL:
                button.grid(row=0, column=i)
            else:
                button.grid(row=i, column=0, sticky=tkinter.W)

    def get_radio_button_value(self) -> str:
        if not self.buttons:
            raise IndexError('There are no buttons in this container')
        elif isinstance(self.buttons[0], ttk.Radiobutton):
            return self.button_values[0].get()
        else:
            raise TypeError('The Buttons in this container are not tkinter.ttk.Radiobuttons')

    def get_name_and_button_values(self) -> Dict[str, str]:
        return {button['text']: value.get() for button, value in zip(self.buttons, self.button_values)}

    def __iter__(self) -> Iterator[Tuple[Union[ttk.Radiobutton, ttk.Checkbutton], tkinter.StringVar]]:
        return zip(self.buttons, itertools.cycle(self.button_values))
