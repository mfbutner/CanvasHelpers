# Author: Qianhan Zhang

import canvasapi
import csv
from typing import List, Union
from src.grade_transfer.third_party_student import ThirdPartyStudent


class CanvasGradeTransfer:
    # csv_path because we still need to read the csv after knowing what the header situation is.
    def __init__(self, course: canvasapi.course.Course,
                 gui_list: List[Union[str, None, canvasapi.assignment.Assignment]],
                 csv_path: str):
        self.course = course
        self.csv_path = csv_path
        self.gui_list = gui_list
        self.third_party_students_full_name_pool = []
        self.third_party_students_last_name_pool = []
        self.canvas_students_full_name_pool = []
        self.canvas_students_last_name_pool = []
        # gui_list = ["first_name", "last_name", "email", None, assignment1, assignment2]
        self.third_party_students = self.create_third_party_student_list()
        self.canvas_students = set(course.get_users(enrollment_type=["student"]))
        self.create_canvas_name_pool()
        self.match_students()

    def create_third_party_student_list(self):
        student_set = set()
        with open(self.csv_path, newline='') as file:
            reader = csv.reader(file, delimiter=',')
            next(reader)
            for row in reader:
                student = ThirdPartyStudent()
                for key, cell in zip(self.gui_list, row):
                    if key == "first_name":
                        student.first_name = cell
                    elif key == "last_name":
                        student.last_name = cell
                    elif key == "name":
                        first, last = split_name(cell)
                        student.first_name = first
                        student.last_name = last
                    elif key == "sid":
                        student.sid = cell
                    elif key == "email":
                        student.email = cell
                    elif type(key) == canvasapi.assignment.Assignment:
                        student.add_assignment(cell)
                student.set_full_name()
                student_set.add(student)
                self.third_party_students_full_name_pool.append(student.full_name)
                self.third_party_students_last_name_pool.append(student.last_name)
        return student_set

    def create_canvas_name_pool(self):
        for student in self.canvas_students:
            self.canvas_students_full_name_pool.append(student.sortable_name)
            self.canvas_students_last_name_pool.append(split_name(student.sortable_name)[1])
        return

    def match_students(self):
        for third_student in self.third_party_students:
            for canvas_student in self.canvas_students:
                self.email_check(third_student, canvas_student)
                if not third_student.email_match:
                    self.sid_check(third_student, canvas_student)
                    if not third_student.sid_match:
                        self.full_name_check(third_student, canvas_student)
                        if not third_student.full_name_match:
                            self.last_name_check(third_student, canvas_student)
        return

    def remove_from_name_pool(self, csv_student: ThirdPartyStudent, canvas_student: canvasapi.user.User):
        self.canvas_students_full_name_pool.remove(canvas_student.sortable_name)
        self.canvas_students_last_name_pool.remove(split_name(canvas_student.sortable_name)[1])
        self.third_party_students_full_name_pool.remove(csv_student.full_name)
        self.third_party_students_last_name_pool.remove(csv_student.last_name)
        return

    def is_unique(self, name: str, type: str):
        # type == "full" or "last"
        third_party_list = getattr(self, "third_party_students_" + type + "_name_pool").copy()
        canvas_list = getattr(self, "canvas_students_" + type + "_name_pool").copy()
        if is_unique_quick_check(third_party_list) and is_unique_quick_check(canvas_list):
            return True
        else:
            third_party_list.remove(name)
            canvas_list.remove(name)
            if is_unique_quick_check(third_party_list) and is_unique_quick_check(canvas_list):
                return False
        return True

    def email_check(self, csv_student: ThirdPartyStudent, canvas_student: canvasapi.user.User):
        if csv_student.email is not None:
            if csv_student.email == canvas_student.email:
                csv_student.email_match = True
                self.remove_from_name_pool(csv_student, canvas_student)
        return

    def sid_check(self, csv_student: ThirdPartyStudent, canvas_student: canvasapi.user.User):
        if csv_student.sid is not None:
            if int(csv_student.sid) == canvas_student.sis_user_id:
                csv_student.sid_match = True
                self.remove_from_name_pool(csv_student, canvas_student)
        return

    def full_name_check(self, csv_student: ThirdPartyStudent, canvas_student: canvasapi.user.User):
        if csv_student.full_name is not None:
            if csv_student.full_name == canvas_student.sortable_name:
                if self.is_unique(csv_student.full_name, "full"):
                    csv_student.full_name_match = True
        return

    def last_name_check(self, csv_student: ThirdPartyStudent, canvas_student: canvasapi.user.User):
        if csv_student.last_name is not None:
            if csv_student.last_name == split_name(canvas_student.sortable_name)[1]:
                if self.is_unique(csv_student.last_name, "last"):
                    csv_student.last_name_match = True
        return

    def __str__(self):
        return str(self.__dict__)


def split_name(full_name: str):
    if "," in full_name:
        last, first = full_name.split(",")
    elif " " in full_name:
        first, last = full_name.split(" ", 1)
    first = first.strip()
    last = last.strip()
    return first, last


def is_unique_quick_check(list_a: list):
    if len(list_a) == len(set(list_a)):
        return True
    return False
