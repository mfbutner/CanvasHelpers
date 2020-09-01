import tkinter
from tkinter import ttk
from typing import Optional


class LabeledEntry:
    def __init__(self, label: ttk.Label, entry: ttk.Entry, entry_contents:tkinter.StringVar = None):
        self.label = label
        self.entry = entry
        self.entry_contents = entry_contents if entry_contents is not None else tkinter.StringVar()

