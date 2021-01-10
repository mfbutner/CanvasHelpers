import tkinter
from tkinter import ttk


class ResizeableWindow(tkinter.Toplevel):

    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.size_grip = self.size_grip = ttk.Sizegrip(self)
        self.size_grip.grid(row=999, column=999, sticky=tkinter.SE)

    def enable_resizing(self, row_weight: int = 1, column_weight: int = 1) -> None:
        """
       Enable a widget and all elements inside of it that have been placed
       using the grid method to resize. This must be called AFTER all widgets
       have been placed.
       :param row_weight: the rate at which the rows expands. default 1
       :param column_weight: the rate at which the columns expands. default 1
       :return: None
       """
        self._enable_resizing(self, row_weight, column_weight)

    @staticmethod
    def _enable_resizing(widget: tkinter.Misc, row_weight: int = 1, column_weight: int = 1) -> None:
        """
        Enable a widget and all elements inside of it that have been placed
        using the grid method to resize. This must be called AFTER all widgets
        have been placed.
        :param widget: the widget to enable resizing on
        :param row_weight: the rate at which the rows expands. default 1
        :param column_weight: the rate at which the columns expands. default 1
        :return: None
        """
        for child in widget.grid_slaves():
            grid_info = child.grid_info()
            row, column = {grid_info["row"]}, {grid_info["column"]}
            widget.rowconfigure(row, weight=row_weight)
            widget.columnconfigure(column, weight=column_weight)
            ResizeableWindow._enable_resizing(child)
