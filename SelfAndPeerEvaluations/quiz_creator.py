"""Script to create a single Self and Peer Evaluation quiz on Canvas

Contains a SelfAndPeerEvaluationQuizCreator class that handles the quiz
creation. Requires an external JSON file of quiz questions to actually
create the quiz questions.

Typical Usage example:

    python3 quiz_creator.py @creator_args.txt --questions_file_path ./questions.json
"""
import argparse
import canvasapi
import datetime
import json
from typing import Union
from utils import make_unique_student_id_map

JsonValue = Union[str, int, float, bool, list["JsonValue"], "JsonDict"]
JsonDict = dict[str, JsonValue]


class SelfAndPeerEvaluationQuizCreator:
    """Class that stores the evaluation quiz creation logic

    You can create an evaluation quiz by calling upload_to_canvas()

    Typical Usage example:
        quiz = SelfAndPeerEvaluationQuizCreator(
            course,
            json_questions,
            assignment_group_name,
            assignment_name,
            unlock_date,
            due_date,
            lock_date
        )
        quiz.upload_to_canvas()
    public functions
    ---
    upload_to_canvas(): uploads a evaluation quiz to canvas
    """

    def __init__(
        self,
        course: canvasapi.course.Course,
        json_questions: JsonDict,
        assignment_group_name: str,
        assignment_name: str,
        unlock_date: datetime.datetime,
        due_date: datetime.datetime,
        lock_date: datetime.datetime,
    ):
        self.course = course
        self.json_questions = json_questions
        self.assignment_name = assignment_name
        self.assignment_group_id = self.__find_assignment_group_id(
            assignment_group_name
        )
        self.unlock_date = unlock_date
        self.due_date = due_date
        self.lock_date = lock_date

    def upload_to_canvas(self) -> None:
        """
        uploads quiz assignemnt to Canvas
        :returns: None
        """
        print(f'Uploading "{self.assignment_name}" quiz assignment to Canvas')
        print("This might take a while")
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

    def __find_assignment_group_id(self, assignment_group_name: str) -> int:
        """
        looks for assignment group named assignment_group_name
        if no group is found, ask user if they want to create the group.
        if user doesn't want to create new group, program exits
        :returns: assignemnt group ID of specificed assignment group
        """
        # look for assignment group
        for ag in self.course.get_assignment_groups():
            if ag.name == assignment_group_name:
                return ag.id

        # assignment group was not found, so ask user if they want to make it
        choice = input(
            f"{assignment_group_name} was not found. Do you want to create it instead? (Y/N) "
        )
        if choice == "Y":
            ag = self.course.create_assignment_group(name=assignment_group_name)
            return ag.id
        else:
            print("Can't find assignment group or make it")
            print("Exiting creation script now.")
            exit(1)

    def __create_quiz_info(self) -> dict[str, Union[str, int, datetime.datetime]]:
        """
        Create the Canvas quiz's quiz_info
        :returns: dictonary of the Canvas quiz's quiz_info
        """
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

    def __create_quiz_questions(self) -> list[dict[str, Union[str, int]]]:
        """
        Iterates through all the questions in the JSON file's question list
        Most of the questions in the JSON file are properly formatted
        for canvasapi, but some have missing fields (answer section, pts possible)
        :return: list of questions ready to send to canvasapi's create_question()
        """
        quiz_questions = []
        multiple_choice_answers = self.json_questions["defaults"][
            "multiple_choice_answers"
        ]
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
                question["points_possible"] = self.json_questions["defaults"][
                    "points_possible"
                ]

            quiz_questions.append(question)
        return quiz_questions

    def __create_identify_partner_answers(self) -> list[dict[str, Union[str, int]]]:
        """
        Creates the multiple choice answers for "Who is your partner?" question
        If a student has the same sortable_name as another student, then we
        try to see if the student's name is unique with the last 4 digits of their SID appended (no SID -> XXXXXXXXX appended).
        If a student still isn't unique with their last 4 SID digits append, then we try their last 5 SID digits.
        It is extremely unlikely (at least 1 in 10^5 chance) that there exists students with
        the same sortable_name AND same last 5 digits.
        :return: list of answers properly formated for canvasapi
        """
        students = self.course.get_users(
            enrollment_type=["student"], enrollment_state=["active"]
        )
        students = make_unique_student_id_map(students).keys()
        answers = [{"answer_text": student, "answer_weight": 1} for student in students]
        answers.append(
            {"answer_text": "I did not submit with a partner.", "answer_weight": 1}
        )
        return answers


def create_arguement_parser() -> argparse.ArgumentParser:
    """
    Creates the quiz_creator arguement parser
    :returns: quiz_creator arguement parser
    """
    parser = argparse.ArgumentParser(
        prog="quiz_creator",
        description="Script to create a single Self and Peer Evaluations Quiz\nRead args from file by prefixing file_name with '@' (e.g. python3 quiz_creator.py @my_args.txt)",
        fromfile_prefix_chars="@",
    )
    parser.add_argument(
        "--canvas_url",
        dest="canvas_url",
        required=False,
        default="https://canvas.ucdavis.edu/",
        help="Your Canvas URL. By default, https://canvas.ucdavis.edu",
    )
    parser.add_argument(
        "--key", dest="canvas_key", required=True, help="Your Canvas API key."
    )
    parser.add_argument(
        "--course_id",
        dest="course_id",
        required=True,
        help="The id of the course.\nThis ID is located at the end of /courses in the Canvas URL.",
    )
    parser.add_argument(
        "--assignment_group_name",
        dest="assignment_group_name",
        required=True,
        help="The name of the assignment group for the "
        "Self and Peer Evaluation quiz assignment to be created under. "
        "If the assignment group is not found, you will be asked if you want to create it.",
    )
    parser.add_argument(
        "--assignment_name",
        dest="assignment_name",
        required=True,
        help="The name of the assignment you want to create.",
    )
    parser.add_argument(
        "--due_date",
        dest="due_date",
        required=True,
        type=datetime.datetime.fromisoformat,
        help="The date and time that the assignment is due in ISO Format: YYYY-MM-DDTHH:MM (e.g. 2022-03-03T23:59 -> March 3rd, 2022 at 11:59 PM)",
    )
    parser.add_argument(
        "--unlock_date",
        dest="unlock_date",
        type=datetime.datetime.fromisoformat,
        default=datetime.datetime.now(),
        help="The date the assignment should unlock. If not specified the assignment is made immediately available to students",
    )
    parser.add_argument(
        "--late_days",
        dest="late_days",
        type=int,
        default=0,
        help="The number of days an assignment can be turned in late. By default there are no late days.",
    )
    parser.add_argument(
        "--questions_path",
        dest="questions_path",
        type=str,
        required=True,
        help="The path to the JSON file of questions you want the quiz to be off of.",
    )
    return parser


if __name__ == "__main__":
    parser = create_arguement_parser()
    args = parser.parse_args()

    canvas = canvasapi.Canvas(args.canvas_url, args.canvas_key)
    course = canvas.get_course(args.course_id)
    with open(args.questions_path) as f:
        json_questions = json.load(f)

    quiz = SelfAndPeerEvaluationQuizCreator(
        course,
        json_questions,
        args.assignment_group_name,
        args.assignment_name,
        args.unlock_date,
        args.due_date,
        args.due_date + datetime.timedelta(days=args.late_days),
    )
    quiz.upload_to_canvas()
