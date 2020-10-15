# Author: Qianhan Zhang

# GUI part 1: "Tell me about this csv": Given a preview of the first 10 rows of the 3rd party csv (ex: mimir), user drag
#             and drop which row is STUDENTS: "first_name", "last_name", "NAME" (MAY separate by comma OR whitespace,
#             worry about it later), "email", "SID", HOMEWORK: homework1, QUIZ: quiz1, quiz2, EXAM: midterm1, final etc.
#             NOTE: User MUST match AT LEAST one of the columns to move on: "first_name" AND "last_name", "name", "SID",
#             "email"
#
# GUI part 2: "How to match the rest": After 1st and 2nd degree matches, show user the leftover from both
#             lists (Canvas student list: first_name, last_name, school_email, SID; 3rd party csv: name, Or, first_name,
#             last_name, email, SID (whichever is available). Let canvas list be on the left, 3rd party csv rows be on
#             the right, and let user drag and drop the matching rows from both sides to the box below them. After user
#             finish matching, whatever left in both sides should be disregarded.
#             NOTE: There will be some pre-matched results from 2nd degree match (unique leftover full name and unique
#             leftover last name) in the below box. Ask user to VERIFY the pre-matched results.


# Part 1: Don't need to ask for canvas list, I was already given Canvas course object. Can use canvas course object to
#         do the additional query (student list, assignments, etc)

# Part 2: Ask for the 3rd party csv address (GUI!!!!! THIS IS GUI!!!!! Make it look like when word doc asks for document
#         location.) Actually it is a part of Gui part 1.

# Part 3: "Tell me about this csv" (GUI part 1)

# Part 4: Match by Email (1st degree match)

# Part 5: Match by SID, IF SID is available (Continue 1st degree match)

# Part 6: Match by unique full name after 1st degree match (2nd degree match) (######## Put the result in the below box)

# Part 7: Match by unique last name after 1nd degree match (Continue 2rd degree match) (######## Put the result in the
#         below box)

# Part 8: "How to match the rest" (GUI part 2)

# Part 9: Upload the grades to Canvas


# NOTE: 1. First Gui part 1, then this logic program (start.py), so CanvasGradeTransfer instance only exits AFTER Gui
#          part1 hits "play", therefore you will have everything (course_name, email_index, name_index,
#          assignment1_index, etc.) and you can use this list to create the logic instance.

#       2. Gui part1 returns a list of mix of strings ("First_name", "Last_name", "email", "SID") and NA (placeholders,
#          columns that we are not using), and instances of Canvas assignments. Only Canvas assignments are instances of
#          class because name column (for example) in csv doesn't represent a unique entity (names for multiple
#          students, grades are all for the same assignment)

#       3. Gui gets a course, and it downloads the available assignments in that course, so the drag and drop can tell
#          me which column is canvas.course.assignment1.

#       4. Want to avoid asking Canvas stuff. If already asked before, better to pass the info through instead of asking
#          Canvas again.
#
#       5. Gui part1 takes the Canvas course as argument and in Gui part1 we ask CanvasAPI for assignment_group. For
#          each assignment group (quiz, exam, projects, ...), ask for specific assignment names.
#
#       6. Gui part1 will NOT be in this file, it will be on its own file under "GUI" directory.
#
#       7. CanvasGradeTransfer should NEVER receive an instance of Gui_part1 class. Should write start.py as if
#          gui_part1 doesn't exit (don't know it exists as in logic wise, like that index_list can be passed from
#          anywhere).


# "command + option + L" to make the code looks nice

# Questions for the meeting:
# 1. When to make a function static?
# 2. When to make a function away from class?

import canvasapi
import csv
from typing import List, Union


class ThirdPartyStudent:
    def __init__(self, first_name=None, last_name=None, sid=None, email=None, assignment=None, full_name=None):
        self.first_name = first_name
        self.last_name = last_name
        self.sid = sid
        self.email = email
        self.full_name = full_name
        self.assignment_list = []
        self.email_match = False
        self.sid_match = False
        self.full_name_match = False
        self.last_name_match = False
        self.manual_match = False

    def set_full_name(self):
        if (self.last_name is None) and (self.first_name is None):
            name = None
        elif self.last_name is None:
            name = ", " + self.first_name
        elif self.first_name is None:
            name = self.last_name + ", "
        else:
            name = self.last_name + ", " + self.first_name
        self.full_name = name
        return

    def add_assignment(self, assignment):
        self.assignment_list.append(assignment)

    def __str__(self):
        return str(self.__dict__)


# class CanvasStudents:
#     def __init__(self, course: canvasapi.course.Course, canvas: canvasapi.canvas.Canvas):
#         for course in canvas.get_courses():
#             for student in course.get_users(enrollment_type=["student"]):
#                 print(student.name, student.email)
#                 print(student.sortable_name)


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
        self.canvas_students_full_name_pool.remove(split_name(canvas_student.sortable_name)[1])
        self.third_party_students_full_name_pool.remove(csv_student.full_name)
        self.third_party_students_last_name_pool.remove(csv_student.last_name)
        return

    # I LEFT AT HERE
    def is_unique(self, name: str, type: str):
        # type == "full" or "last"
        if len(getattr(self, "third_party_students_" + type + "_name_pool")) == len(set(getattr(self, "canvas_students_"
                                                                                               + type + "_name_pool"))):
            return True
        else:
            third_party_without = self.th
                seen = set()
                return not any(i in seen or seen.add(i) for i in )

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
                csv_student.full_name_match = True
        return

    def last_name_check(self, csv_student: ThirdPartyStudent, canvas_student: canvasapi.user.User):
        if csv_student.last_name is not None:
            if csv_student.last_name == split_name(canvas_student.sortable_name)[1]:
                csv_student.last_name_match = True
        return

    def verify_name_checks(self):
        for student in self.third_party_students:
            if student.full_name_match:
                print("************* ATTENTION: Students below have the UNIQUE same names in both Canvas and the third "
                      "party grade website, BUT")


    def print_prompt_for_names(self, name_type:str):
        print("************* ATTENTION: Students below have the UNIQUE same names in both Canvas and the third party grade website, BUT")


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
