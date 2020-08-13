import tkinter
from tkinter import ttk
from typing import List, Dict

import canvasapi
import enum

from src.canvas_adapters.term import Term
from src.utilities.canvas_util import get_courses_enrolled_in_by_role, CanvasRole


class CourseTreeTags(enum.Enum):
    FOLDER = 'folder'
    COURSE = 'course'


class CourseSelectionTree(ttk.Treeview):
    teaching_roles = (CanvasRole.TEACHER, CanvasRole.TA, CanvasRole.DESIGNER)

    def __init__(self, canvas_connection: canvasapi.Canvas,
                 master=None, **kw):
        super().__init__(master, **kw)
        # self['selectmode'] = 'browse'
        # self['sticky'] = tkinter.NSEW

        # gui elements
        self.scroll_bar = ttk.Scrollbar(master, orient='vertical', command=self.yview)
        self['yscrollcommand'] = self.scroll_bar.set

        # logic
        self.canvas_connection = canvas_connection
        self.favorite_courses = self.download_favorite_courses()
        self.all_courses = self.download_all_courses()
        self.term_to_courses = self.build_term_to_course_mapping()
        self.id_to_course: Dict[str, canvasapi.course.Course] = dict()
        self.build_tree()
        self.selected_course = None

    # gui elements

    def build_tree(self) -> None:
        self.add_favorite_courses_to_tree()
        self.add_all_courses_to_tree()
        self.tag_bind(CourseTreeTags.COURSE, '<<TreeviewSelect>>', self.get_course_selected)

    def add_favorite_courses_to_tree(self) -> None:
        self.insert('', 0, iid='favorites_folder', text='Favorites', tags=(CourseTreeTags.FOLDER,), open=True)
        for course in self.favorite_courses:
            tree_id = self.insert('favorites_folder', 'end', text=course.name, tags=(CourseTreeTags.COURSE,))
            self.id_to_course[tree_id] = course

    def add_all_courses_to_tree(self) -> None:
        self.insert('', 'end', iid='all_courses_folder', text='All Courses', tags=(CourseTreeTags.FOLDER,))
        for term in sorted(self.term_to_courses, reverse=True):
            term_id = self.insert('all_courses_folder', 'end', text=term.name, tags=(CourseTreeTags.FOLDER,))
            for course in self.term_to_courses[term]:
                tree_id = self.insert(term_id, 'end', text=course.name, tags=(CourseTreeTags.COURSE,))
                self.id_to_course[tree_id] = course

    def get_course_selected(self, *args):
        selected_item_id = self.focus()
        self.selected_course = self.id_to_course[selected_item_id]
        print(f'{self.selected_course.name} selected')

    # logic

    def download_favorite_courses(self) -> List[canvasapi.course.Course]:
        me = self.canvas_connection.get_current_user()
        courses = get_courses_enrolled_in_by_role(me.get_favorite_courses, self.teaching_roles, include=['term'])
        for course in courses:
            course.term = Term(course.term)  # convert all of the term dictionaries to objects
        courses.sort(key=lambda course: course.name)
        return courses

    def download_all_courses(self) -> List[canvasapi.course.Course]:
        courses = get_courses_enrolled_in_by_role(
            self.canvas_connection.get_courses, self.teaching_roles, include=['term'])
        for course in courses:
            course.term = Term(course.term)  # convert all of the term dictionaries to objects
        return courses

    def build_term_to_course_mapping(self) -> Dict[Term, List[canvasapi.course.Course]]:
        term_to_course = dict()
        for course in self.all_courses:
            if course.term in term_to_course:
                term_to_course[course.term].append(course)
            else:
                term_to_course[course.term] = [course]

        for courses in term_to_course.values():
            courses.sort(key=lambda course: course.name)

        return term_to_course

    # def build_id_to_course_mapping(self) -> Dict[int, canvasapi.course.Course]:
    #     return {course.id: course for course in self.all_courses}
