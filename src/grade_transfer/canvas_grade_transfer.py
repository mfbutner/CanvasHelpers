# Author: Qianhan Zhang


from canvasapi.course import Course
from canvasapi.assignment import Assignment
from canvasapi.user import User
import csv
from typing import List, Union
from src.grade_transfer.third_party_student import ThirdPartyStudent


class CanvasGradeTransfer:
    # csv_path because we still need to read the csv after knowing what the header situation is.
    def __init__(self, course: Course,
                 gui_list: List[Union[str, None, Assignment]],
                 csv_path: str):
        self.course = course
        self.csv_path = csv_path
        self.gui_list = gui_list
        self.third_party_students_full_name_pool = []
        self.third_party_students_last_name_pool = []
        self.canvas_students_full_name_pool = []
        self.canvas_students_last_name_pool = []
        self.grade_book = self.create_empty_grade_book()
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
                    elif key == "full_name":
                        first, last = self.split_name(cell)
                        student.first_name = first
                        student.last_name = last
                    elif key == "sid":
                        student.sid = cell
                    elif key == "email":
                        student.email = cell
                    elif type(key) == Assignment:
                        student.add_assignment(cell)
                student.set_full_name()
                student_set.add(student)
                self.third_party_students_full_name_pool.append(student.full_name)
                self.third_party_students_last_name_pool.append(student.last_name)
        return student_set

    def create_empty_grade_book(self):
        grade_book = {}
        for assignment in self.gui_list:
            if type(assignment) == Assignment:
                grade_book[assignment.id] = {}
        return grade_book

    def create_canvas_name_pool(self):
        for student in self.canvas_students:
            self.canvas_students_full_name_pool.append(student.sortable_name)
            self.canvas_students_last_name_pool.append(self.split_name(student.sortable_name)[1])
        return

    def match_students(self):
        # do all email matches
        for third_student in self.third_party_students:
            for canvas_student in self.canvas_students:
                self.email_check(third_student, canvas_student)
                if third_student.email_match:
                    break

        # do all student id matches but only for students we haven't already matched by email
        for third_student in self.third_party_students:
            if third_student.email_match:
                continue
            for canvas_student in self.canvas_students:
                self.sid_check(third_student, canvas_student)
                if third_student.sid_match:
                    break

        # now match students by full name but only if they haven't matched by email or sid
        for third_student in self.third_party_students:
            if third_student.email_match or third_student.sid_match:
                continue
            for canvas_student in self.canvas_students:
                self.full_name_check(third_student, canvas_student)
                if third_student.full_name_match:
                    break

        # now match students by last name but only if they haven't matched by email or sid or fullname
        for third_student in self.third_party_students:
            if third_student.email_match or third_student.sid_match or third_student.full_name_match:
                continue
            for canvas_student in self.canvas_students:
                self.last_name_check(third_student, canvas_student)
                if third_student.last_name_match:
                    break
        return

    def remove_from_name_pool(self, csv_student: ThirdPartyStudent, canvas_student: User):
        self.canvas_students_full_name_pool.remove(canvas_student.sortable_name)
        self.canvas_students_last_name_pool.remove(self.split_name(canvas_student.sortable_name)[1])
        self.third_party_students_full_name_pool.remove(csv_student.full_name)
        self.third_party_students_last_name_pool.remove(csv_student.last_name)
        return

    def is_unique(self, name: str, name_type: str):
        # type == "full" or "last"
        third_party_list = getattr(self, "third_party_students_" + name_type + "_name_pool").copy()
        canvas_list = getattr(self, "canvas_students_" + name_type + "_name_pool").copy()

        third_n = third_party_list.count(name)
        canvas_n = canvas_list.count(name)

        if (third_n == 1) and (canvas_n == 1):
            return True
        return False

    def email_check(self, csv_student: ThirdPartyStudent, canvas_student: User):
        if csv_student.email is not None and canvas_student.email is not None:
            if csv_student.email == canvas_student.email:
                csv_student.email_match = True
                self.remove_from_name_pool(csv_student, canvas_student)
        return

    def sid_check(self, csv_student: ThirdPartyStudent, canvas_student: User):
        if csv_student.sid is not None and canvas_student.sis_user_id is not None:
            try:
                csv_student_sid = int(csv_student.sid)
                canvas_student_sid = int(canvas_student.sis_user_id)
            except ValueError:
                return
            if csv_student_sid == canvas_student_sid:
                csv_student.sid_match = True
                self.remove_from_name_pool(csv_student, canvas_student)
        return

    def full_name_check(self, csv_student: ThirdPartyStudent, canvas_student: User):
        if csv_student.full_name is not None and canvas_student.sortable_name is not None:
            if csv_student.full_name == canvas_student.sortable_name:
                if self.is_unique(csv_student.full_name, "full"):
                    csv_student.full_name_match = True
        return

    def last_name_check(self, csv_student: ThirdPartyStudent, canvas_student: User):
        canvas_student_last_name = self.split_name(canvas_student.sortable_name)[1]
        if csv_student.last_name is not None and canvas_student_last_name is not None:
            if csv_student.last_name == canvas_student_last_name:
                if self.is_unique(csv_student.last_name, "last"):
                    csv_student.last_name_match = True
        return

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def split_name(full_name: str):
        if "," in full_name:
            last, first = full_name.split(",")
        elif " " in full_name:
            first, last = full_name.split(" ", 1)
        else:
            last = full_name
            first = None
            return first, last
        first = first.strip()
        last = last.strip()
        return first, last

    def update_grade_for_one(self, csv_student: ThirdPartyStudent, canvas_student: User):
        i = 0
        for grade in self.grade_book:
            self.grade_book[grade][canvas_student.id] = {"posted_grade": csv_student.assignment_list[i]}
            i += 1
        return

    def fill_in_grade_data(self):
        for student in self.third_party_students:
            if student.email_match:
                for c_student in self.canvas_students:
                    if (c_student.email is not None) and student.email == c_student.email:
                        self.update_grade_for_one(student, c_student)
                        break
            elif student.sid_match:
                for c_student in self.canvas_students:
                    if (c_student.sis_user_id is not None) and int(student.sid) == int(c_student.sis_user_id):
                        self.update_grade_for_one(student, c_student)
                        break
            elif student.manual_match:
                if student.full_name_match:
                    for c_student in self.canvas_students:
                        if (c_student.sortable_name is not None) and student.full_name == c_student.sortable_name:
                            self.update_grade_for_one(student, c_student)
                            break
                elif student.last_name_match:
                    for c_student in self.canvas_students:
                        c_student_last_name = self.split_name(c_student.sortable_name)[1]
                        if (c_student_last_name is not None) and student.last_name == c_student_last_name:
                            self.update_grade_for_one(student, c_student)
                            break
        return

    def bulk_update(self, assignment: Assignment):
        # print(self.grade_book[assignment.id])
        assignment.submissions_bulk_update(grade_data=self.grade_book[assignment.id])
        return

    def find_Canvas_student_info(self, name: str, name_type: str):
        for student in self.canvas_students:
            if name_type == "FULL":
                if student.sortable_name == name:
                    return [name, {"full_name": student.sortable_name, "sid": student.sis_user_id, "email": student.email}]
            elif name_type == "LAST":
                if self.split_name(student.sortable_name)[1] == name:
                    return [name, {"full_name": student.sortable_name, "sid": student.sis_user_id, "email": student.email}]
            else:
                return [None, {"full_name": None, "sid": None, "email": None}]

    def third_party_full_name_match(self):
        return {student.full_name: {"full_name": student.full_name, "sid": student.sid, "email": student.email}
                for student in self.third_party_students if student.full_name_match is True}

    def third_party_last_name_match(self):
        return {student.last_name: {"full_name": student.full_name, "sid": student.sid, "email": student.email}
                for student in self.third_party_students if student.last_name_match is True}

    def Canvas_name_match(self, name_type: str, student_dic: dict):
        Canvas_dic = {}
        for name in student_dic:
            Canvas_info = self.find_Canvas_student_info(name=name, name_type=name_type)
            Canvas_dic[Canvas_info[0]] = Canvas_info[1]
        return Canvas_dic

    def change_manual_update(self, third_party_dic: dict, name_type: str):
        if name_type == "FULL":
            third_party_student_name_check = [student for student in self.third_party_students if student.full_name_match is True]
        else:
            third_party_student_name_check = [student for student in self.third_party_students if student.last_name_match is True]
        for name in third_party_dic:
            for student in third_party_student_name_check:
                if (name == student.full_name and student.full_name_match is True) \
                        or (name == student.last_name and student.last_name_match is True):
                    student.manual_match = third_party_dic[name]["manual_match"]
        return

    def get_leftover_third_party_students(self):
        student_dic = {}
        for student in self.third_party_students:
            if not (student.sid_match or student.email_match or student.manual_match):
                student_dic[student.full_name] = {"sid": student.sid, "email": student.email}
        return student_dic


def is_unique_quick_check(list_a: list):
    if len(list_a) == len(set(list_a)):
        return True
    return False
