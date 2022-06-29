import canvasapi
import datetime
from typing import List, Optional


class PartnerEvalQuiz:
    def __init__(
        self,
        course: canvasapi.course.Course,
        assignment_name: str,
        assignment_group_id: int,
        unlock_date: Optional[datetime.datetime] = None,
        due_date: Optional[datetime.datetime] = None,
        lock_date: Optional[datetime.datetime] = None,
    ):
        self.course = course
        self.assignment_name = assignment_name
        self.assignment_group_id = assignment_group_id
        self.unlock_date = unlock_date
        self.due_date = due_date
        self.lock_date = lock_date

        self.students = []
        for student in course.get_users(sort="username", enrollment_type=["student"]):
            self.students.append(student.sortable_name)

        self.quiz_info = self._create_quiz_info()
        self.assignment_info = self._create_assignment_info()
        self.quiz_questions = self._create_quiz_questions()

    def _create_quiz_info(self) -> dict:
        description = "This is the quiz description"
        return {
            "title": self.assignment_name,
            "description": description,
            "quiz_type": "assignment",
            "assignment_group_id": self.assignment_group_id,
            "scoring_policy": "keep_latest",
            "published": False,
            "show_correct_answers": False,
            "unlock_at": self.unlock_date,
            "due_at": self.due_date,
            "lock_at": self.lock_date,
        }

    def _create_assignment_info(self) -> dict:
        return {"omit_fromt_final_grade": True, "published": True}

    def _create_quiz_questions(self) -> List[dict]:
        # FIXME: why is answers a local var but not questions???
        quiz_questions = []

        # integreity question
        quiz_questions.append(self._create_integrity_question())

        # self-eval questions
        for question in self._create_eval_questions("self"):
            quiz_questions.append(question)

        # partner check question
        # quiz_questions.append(self._create_partner_check_question())

        # peer eval questions
        for question in self._create_eval_questions("peer"):
            quiz_questions.append(question)

        # solo sub justification
        quiz_questions.append(self._create_solo_sub_justify_question())

        return quiz_questions

    def _create_solo_sub_justify_question(self) -> dict:
        return {
            "question_name": "Solo Submission Justification",
            "question_text": "Please explain why you didn't submit with a partner. If you spoke with me already about your reason, please put that here and whether or not I approved your reason.",
            "question_type": "essay_question",
            "points_possible": 1,
        }

    def _create_integrity_question(self) -> dict:
        return {
            "question_name": "Integrity check",
            "question_text": "I commit to complete this survey as fairly and honestly as possible",
            "question_type": "multiple_choice_question",
            "answers": [{"answer_text": "Yes", "answer_weight": 100}],
            "points_possible": 1,
        }

    def _create_eval_questions(self, subject: str) -> List[dict]:
        eval_questions = []
        if subject == "peer":
            eval_questions.append(
                {
                    "question_name": "Peer evaluation",
                    "question_text": "Now, let's evaluate your partner. Again, take the time to read all the questions, and their descriptions, and answer honestly.",
                    "question_type": "text_only_question",
                }
            )
            eval_questions.append(self._create_identify_partner_question())
            # FIXME: is this really the pythonic way to do it
            placeholder_1 = "Your partner"
            placeholder_2 = "they"
            placeholder_3 = "you"
        elif subject == "self":
            # FIXME: is this really the pythonic way to do it
            eval_questions.append(
                {
                    "question_name": "Self-evaluation",
                    "question_text": "First, let's start by evaluating yourself. Take the time to read all the questions, and their descriptions, and answer honestly.",
                    "question_type": "text_only_question",
                }
            )
            placeholder_1 = "You"
            placeholder_2 = "you"
            placeholder_3 = "your partner"
        else:
            raise Exception(
                "Trying to create an eval question for neither your partner nor yourself"
            )

        # TODO: make these into functions?
        scale_answers = [
            {"answer_text": val, "answer_weight": 1} for val in range(1, 5)
        ]

        # organiztion
        eval_questions.append(
            {
                "question_name": "Orgnization/planning",
                "question_text": f"{placeholder_1} had a role in the clerical organization of your group. For example {placeholder_2} helped define the terms of your collaboration: how/when/where you should meet, how you should work together, etc.",
                "question_type": "multiple_choice_question",
                "answers": dict(enumerate(scale_answers)),
                "points_possible": 1,
            }
        )

        # communication
        eval_questions.append(
            {
                "question_name": "Communication",
                "question_text": f"{placeholder_1} had a role in the communication of your group. For example, {placeholder_2} helped maintain a constant communication with {placeholder_3} throughout the project.",
                "question_type": "multiple_choice_question",
                "answers": dict(enumerate(scale_answers)),
                "points_possible": 1,
            }
        )

        # teamwork / cooperation
        eval_questions.append(
            {
                "question_name": "Teamwork/cooperation",
                "question_text": f"{placeholder_1} were willing to listen and respect the ideas of {placeholder_2}, and discuss the work distribution. For example, {placeholder_2} would not try to always impose your way of doing things.",
                "question_type": "multiple_choice_question",
                "answers": dict(enumerate(scale_answers)),
                "points_possible": 1,
            }
        )

        # attitude
        eval_questions.append(
            {
                "question_name": "Attitude",
                "question_text": f"{placeholder_1} showed positive and enthusiast attidue, and it was pleasant to work with {placeholder_2}.",
                "question_type": "multiple_choice_question",
                "answers": dict(enumerate(scale_answers)),
                "points_possible": 1,
            }
        )

        # contriution of ideas
        eval_questions.append(
            {
                "question_name": "Contribution of ideas",
                "question_text": f"{placeholder_1} contributed ideas to the project in terms of how to tackle the assignment, structure the code, build certain algorithms, etc.",
                "question_type": "multiple_choice_question",
                "answers": dict(enumerate(scale_answers)),
                "points_possible": 1,
            }
        )

        # contribution of code
        eval_questions.append(
            {
                "question_name": "Contribution of code",
                "question_text": f"{placeholder_1} participated in the programming aspect of the project.",
                "question_type": "multiple_choice_question",
                "answers": dict(enumerate(scale_answers)),
                "points_possible": 1,
            }
        )

        eval_questions.append(
            {
                "question_name": "Additional comments",
                "question_text": f"Please leave any additional comments about {placeholder_1} here. This is optional.",
                "question_type": "essay_question",
                "points_possible": 1,
            }
        )

        return eval_questions

    def _create_identify_partner_question(self) -> dict:
        identify_partner_answers = self._create_identify_partner_answers()
        return {
            "question_name": "Identify partner",
            "question_text": "Who is your partner?",
            "question_type": "multiple_choice_question",
            "answers": dict(enumerate(identify_partner_answers)),
            "points_possible": 1,
        }

    def _create_identify_partner_answers(self) -> List[dict]:
        return [
            {"answer_text": student_name, "answer_weight": 1}
            for student_name in self.students
        ]

    def upload_to_canvas(self) -> None:
        print("uploading assignment to canvas")
        quiz = self.course.create_quiz(self.quiz_info)
        for question in self.quiz_questions:
            quiz.create_question(question=question)
        return


def find_partner_eval_ag_id(course: canvasapi.course.Course) -> int:
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
            name="Partner Evalulations", group_weight=0
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

    assignment_name = "testing partner eval prog"

    assignment_group_id = find_partner_eval_ag_id(course)

    quiz = PartnerEvalQuiz(course, assignment_name, assignment_group_id)
    quiz.upload_to_canvas()
