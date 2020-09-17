import tkinter
import canvasapi
from tkinter import ttk
from tkinter import messagebox

from src.gui.convenience.resizeable_window import ResizeableWindow
from src.gui.convenience.tracked_items_list_box import TrackedItemListBox
from src.gui.convenience.tool_tip import CreateToolTip
from src.gui.convenience.canvas_related.assignment_dates import AssignmentDates
from src.gui.convenience.labeled_entry import LabeledEntry
from src.gui.convenience.progress_window import ProgressWindow
from src.gui.convenience.refreshable_items_list import RefreshableItemsList

from src.kudo_points.giving_quiz_creator.kudo_point_giving_quiz import KudoPointGivingQuiz


class KudoPointAssignmentCreationWindow(ResizeableWindow):

    def __init__(self, master=None, course: canvasapi.course.Course = None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.course = course

        self.group_categories_list_box = self.create_group_categories_list_box()
        self.group_categories_label = ttk.Label(self, text='Group Category to create Kudo Point Giving Assignment for')

        self.assignment_groups_list_box = self.create_assignment_groups_list_box()
        self.assignment_group_label = ttk.Label(self,
                                                text='Assignment Group to put the Kudo Point Giving Assignments in')

        self.dates = AssignmentDates(self)
        self.dates.set_default_dates()

        self.kudo_points = LabeledEntry(self, 'Number of Kudo Points each student can give', '3')
        self.kudo_points.entry['width'] = 2

        self.create_assignments_button = ttk.Button(self,
                                                    text='Create Kudo Point Giving Assignments',
                                                    command=self.create_assignments,
                                                    # TODO: enable input validation state='disabled'
                                                    )

        self.place_contents()

    def create_group_categories_list_box(self):
        group_categories = RefreshableItemsList(self, self.course.get_group_categories,
                                                list_box_configs={'height': 10, 'exportselection': False})

        CreateToolTip(group_categories,
                      'Create Kudo Point Giving Assignments for all groups in this Group Category,',
                      1000)
        group_categories.listbox.bind('<<ListboxSelect>>', self.enable_assignment_creation)
        group_categories.listbox.focus_set()
        return group_categories

    def create_assignment_groups_list_box(self):
        assignment_groups = RefreshableItemsList(self, self.course.get_assignment_groups,
                                                 list_box_configs={'height': 10, 'exportselection': False},
                                                 include_horizontal_scroll_bar=True,)

        CreateToolTip(assignment_groups,
                      'The Assignment Group the Kudo Point Giving Assignments should be placed under,',
                      1000)
        assignment_groups.listbox.bind('<<ListboxSelect>>', self.enable_assignment_creation)

        return assignment_groups

    def place_contents(self):
        self.group_categories_label.grid(row=0, column=0)
        self.group_categories_list_box.grid(row=1, column=0)

        self.assignment_group_label.grid(row=0, column=1)
        self.assignment_groups_list_box.grid(row=1, column=1)


        self.dates.grid(row=1, column=2)
        self.kudo_points.grid(row=2, column=2)
        self.create_assignments_button.grid(row=3, column=2)

    def refresh_group_categories(self):
        self.group_categories_list_box.values = self.course.get_group_categories()

    # self.create_assignments_button['state'] = 'disabled'

    def refresh_assignment_groups(self):
        self.assignment_groups_list_box.values = self.course.get_assignment_groups()
        # self.create_assignments_button['state'] = 'disabled'

    def create_assignments(self):
        groups = list(self.group_categories_list_box.get_selected_items()[0].get_groups())
        progress_tracker = ProgressWindow(self, total_work_to_do=len(groups))
        KudoPointGivingQuiz.create_kudo_point_giving_quiz_for_group_category(
            self.course,
            self.group_categories_list_box.listbox.get_selected_items()[0],
            self.assignment_groups_list_box.listbox.get_selected_items()[0],
            int(self.kudo_points.entry.get()),
            self.dates.due_date.get_datetime(),
            self.dates.unlock_date.get_datetime(),
            self.dates.lock_date.get_datetime(),
            on_group_start=lambda group: progress_tracker.set_text_progress(
                f'Creating Kudo Point Giving Assignments for Group: {group.name}'),
            on_group_end=lambda group: (progress_tracker.set_text_progress(
                f'Finished Creating Kudo Point Giving Assignments for Group : {group.name}'),
                                        progress_tracker.increment_work_done()),
            on_user_start=lambda user, group: progress_tracker.set_text_progress(
                f'Creating Kudo Point Giving Assignments for {user.name} in Group {group.name}'),
            on_user_end=lambda user, group: progress_tracker.set_text_progress(
                f'Finished Creating Kudo Point Giving Assignments for {user.name} in Group {group.name}')
        )

    def enable_assignment_creation(self, effect) -> None:
        """
        Check if all the information needed to create assignments has been entered
        and if so enable the assignment creation button
        :param effect:
        :return:
        """
        try:
            self.group_categories_list_box.listbox.curselection()[0]
            self.assignment_groups_list_box.listbox.curselection()[0]
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
