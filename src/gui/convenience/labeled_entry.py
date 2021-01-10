import tkinter
from tkinter import ttk
from typing import Optional

from typing import Optional, Union


class LabeledEntry(ttk.Frame):

    def __init__(self, master=None,
                 label_content: Union[tkinter.Variable, str] = '',
                 entry_contents: Union[tkinter.Variable, str] = '',
                 orientation: str = 'horizontal', **kw):
        super().__init__(master, **kw)

        self.label = ttk.Label(self)
        self.init_text(self.label, label_content)

        self.entry = ttk.Entry(self)
        self.init_text(self.entry, entry_contents)

        self.orientation = orientation

        self.place_contents()

    def init_text(self, widget: Union[ttk.Widget, tkinter.Widget], content: Union[tkinter.Variable, str]) -> None:
        if isinstance(content, str):
            content = tkinter.StringVar(widget,value=content)

        widget.content = content
        widget['textvariable'] = content

    def place_contents(self) -> None:

        if self.orientation == 'horizontal':
            self.label.grid(row=0, column=0, sticky=tkinter.E)
            self.entry.grid(row=0, column=1, sticky=tkinter.EW)
        else:
            self.label.grid(row=0, column=0, sticky=tkinter.S)
            self.entry.grid(row=1, column=0, sticky=tkinter.NS)
