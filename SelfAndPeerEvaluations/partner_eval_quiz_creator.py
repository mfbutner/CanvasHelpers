import argparse
import canvasapi
import datetime
import json
from typing import Optional, Union
from utils import make_student_id_map

JsonValue = Union[str, int, float, bool, list["JsonValue"], "JsonDict"]
JsonDict = dict[str, JsonValue]


class PartnerEvalQuizCreator:
    def __init__(
        self,
        course: canvasapi.course.Course,
        json_questions: JsonDict,
        assignment_name: str,
        unlock_date: Optional[datetime.datetime] = None,
        due_date: Optional[datetime.datetime] = None,
        lock_date: Optional[datetime.datetime] = None,
        assignment_group_id: int = 0,
    ):
        """
        public functions
        ---
        upload_to_canvas(): uploads a evaluation quiz to canvas
        """
        self.course = course
        self.json_questions = json_questions
        self.assignment_name = assignment_name
        self.assignment_group_id = (
            assignment_group_id
            if assignment_group_id
            else self.__find_partner_eval_ag_id(course)
        )
        self.unlock_date = unlock_date
        self.due_date = due_date
        self.lock_date = lock_date

    def upload_to_canvas(self) -> None:
        print("Uploading quiz assignment to canvas")
        quiz_info = self.__create_quiz_info()
        quiz_questions = self.__create_quiz_questions()

        quiz = self.course.create_quiz(quiz_info)
        for quiz_question in quiz_questions:
            quiz.create_question(question=quiz_question)

        canvas_assignment = course.get_assignment(quiz.assignment_id)
        canvas_assignment.edit(
            assignment={"omit_from_final_grade": True, "published": True}
        )

        print("Finished upload!")

    def __create_quiz_info(self) -> dict:
        return {
            "title": self.assignment_name,
            "description": self.json_questions["description"],
            "quiz_type": self.json_questions["quiz_type"],
            "assignment_group_id": self.assignment_group_id,
            "scoring_policy": self.json_questions["scoring_policy"],
            "published": self.json_questions["published"],
            "show_correct_answers": self.json_questions["show_correct_answers"],
            "unlock_at": self.unlock_date,
            "due_at": self.due_date,
            "lock_at": self.lock_date,
            "allowed_attempts": self.json_questions["allowed_attempts"],
        }

    def __create_quiz_questions(self) -> list[dict]:
        """
        Iterates through all the questions in the JSON file's question list
        Most of the questions in the JSON file are properly formated formated
        for canvasapi, but some have missing fields (answer section, pts possible)
        :return: list of questions ready to send to canvasapi's create_question()
        """
        quiz_questions = []
        multiple_choice_answers = dict(
            enumerate(
                {"answer_text": choice, "answer_weight": 1}
                for choice in [
                    "Strongly disagree",
                    "Disagree",
                    "Agree",
                    "Strongly agree",
                ]
            )
        )
        for question in self.json_questions["questions"]:
            if question["question_name"] == "Partner Identification":
                question["answers"] = self.__create_identify_partner_answers()
            elif (
                question["question_type"] == "multiple_choice_question"
                and "answers" not in question
            ):
                question["answers"] = multiple_choice_answers
            if "points_possible" not in question:
                # by default, we want questions to be 1 point
                question["points_possible"] = 1

            quiz_questions.append(question)
        return quiz_questions

    def __create_identify_partner_answers(self) -> dict:
        """
        Creates the multiple choice answers for "Who is your partner?" question
        If a student has the same sortable_name as another student, then we
        try to see if the student's name is unique with the last 4 digits of their SID appended (no SID -> XXXXXXXXX appended).
        If a student still isn't unique with their last 4 SID digits append, then we try their last 5 SID digits.
        It is extremely unlikely (at least 1 in 9^5 chance) that there exists students with
        the same sortable_name AND same last 5 digits.
        :return: dict of answers properly formated for canvasapi
        """
        students = make_student_id_map(self.course).keys()
        answers = [{"answer_text": student, "answer_weight": 1} for student in students]
        answers.append(
            {"answer_text": "I did not submit with a partner.", "answer_weight": 1}
        )
        return dict(enumerate(answers))

    def __find_partner_eval_ag_id(self, course: canvasapi.course.Course) -> int:
        partner_eval_ag = None

        for ag in course.get_assignment_groups():
            # FIXME: this is too strict
            #        we should be able to match similar assignment groups
            #        or, allow user to create their own ag
            if ag.name == "Partner Evalulations":
                partner_eval_ag = ag

        if partner_eval_ag is None:
            print('"Partner Evaluations" category does not exist!')
            print('Creating "Partner Evalutions" assignment group')
            partner_eval_ag = course.create_assignment_group(
                name="Partner Evalulations", group_weight=10
            )
        else:
            print("Not making a new assignment group since ")
            print('"Partner Evaluations" assignment group exists.')

        return partner_eval_ag.id


if __name__ == "__main__":
    url = "https://canvas.ucdavis.edu"
    key = str(input("Enter API key:"))

    canvas = canvasapi.Canvas(url, key)
    course = canvas.get_course(1599)  # sandbox course ID

    with open("./self_and_partner_evaluation_questions.json") as f:
        json_questions = json.load(f)

    # first_due = datetime.datetime(2022, 7, 20, 23, 59)
    # first_open = datetime.datetime(2022, 7, 20, 19, 00)
    assignment_names = ["json quiz x"]
    for _ in assignment_names:
        # due = first_due + datetime.timedelta(weeks_into_the_quarter * 7)
        # close = due + datetime.timedelta(days=1)
        # open_d = first_open + datetime.timedelta(weeks_into_the_quarter * 7)
        # quiz = PartnerEvalQuizCreator(course, _, open_d, due, close)
        quiz = PartnerEvalQuizCreator(course, json_questions, _)
        quiz.upload_to_canvas()
        # weeks_into_the_quarter += 1
