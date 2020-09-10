import tkinter
from tkinter import ttk
from typing import Optional, Callable


class ProgressWindow(tkinter.Toplevel):
    def __init__(self, master=None, work_completed: float = 0,
                 initial_progress_text: str = '',
                 total_work_to_do: float = 100,
                 width: int = 500,
                 cancel_command=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)

        self.text_progress = ttk.Label(self)
        self.text_progress.content = tkinter.StringVar(self.text_progress, value=initial_progress_text)
        self.text_progress['textvariable'] = self.text_progress.content

        self.work_completed = tkinter.DoubleVar(value=work_completed)
        self.progress_bar = ttk.Progressbar(self, mode='determinate',
                                            orient='horizontal', length=width,
                                            variable=self.work_completed,
                                            maximum=total_work_to_do)

        self.cancel_button = ttk.Button(self, text='Cancel')
        self.set_cancel_command(cancel_command)

        self.place_content()

        self.grab_set()  # make it so that the user cannot interact with other windows

    def place_content(self):
        self.text_progress.grid(row=0, column=0)
        self.progress_bar.grid(row=1, column=0)
        self.cancel_button.grid(row=2, column=0)

        if not self.text_progress.content.get():
            self.text_progress.grid_remove()

    def get_progress_text(self) -> str:
        return self.text_progress.content.get()

    def set_text_progress(self, text: str) -> None:
        self.text_progress.content.set(text)
        if self.get_progress_text():
            self.text_progress.grid()
        else:
            self.text_progress.grid_remove()

    def get_work_done(self) -> float:
        return self.work_completed.get()

    def set_work_done(self, amount: float) -> None:
        self.work_completed.set(amount)
        if amount >= float(self.progress_bar['maximum']):
            self.grab_release()
            self.destroy()

    def increment_work_done(self, amount: float = 1) -> None:
        self.set_work_done(self.get_work_done() + amount)

    def set_cancel_command(self, cancel_command: Optional[Callable[[], Optional[str]]]) -> None:
        def resume():
            self.grab_release()
            return_val = cancel_command() if cancel_command is not None else None
            self.destroy()
            return return_val

        self.cancel_button['command'] = resume
