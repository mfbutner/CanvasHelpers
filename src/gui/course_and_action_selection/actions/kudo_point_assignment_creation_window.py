import tkinter
import canvasapi
from tkinter import ttk
from tkinter import messagebox

from src.gui.convenience.resizeable_window import ResizeableWindow
from src.gui.convenience.tracked_items_list_box import TrackedItemListBox
from src.gui.convenience.tool_tip import CreateToolTip
from src.gui.convenience.canvas_related.assignment_dates import AssignmentDates


class KudoPointAssignmentCreationWindow(ResizeableWindow):

    def __init__(self, course: canvasapi.course.Course, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.course = course

        self.group_categories_list_box = self.create_group_categories_list_box()
        self.group_categories_label = ttk.Label(self, text='Group Category to create Kudo Point Giving Assignment for')
        self.group_category_refresh_button = ttk.Button(self, text='Refresh', command=self.refresh_group_categories)

        self.assignment_groups_list_box = self.create_assignment_groups_list_box()
        self.assignment_group_label = ttk.Label(self,
                                                text='Assignment Group to put the Kudo Point Giving Assignments in')
        self.assignment_group_category_refresh_button = ttk.Button(self, text='Refresh',
                                                                   command=self.refresh_assignment_groups)

        self.dates = AssignmentDates(self)
        self.dates.set_default_dates()

        self.create_assignments_button = ttk.Button(self,
                                                    text='Create Kudo Point Giving Assignments',
                                                    command=self.create_assignments,
                                                    state='disabled'
                                                    )
        self.bind('<<TIME_CHANGED>>', lambda time: print(f'The time changed to {time.widget.get_time()}'))
        self.place_contents()

    def create_group_categories_list_box(self):
        group_categories = TrackedItemListBox(self, self.course.get_group_categories(), height=10)
        CreateToolTip(group_categories,
                      'Create Kudo Point Giving Assignments for all groups in this Group Category,',
                      1000)
        group_categories.bind('<<ListboxSelect>>', self.enable_assignment_creation)
        group_categories.focus_set()
        return group_categories

    def create_assignment_groups_list_box(self):
        assignment_groups = TrackedItemListBox(self, self.course.get_assignment_groups(), height=10)
        CreateToolTip(assignment_groups,
                      'The Assignment Group the Kudo Point Giving Assignments should be placed under,',
                      1000)
        assignment_groups.bind('<<ListboxSelect>>', self.enable_assignment_creation)

        return assignment_groups

    def place_contents(self):
        self.group_categories_label.grid(row=0, column=0)
        self.group_categories_list_box.grid(row=1, column=0)
        self.group_category_refresh_button.grid(row=2, column=0)

        self.assignment_group_label.grid(row=0, column=1)
        self.assignment_groups_list_box.grid(row=1, column=1)
        self.assignment_group_category_refresh_button.grid(row=2, column=1)

        self.dates.grid(row=1, column=2)
        self.create_assignments_button.grid(row=3, column=2)

    def refresh_group_categories(self):
        self.group_categories_list_box.values = self.course.get_group_categories()
        self.create_assignments_button['state'] = 'disabled'

    def refresh_assignment_groups(self):
        self.assignment_groups_list_box.values = self.course.get_assignment_groups()
        self.create_assignments_button['state'] = 'disabled'

    def create_assignments(self):
        print(self.group_categories_list_box.curselection())

    def enable_assignment_creation(self, effect) -> None:
        """
        Check if all the information needed to create assignments has been entered
        and if so enable the assignment creation button
        :param effect:
        :return:
        """
        try:
            self.group_categories_list_box.curselection()[0]
            self.assignment_groups_list_box.curselection()[0]
        except IndexError:
            self.create_assignments_button['state'] = 'disabled'
            return
        try:
            self.dates.due_date.get_datetime()
            self.dates.unlock_date.get_datetime()
            self.dates.lock_date.get_datetime()
        except ValueError:
            self.create_assignments_button['state'] = 'disabled'
            return

        self.create_assignments_button['state'] = 'normal'
