"""
tkentrycomplete.py

A tkinter widget that features autocompletion.

Created by Mitja Martini on 2008-11-29.
Updated by Russell Adams, 2011/01/24 to support Python 3 and Combobox.
Updated by Dominic Kexel to use tkinter and ttk instead of tkinter and tkinter.ttk
   Licensed same as original (not specified?), or public domain, whichever is less restrictive.
"""
import tkinter
from tkinter import ttk

__version__ = "1.1"

# I may have broken the unicode...
Tkinter_umlauts = ['odiaeresis', 'adiaeresis', 'udiaeresis', 'Odiaeresis', 'Adiaeresis', 'Udiaeresis', 'ssharp']


class AutocompleteCombobox(ttk.Combobox):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.currently_dropping_down = False
        #this stuff causes the drop down box to appear when you click on the text box portion
        # self.bind('<FocusIn>', self.drop_up_down, add=True)
        # self.bind('<1>', self.drop_up_down)
        # self.bind('<FocusOut>', self.stop_dropping_down, add=True)

    def stop_dropping_down(self, *args):
        try:
            self.focus_get()
            self.currently_dropping_down = False
        except KeyError as error:
            if not (len(error.args) == 1 and error.args[0] == 'popdown'):
                raise error

        # print(f'Focus Lost: {self.master.focus_get()}')

    def drop_up_down(self, event):
        print(f'inside callback: {self.focus_get()}')
        if event.type == tkinter.EventType.ButtonPress and self.focus_get() is not self:
            return
        if self.currently_dropping_down:
            self.currently_dropping_down = False
            self.event_generate('<Escape>')
        else:
            self.currently_dropping_down = True
            self.event_generate('<Down>')

    def set_completion_list(self, completion_list):
        """Use our completion list as our drop down selection menu, arrows move through menu."""
        self._completion_list = sorted(completion_list, key=str.lower)  # Work with a sorted list
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list  # Setup our popup menu

    def autocomplete(self, delta=0):
        """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
        if delta:  # need to delete selection otherwise we would fix the current position
            self.delete(self.position, tkinter.END)
        else:  # set position to end so selection starts where textentry ended
            self.position = len(self.get())
        # collect hits
        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.get().lower()):  # Match case insensitively
                _hits.append(element)
        # if we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        # only allow cycling if we are in a known hit list
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        # now finally perform the auto completion
        if self._hits:
            self.delete(0, tkinter.END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, tkinter.END)

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        if event.keysym == "BackSpace":
            self.delete(self.index(tkinter.INSERT), tkinter.END)
            self.position = self.index(tkinter.END)
        if event.keysym == "Left" and self.select_present(): # added checking for selection before left arrow deletes
            if self.position < self.index(tkinter.END):  # delete the selection
                self.delete(self.position, tkinter.END)
            else:
                self.position = self.position - 1  # delete one character
                self.delete(self.position, tkinter.END)
        if event.keysym == "Right":
            self.position = self.index(tkinter.END)  # go to end (no selection)
        if len(event.keysym) == 1:
            self.autocomplete()
        # No need for up/down, we'll jump to the popup
        # list at the position of the autocompletion
