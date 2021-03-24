# Author: Qianhan Zhang


from canvasapi.course import Course
from canvasapi.canvas import Canvas
from canvasapi.assignment import Assignment
from typing import List
import csv
import itertools
from collections import Counter


class UserInterface:

    @staticmethod
    def line_separator():
        print("*******************************************************************************************************")
        return

    @staticmethod
    def sub_line_separator():
        print("***********************************************************************************************")
        return

    def build_canvas_connection(self) -> Canvas:
        self.line_separator()
        while True:
            try:
                url = input("Please enter the Canvas url (example: https://canvas.ucdavis.edu/): ")
                token = input("Please enter your Canvas token: ")
                connection = Canvas(url, token)
                # Check if url and token match
                connection.get_current_user()
            except (UserWarning, ValueError) as e:
                print(e)
            else:
                return connection

    def get_csv_path(self) -> str:
        self.line_separator()
        while True:
            try:
                csv_path = input("Please specify the path to the third party CSV file from which you want to upload "
                                 "the grades: ")
                # Check if 1.the file exits; 2.it has read permission; 3.it is unifomally coded
                with open(csv_path) as file:
                    for row in file:
                        pass
            except Exception as e:
                print(e)
            else:
                return csv_path

    @staticmethod
    def print_list_with_index(a_list: list) -> int:
        # List index starts with 1
        index = 0
        for item in a_list:
            index += 1
            print(str(index) + ": " + item.name)
        return index

    @staticmethod
    def is_int(user_input: str) -> bool:
        try:
            user_input = int(user_input)
        except ValueError as e:
            print(e)
            return False
        return True

    @staticmethod
    def get_user_input_int(start_point: int, end_point: int, prompt: str, comma_allowed: bool):
        while True:
            user_input = input(prompt)
            if not comma_allowed:
                if UserInterface.verify_user_input(start_point, end_point, user_input):
                    return int(user_input)
            else:
                user_input = user_input.split(",")
                if all((UserInterface.verify_user_input(start_point, end_point, element)) for element in user_input):
                    return [int(element) for element in user_input]

    @staticmethod
    def verify_user_input(start_point: int, end_point: int, user_input: str):
        if UserInterface.is_int(user_input):
            if UserInterface.is_in_range(start_point, end_point, int(user_input)):
                return True
            else:
                print("Please enter a number between ", start_point, "and ", end_point)
                return False
        else:
            return False

    @staticmethod
    def get_user_input_key_words(allowed_key_words: List[str], prompt: str) -> str:
        while True:
            user_input = input(prompt)
            if user_input in allowed_key_words:
                return user_input
            else:
                print("Please only enter the allowed key words:", allowed_key_words)

    @staticmethod
    def is_in_range(start: int, end: int, user_input: int) -> bool:
        if (user_input < start) or (user_input > end):
            return False
        return True

    def print_favorite_courses(self, canvas: Canvas) -> int:
        print("These are your FAVORITE Canvas courses.")
        end_favorite_index = self.print_list_with_index(canvas.get_current_user().get_favorite_courses())
        all_course_index = end_favorite_index + 1
        print(str(all_course_index) + ": " + "Show me ALL Canvas courses")
        return all_course_index

    def print_all_courses(self, canvas: Canvas) -> int:
        print("These are ALL of your Canvas courses")
        end_all_index = self.print_list_with_index(canvas.get_courses())
        return end_all_index

    def get_course(self, canvas: Canvas) -> Course:
        self.line_separator()
        ask_course = "Please enter the index number in front of the course in which you want to manage the grades: "
        all_course_index = self.print_favorite_courses(canvas)
        user_input_course = self.get_user_input_int(start_point=1, end_point=all_course_index, prompt=ask_course,
                                                    comma_allowed=False)
        if user_input_course == all_course_index:
            end_all_index = self.print_all_courses(canvas)
            user_input_course = self.get_user_input_int(start_point=1, end_point=end_all_index, prompt=ask_course,
                                                        comma_allowed=False)
        course_index = user_input_course - 1
        canvas_course = canvas.get_current_user().get_favorite_courses()[course_index]
        return canvas_course

    def get_assignment_groups(self, canvas_course: Course):
        self.line_separator()
        print("These are the available ASSIGNMENT GROUPS from " + canvas_course.name + ".")
        last_assignment_index = self.print_list_with_index(canvas_course.get_assignment_groups())
        ask_groups = "Please enter the index in front of the assignment GROUP(s) that you want to transfer grade from.\n" \
                     "If you want to select multiple groups, please separate them with commas: "
        user_input_groups = self.get_user_input_int(start_point=1, end_point=last_assignment_index, prompt=ask_groups,
                                                    comma_allowed=True)
        assignments = []
        for group in user_input_groups:
            group_id = canvas_course.get_assignment_groups().__getitem__(group - 1).id
            self.get_each_assignments(group_id, canvas_course, assignments)
        return assignments

    def get_each_assignments(self, group_id: int, canvas_course: Course, assignments: List[Assignment]):
        self.line_separator()
        group_name = canvas_course.get_assignment_group(group_id).name
        print("These are the available assignment(s) in the " + group_name + " you just chose.")
        last_assignment_index = self.print_list_with_index(canvas_course.get_assignments_for_group(group_id))
        ask_assignments = "Please enter the index number in front of the assignment(s) which you want to transfer \n" \
                          "grades from. If multiple, separate them with commas: "
        assignment_list = self.get_user_input_int(start_point=1, end_point=last_assignment_index,
                                                  prompt=ask_assignments,
                                                  comma_allowed=True)
        for index in assignment_list:
            assignments.append(canvas_course.get_assignments_for_group(group_id)[index - 1])
        return

    def show_head(self, csv_path: str) -> int:
        self.line_separator()
        print("Below are the first 6 lines in " + csv_path + ": ")
        with open(csv_path) as csv_file:
            reader1, reader2 = itertools.tee(csv.reader(csv_file))
            n_col = len(next(reader1))
            del reader1
            for i, row in enumerate(reader2):
                print(row)
                if i >= 5:
                    break
        return n_col

    @staticmethod
    def is_only_one_element_repeated(a_list: list, element_repeated: int) -> bool:
        counter = dict(Counter(a_list))
        for element, num_occurrence in counter.items():
            if num_occurrence != 1:
                if element != element_repeated:
                    return False
        return True

    def list_header_options(self, assignments: List[Assignment]) -> int:
        self.line_separator()
        print("Use the numbers in front of key words below to identify what's in the header, separated by comma(s):")
        print("NOTE: 0 (None) means to ignore this column because it is NOT important to this grade transfer. You can\n"
              "ONLY repeat 0; other numbers can be used AT MOST once.")
        print("0 None \n"
              "1 first_name\n"
              "2 last_name\n"
              "3 full_name\n"
              "4 sid\n"
              "5 email")
        assignment_index = 5
        for assignment in assignments:
            assignment_index += 1
            print(str(assignment_index) + " " + assignment.name)
        return assignment_index

    def tell_me_about_header(self, csv_ncol: int, csv_path: str, assignments: List[Assignment]):
        self.line_separator()
        last_available_index = self.list_header_options(assignments)
        ask_header = "Please categorize the columns: "
        user_input = self.get_user_input_int(start_point=0, end_point=last_available_index, prompt=ask_header,
                                             comma_allowed=True)
        while True:
            if len(user_input) != csv_ncol:
                print("Please enter EXACTLY " + str(csv_ncol) + " numbers. One for each column in " + csv_path
                      + ": ")
            elif not UserInterface.is_only_one_element_repeated(a_list=user_input, element_repeated=0):
                print("Only 0 (None) is allowed to repeat. Please enter again.")
            else:
                csv_header = self.decode_input_header(user_input, assignments)
                return csv_header

    @staticmethod
    def decode_input_header(input_header: List[int], assignments: List[Assignment]):
        csv_header = []
        for i in input_header:
            if i == 0:
                csv_header.append(None)
            elif i == 1:
                csv_header.append("first_name")
            elif i == 2:
                csv_header.append("last_name")
            elif i == 3:
                csv_header.append("full_name")
            elif i == 4:
                csv_header.append("sid")
            elif i == 5:
                csv_header.append("email")
            elif i > 5:
                csv_header.append(assignments[i - 6])
        return csv_header

    def print_prompt_for_names(self, name_type: str, csv_path: str):
        self.line_separator()
        print("ATTENTION: We suspect students below from " + csv_path + " match with the these from Canvas \n"
                                                                        "because they share the SAME UNIQUE ",
              name_type, " name after eliminating those who match absolutely \n"
                         "(either by SID or EMAIL). Please help us verify one by one. If match, type \"yes\" or \"y\"; if not,\n"
                         " type \"no\" or \"n\"")
        return

    @staticmethod
    def translate_yes_no_to_TF(user_input: str, yes_list: List[str], no_list: List[str]):
        if user_input in yes_list:
            return True
        elif user_input in no_list:
            return False
        return

    @staticmethod
    def print_student_info(name: str, sid: str, email: str):
        print(f"Full name: {name}")
        print(f"SID: {sid}")
        print(f"Email: {email}")
        print("")
        return

    def verify_name_check(self, third_party_dic: dict, canvas_dict: dict, name_type: str, csv_path: str):
        self.print_prompt_for_names(name_type, csv_path)
        ask_verify_name = "Are they the same student? (yes/y or no/n): "
        for student in third_party_dic:
            UserInterface.sub_line_separator()
            print("From " + csv_path + ": ")
            UserInterface.print_student_info(name=third_party_dic[student]["full_name"],
                                             sid=third_party_dic[student]["sid"],
                                             email=third_party_dic[student]["email"])
            print("From Canvas: ")
            UserInterface.print_student_info(name=canvas_dict[student]["full_name"], sid=canvas_dict[student]["sid"],
                                             email=canvas_dict[student]["email"])
            user_verify = UserInterface.get_user_input_key_words(allowed_key_words=["yes", "y", "Y", "no", "n", "N"],
                                                                 prompt=ask_verify_name)
            third_party_dic[student]["manual_match"] = self.translate_yes_no_to_TF(user_input=user_verify,
                                                                                   yes_list=["yes", "y", "Y"],
                                                                                   no_list=["no", "n", "N"])
        return

    def pre_update_announcement(self):
        self.line_separator()
        print("Now upload the grades. Please be patient")
        return

    @staticmethod
    def one_update_finish(name: str):
        print("Finished updating " + name + ".")
        UserInterface.sub_line_separator()
        return

    def show_csv_leftover(self, student_dic: dict, csv_path: str):
        self.line_separator()
        print("These are the students in " + csv_path + " who didn't get their grades transferred this time.")
        print("")
        for student in student_dic:
            UserInterface.print_student_info(student, student_dic[student]["sid"], student_dic[student]["email"])
        return
