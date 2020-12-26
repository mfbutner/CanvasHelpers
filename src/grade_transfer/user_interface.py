# Author: Qianhan Zhang

import canvasapi
from src.grade_transfer.canvas_grade_transfer import CanvasGradeTransfer
from src.grade_transfer.third_party_student import ThirdPartyStudent
from typing import List
import csv
import itertools


class UserInterface:
    def __init__(self):
        self.url = self.get_url()
        self.token = self.get_token()
        self.canvas = canvasapi.Canvas(self.url, self.token)
        self.csv_path = self.get_csv_path()
        self.course = self.get_course()
        self.assignments = []
        self.get_assignments()
        self.csv_header = []
        self.csv_ncol = self.show_head()
        self.tell_me_about_header()
        self.grade_uploader = CanvasGradeTransfer(self.course, self.csv_header, self.csv_path)
        self.verify_name_checks(self.grade_uploader.third_party_students, "FULL")
        self.verify_name_checks(self.grade_uploader.third_party_students, "LAST")
        self.grade_uploader.fill_in_grade_data()
        self.update_grade()
        self.show_csv_leftover(self.grade_uploader.third_party_students)

    @staticmethod
    def get_url() -> str:
        print("*******************************************************************************************************")
        url = input("Please enter the Canvas url link: ")
        return url

    @staticmethod
    def get_token() -> str:
        print("*******************************************************************************************************")
        token = input("Please enter your Canvas token: ")
        return token

    @staticmethod
    def get_csv_path() -> str:
        print("*******************************************************************************************************")
        csv = input("Please specify the path to the third party CSV file from which you want to upload the grades: ")
        return csv

    @staticmethod
    def print_list_with_index(a_list: list):
        index = 1
        for item in a_list:
            print(str(index) + ": " + item.name)
            index += 1
        return

    @staticmethod
    def str_to_int(word: str):
        word = word.replace(" ", "")
        word = int(word)
        return word

    def separate_by_comma(self, user_input: str):
        input_list = user_input.split(",")
        for index, item in enumerate(input_list):
            input_list[index] = self.str_to_int(item)
        return input_list

    def get_course(self) -> canvasapi.course.Course:
        # EXCEPTION: If user choose out of bounds or enter non-number or empty space or more than one number
        print("*******************************************************************************************************")
        print("These are the available FAVORITE Canvas courses from your token and url.")
        self.print_list_with_index(self.canvas.get_current_user().get_favorite_courses())
        course_index = input("Please enter the index number in front of the course in which you want to manage the "
                             "grades: ")
        course_index = self.str_to_int(course_index)
        course_index -= 1
        course = self.canvas.get_current_user().get_favorite_courses()[course_index]
        return course

    def get_assignments(self):
        print("*******************************************************************************************************")
        print("These are the available ASSIGNMENT GROUPS in the Canvas course you just chose.")
        self.print_list_with_index(self.course.get_assignment_groups())
        assignment_groups = input("Please enter the index in front of the assignment GROUP(s) that you want to transfer"
                                  " grade from. If multiple, separate them with commas: ")
        assignment_groups = self.separate_by_comma(assignment_groups)
        for group in assignment_groups:
            id = self.course.get_assignment_groups().__getitem__(group-1).id
            self.get_each_assignments(id)

    def get_each_assignments(self, group_id: int):
        print("*******************************************************************************************************")
        group_name = self.course.get_assignment_group(group_id).name
        print("These are the available assignment(s) in the " + group_name + " you just chose.")
        self.print_list_with_index(self.course.get_assignments_for_group(group_id))
        assignment_index = input("Please enter the index number in front of the assignment(s) which you want to transfer"
                                 " grades from. If multiple, separate them with commas: ")
        assignment_list = self.separate_by_comma(assignment_index)
        for index in assignment_list:
            self.assignments.append(self.course.get_assignments_for_group(group_id)[index - 1])
        return

    # def get_assignments(self):
    #     # EXCEPTION: If user choose out of bounds or enter non-number or empty space or end with comma
    #     print("*******************************************************************************************************")
    #     print("These are the available Canvas assignments from your chosen class.")
    #     self.print_list_with_index(self.course.get_assignments())
    #     assignment_index = input("Please enter the index number in front of the assignment(s). If multiple, separate "
    #                              "them with commas: ")
    #     print(assignment_index)
    #     assignment_list = self.separate_by_comma(assignment_index)
    #     for index in assignment_list:
    #         self.assignments.append(self.course.get_assignments()[index - 1])
    #     return

    def show_head(self):
        print("*******************************************************************************************************")
        print("Below are the first 6 lines in " + self.csv_path + ": ")
        with open(self.csv_path) as csv_file:
            reader1, reader2 = itertools.tee(csv.reader(csv_file))
            n_col = len(next(reader1))
            del reader1
            for i, row in enumerate(reader2):
                print(row)
                if i >= 5:
                    break
        return n_col

    def tell_me_about_header(self):
        print("*******************************************************************************************************")
        print("Use the numbers in front of below key words to identify what's in the header, separated by comma(s):")
        print("NOTE: 0 (None) means to ignore this column because it is NOT important to this grade transfer. You can "
              "ONLY repeat 0, other numbers can be used AT MOST once.")
        print("0 None \n"
              "1 first_name\n"                                                                 
              "2 last_name\n"
              "3 full_name\n"
              "4 sid\n"
              "5 email")
        i = 6
        for assignment in self.assignments:
            print(str(i) + " " + assignment.name)
            i += 1

        input_header = input("Please categorize the columns: ")
        while len(input_header.split(",")) != self.csv_ncol:
            input_header = input("Please enter EXACTLY " + str(self.csv_ncol) + " numbers. One for each column in "
                                 + self.csv_path + ": ")

        input_header = self.separate_by_comma(input_header)
        self.decompose_input_header(input_header)
        return

    def decompose_input_header(self, input_header: list):
        for i in input_header:
            if i == 0:
                self.csv_header.append(None)
            elif i == 1:
                self.csv_header.append("first_name")
            elif i == 2:
                self.csv_header.append("last_name")
            elif i == 3:
                self.csv_header.append("full_name")
            elif i == 4:
                self.csv_header.append("sid")
            elif i == 5:
                self.csv_header.append("email")
            elif i > 5:
                self.csv_header.append(self.assignments[i-6])
        return

    def print_prompt_for_names(self, name_type: str):
        print("*******************************************************************************************************")
        print("ATTENTION: We suspect students below from " + self.csv_path + " match with the these "
              "from Canvas because they share the SAME UNIQUE ", name_type, " name after eliminating those who match "
              "absolutely (either by SID or EMAIL). Please help us verify one by one. If match, type \"yes\"; if not, "
              "type \"no\"")
        return

    def find_Canvas_student(self, name: str, n_type: str):
        for student in self.grade_uploader.canvas_students:
            if n_type == "FULL":
                if student.sortable_name == name:
                    return student
            if n_type == "LAST":
                if self.grade_uploader.split_name(student.sortable_name)[1] == name:
                    return student
        return

    @staticmethod
    def translate_yes_no_to_TF(user_input: str):
        if user_input == "yes":
            return True
        elif user_input == "no":
            return False
        return

    def verify_name_checks(self, student_list: List[ThirdPartyStudent], name_type: str):
        self.print_prompt_for_names(name_type)
        for student in student_list:
            if (student.full_name_match and name_type == "FULL") or (student.last_name_match and name_type == "LAST"):
                if name_type == "FULL":
                    search_name = student.full_name
                elif name_type == "LAST":
                    search_name = student.last_name
                print("***********************************************************************************************")
                print("From " + self.csv_path + ": ")
                print("Full name: " + student.full_name)
                print("SID: " + str(student.sid))
                print("Email: " + str(student.email))
                print("")
                canvas_student = self.find_Canvas_student(search_name, name_type)
                print("From Canvas: ")
                print("Full name: " + canvas_student.sortable_name)
                print("SID: " + str(canvas_student.sis_user_id))
                print("Email: " + str(canvas_student.email))
                print("")
                user_check = input("Are they the same student? (yes or no): ")
                student.manual_match = self.translate_yes_no_to_TF(user_check)
        return


    def update_grade(self):
        print("*******************************************************************************************************")
        print("Now upload the grades. Please be patient")
        for assignment in self.assignments:
            self.grade_uploader.bulk_update(assignment)
            print("Finished updating " + assignment.name + ".")
            print("***********************************************************************************************")
        print("Finished updating ALL grades in assignment_list")


    def show_csv_leftover(self, student_list: List[ThirdPartyStudent]):
        print("*******************************************************************************************************")
        print("These are the students in " + self.csv_path + " who didn't get their grades transferred this time.")
        print("")
        for student in student_list:
            if not(student.sid_match or student.email_match or student.manual_match):
                print("Full name: " + student.full_name)
                print("SID: " + str(student.sid))
                print("Email: " + str(student.email))
                print("")
                # repeat function in verify_name_check

