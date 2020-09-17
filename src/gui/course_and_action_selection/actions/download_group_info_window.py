import tkinter
from tkinter import ttk
from tkinter import filedialog
from typing import List
import canvasapi
import datetime

from src.gui.convenience.resizeable_window import ResizeableWindow
from src.gui.convenience.tool_tip import CreateToolTip
from src.gui.convenience.refreshable_items_list import RefreshableItemsList
from src.gui.convenience.button_group import ButtonGroup

from src.kudo_points.groups.groups import download_groups_to_csv


class ButtonFieldLink:

    def __init__(self, button_text: str, field_name: str, include_field_in_download: bool = False) -> None:
        super().__init__()
        self.button_text = button_text
        self.field_name = field_name
        self.include_field_in_download = include_field_in_download


class DownloadGroupInfoWindow(ResizeableWindow):
    def __init__(self, master=None, course: canvasapi.course.Course = None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.course = course
        self.button_field_links = self.create_button_field_links()
        self.download_options = self.create_download_options()
        self.group_categories_list_box = self.create_group_categories_list_box()
        self.download_button = ttk.Button(self, text='Download', command=self.download_groups)
        self.place_contents()

    @staticmethod
    def create_button_field_links() -> List[ButtonFieldLink]:
        return [
            ButtonFieldLink('Email', 'login_id', True),
            ButtonFieldLink('Name', 'sortable_name', False),
            ButtonFieldLink('Student Id', 'sis_user_id', False),
            ButtonFieldLink('Canvas Id', 'id', False)
        ]

    def _make_command_function(self, button_link, button, button_value):
        return lambda: self.update_includes(button_link, button, button_value)

    def create_download_options(self):
        button_configs = [{'text': button_link.button_text}
                          for button_link in self.button_field_links]
        download_options = ButtonGroup(self, text='Include', button_type=ttk.Checkbutton,
                                       button_configs=button_configs, orientation=tkinter.VERTICAL)

        for button_link, (button, button_value) in zip(self.button_field_links, download_options):
            button['command'] = self._make_command_function(button_link, button, button_value)
            if button_link.include_field_in_download:
                button_value.set(button['onvalue'])

        return download_options

    def create_group_categories_list_box(self):
        group_categories = RefreshableItemsList(self, self.course.get_group_categories,
                                                list_box_configs={'height': 10, 'exportselection': False})

        CreateToolTip(group_categories,
                      'Create Kudo Point Giving Assignments for all groups in this Group Category,',
                      1000)
        # group_categories.listbox.bind('<<ListboxSelect>>', self.enable_assignment_creation)
        group_categories.listbox.focus_set()
        return group_categories

    def place_contents(self):
        self.group_categories_list_box.grid(row=1, column=0, sticky=tkinter.NS)
        self.download_options.grid(row=1, column=1, sticky=tkinter.EW)
        self.download_button.grid(row=2, column=0, columnspan=2)

    def update_includes(self, button_link: ButtonFieldLink, checkbutton: ttk.Checkbutton,
                        button_value: tkinter.StringVar):
        button_link.include_field_in_download = button_value.get() == checkbutton['onvalue']

    def download_groups(self):
        group_category = self.group_categories_list_box.listbox.get_selected_items()[0]
        now = datetime.datetime.now()
        default_file_name = f'{self.course.name}-{group_category.name}-{now.strftime("%m-%d-%Y")}'
        csv_path = filedialog.asksaveasfilename(initialfile=default_file_name,
                                                defaultextension='csv', filetypes=[('CSV Files', '*.csv')])
        if csv_path:  # user did not cancel
            headers = self._create_headers()
            headers.insert(0, 'Group Name')
            user_fields = self._create_user_fields()
            download_groups_to_csv(group_category,
                                   csv_path,
                                   headers=headers,
                                   user_fields_to_include=user_fields)

    def _create_headers(self) -> List[str]:
        headers = []
        for button_link in self.button_field_links:
            if button_link.include_field_in_download:
                if button_link.button_text == 'Name':
                    headers.extend(['Last Name', 'First Name'])
                else:
                    headers.append(button_link.button_text)
        return headers

    def _create_user_fields(self) -> List[str]:
        fields = []
        for button_link in self.button_field_links:
            if button_link.include_field_in_download:
                if button_link.button_text == 'Name':
                    fields.extend(['last_name', 'first_name'])
                else:
                    fields.append(button_link.field_name)
        return fields
