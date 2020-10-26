# Author: Qianhan Zhang

import canvasapi
from src.grade_transfer.canvas_grade_transfer import CanvasGradeTransfer
from typing import List


def print_prompt_for_names(name_type: str):
    print("************* ATTENTION: We suspect students below from the third party csv file match with the students "
          "from Canvas because they share the SAME UNIQUE ", name_type, " names after eliminating those who match "
                                                                        "absolutely (either by SID or EMAIL. Please help us verify. *************\n")
    return


class UserInterface:
    def __init__(self):
        self.url = self.get_url()
        self.token = self.get_token()
        self.csv_path = self.get_csv_path()
        self.canvas = canvasapi.Canvas(self.url, self.token)
        self.course = self.get_course()
        self.assignments = []
        self.get_assignments()
        self.csv_header = []
        self.tell_me_about_header()

    @staticmethod
    def get_url() -> str:
        url = input("Please enter the Canvas url link: ")
        return url

    @staticmethod
    def get_token() -> str:
        token = input("Please enter your Canvas token: ")
        return token

    @staticmethod
    def get_csv_path() -> str:
        csv = input("Please specify the path to the third party CSV file from which you want to upload the grades: ")
        return csv

    @staticmethod
    def print_list_with_index(a_list: list):
        index = 1
        for item in a_list:
            print(str(index) + ": " + item)
            index += 1
        return

    @staticmethod
    def separate_by_comma():
        pass

    def get_course(self) -> canvasapi.course.Course:
        print("These are the available Canvas courses from your token and url.")
        self.print_list_with_index(self.canvas.get_courses())
        course_index = input("Please enter the index number in front of the course in which you want to manage the "
                             "grades: ")
        course_index -= 1
        course = self.canvas.get_courses()[course_index]
        return course

    def get_assignments(self):
        print("These are the available Canvas assignments from your chosen class.")
        self.print_list_with_index(self.course.get_assignments())
        assignment_index = input("Please enter the index number in front of the assignment(s). If multiple, separate "
                                 "them with a comma: ")



    def tell_me_about_header(self):
        pass



    def verify_name_checks(self, student_list: List[CanvasGradeTransfer.third_party_students]):
        for student in student_list:
            if student.full_name_match:
                print_prompt_for_names("FULL")


