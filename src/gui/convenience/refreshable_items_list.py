import tkinter
from tkinter import ttk

from typing import Optional, Callable, Iterable, Any, Dict
from .tracked_items_list_box import TrackedItemListBox


class RefreshableItemsList(ttk.Frame):
    def __init__(self, master=None,
                 item_generator: Callable[[], Iterable] = lambda: [],
                 to_string: Callable[[Any], str] = str,
                 list_box_configs: Optional[Dict[str, Any]] = None,
                 include_vertical_scroll_bar: bool = True,
                 include_horizontal_scroll_bar: bool = False,
                 button_configs: Optional[Dict[str, Any]] = {'text': 'Refresh'},
                 **kw):
        super().__init__(master, **kw)
        self.item_generator = item_generator
        self.listbox = TrackedItemListBox(self, item_generator(), to_string, list_box_configs)
        if include_vertical_scroll_bar:
            self.vertical_scroll_bar: Optional[ttk.Scrollbar] = ttk.Scrollbar(self, orient=tkinter.VERTICAL,
                                                                              command=self.listbox.yview)
            self.listbox['yscrollcommand'] = self.vertical_scroll_bar
        else:
            self.vertical_scroll_bar: Optional[ttk.Scrollbar] = None

        if include_horizontal_scroll_bar:
            self.horizontal_scroll_bar: Optional[ttk.Scrollbar] = ttk.Scrollbar(self, orient=tkinter.HORIZONTAL,
                                                                                command=self.listbox.xview)
            self.listbox['xscrollcommand'] = self.horizontal_scroll_bar
        else:
            self.horizontal_scroll_bar: Optional[ttk.Scrollbar] = None

        self.refresh_button = ttk.Button(self, command=self.refresh_listbox, **button_configs)
        self.place_contents()

    def refresh_listbox(self):
        self.listbox.values = self.item_generator()

    def place_contents(self):
        self.listbox.grid(row=0, column=0, sticky=tkinter.NSEW)
        if self.vertical_scroll_bar is not None:
            self.vertical_scroll_bar.grid(row=0, column=1, sticky=tkinter.NS)
        if self.horizontal_scroll_bar is not None:
            self.horizontal_scroll_bar.grid(row=1, column=0, sticky=tkinter.EW)
        self.refresh_button.grid(row=5, column=0)
