import canvasapi
import datetime
from typing import Optional
import random  # only here for generating rand sandbox SID
from collections import OrderedDict


class PartnerEvalQuiz:
    def __init__(
        self,
        course: canvasapi.course.Course,
        assignment_name: str,
        assignment_group_id: int = 0,
        unlock_date: Optional[datetime.datetime] = None,
        due_date: Optional[datetime.datetime] = None,
        lock_date: Optional[datetime.datetime] = None,
    ):
        self.course = course
        self.assignment_name = assignment_name
        self.assignment_group_id = (
            assignment_group_id
            if assignment_group_id
            else self.__find_partner_eval_ag_id(course)
        )
        self.unlock_date = unlock_date
        self.due_date = due_date
        self.lock_date = lock_date

    def __create_quiz_info(self) -> dict:
        description = """
                    <p>This survey is meant for you to evaluate yourself and your partner for the project you just submitted together.</p>
                    <p>There will be one evaluation for each group project. At the end of the quarter, all the results will be combined in order to determine a "Group work" score that will count as part of your class grade. This score is totally independent from the grade you will receive from your related project submission.</p>
                    """
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

    def __create_quiz_questions(self) -> list[dict]:
        quiz_questions = []
        quiz_questions.append(self.__create_integrity_question())
        quiz_questions.extend(self.__create_eval_questions("self"))
        quiz_questions.append(self.__create_identify_partner_question())
        quiz_questions.append(self.__create_solo_justify_question())
        quiz_questions.extend(self.__create_eval_questions("partner"))
        quiz_questions.extend(self.__create_quantitative_contribution_question())
        return quiz_questions

    def __create_integrity_question(self) -> dict:
        return {
            "question_name": "Integrity check",
            "question_text": "I commit to complete this survey as fairly and honestly as possible",
            "question_type": "multiple_choice_question",
            "answers": [{"answer_text": "Yes", "answer_weight": 100}],
            "points_possible": 1,
        }

    def __create_eval_questions(self, subject: str) -> list[dict]:
        eval_questions = []
        eval_questions.append(self.__create_eval_questions_header(subject))
        eval_questions.append(self.__create_organization_question(subject))
        eval_questions.append(self.__create_communication_question(subject))
        eval_questions.append(self.__create_teamwork_question(subject))
        eval_questions.append(self.__create_attitude_question(subject))
        eval_questions.append(self.__create_ideas_question(subject))
        eval_questions.append(self.__create_code_questions(subject))
        eval_questions.append(self.__create_comments_questions(subject))

        for eval_question in eval_questions[1:-1]:
            eval_question["question_type"] = "multiple_choice_question"
            eval_question["answers"] = dict(
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
            eval_question["points_possible"] = 1

        return eval_questions

    def __create_eval_questions_header(self, subject: str) -> dict:
        if subject == "self":
            question_text = """<h3>Self evaluation</h3><p>First, let's start by evaluating yourself. Take the time to read all the questions, and their descriptions, and answer honestly.</p> """
        else:
            question_text = """<h3>Partner evaluation</h3><p>Now, let's evaluate your partner. Again, take the time to read all the questions, and their descriptions, and answer honestly.</p>"""
        return {
            "question_name": f"{subject} evaluation",
            "question_text": question_text,
            "question_type": "text_only_question",
        }

    def __create_organization_question(self, subject: str) -> dict:
        placeholder_1 = "You" if subject == "self" else "Your partner"
        placeholder_2 = "you" if subject == "self" else "they"
        return {
            "question_name": f"{subject} organization",
            "question_text": f"<h3>Organization/planning</h3><p>{placeholder_1} had a role in the clerical organization of your group. For example {placeholder_2} helped define the terms of your collaboration: how/when/where you should meet, how you should work together, etc.</p>",
        }

    def __create_communication_question(self, subject: str) -> dict:
        placeholder_1 = "You" if subject == "self" else "Your partner"
        placeholder_2 = "you" if subject == "self" else "they"
        placeholder_3 = "your partner" if subject == "self" else "you"
        return {
            "question_name": f"{subject} communication",
            "question_text": f"<h3>Communication</h3><p>{placeholder_1} had a role in the communication of your group. For example, {placeholder_2} helped maintain a constant communication with {placeholder_3} throughout the project.</p>",
        }

    def __create_teamwork_question(self, subject: str) -> dict:
        placeholder_1 = "You" if subject == "self" else "Your partner"
        placeholder_2 = (
            "the ideas of your partner" if subject == "self" else "your ideas"
        )
        placeholder_3 = "you" if subject == "self" else "they"
        placeholder_4 = "your" if subject == "self" else "their"
        return {
            "question_name": f"{subject} teamwork",
            "question_text": f"<h3>Teamwork/cooperation</h3><p>{placeholder_1} were willing to listen and respect {placeholder_2}, and discuss the work distribution. For example, {placeholder_3} would not try to always impose {placeholder_4} way of doing things.</p>",
        }

    def __create_attitude_question(self, subject: str) -> dict:
        placeholder_1 = "You" if subject == "self" else "Your partner"
        placeholder_2 = "you" if subject == "self" else "them"
        return {
            "question_name": f"{subject} attitude",
            "question_text": f"<h3>Attitude</h3><p>{placeholder_1} showed positive and enthusiast attitude, and it was pleasant to work with {placeholder_2}.</p>",
        }

    def __create_ideas_question(self, subject: str) -> dict:
        placeholder_1 = "You" if subject == "self" else "Your partner"
        return {
            "question_name": f"{subject} ideas",
            "question_text": f"<h3>Contribution of ideas</h3><p>{placeholder_1} contributed ideas to the project in terms of how to tackle the assignment, structure the code, build certain algorithms, etc.</p>",
        }

    def __create_code_questions(self, subject: str) -> dict:
        placeholder_1 = "You" if subject == "self" else "Your partner"
        return {
            "question_name": f"{subject} code",
            "question_text": f"<h3>Contribution of code</h3><p>{placeholder_1} participated in the programming aspect of the project.</p>",
        }

    def __create_comments_questions(self, subject: str) -> dict:
        placeholder_1 = "your" if subject == "self" else "your partner's"
        return {
            "question_name": f"{subject} comments",
            "question_text": f"<h3>Additional comments</h3><p>Please leave any additional comments about {placeholder_1} participation here. This is optional.</p>",
            "question_type": "essay_question",
            "points_possible": 0,
        }

    def __create_identify_partner_question(self) -> dict:
        # FIXME: messy and hacky way to handle dupes
        raw_students = {}
        raw_students = OrderedDict()
        dup_list = set()
        for raw_student in course.get_users(
            sort="username", enrollment_type=["student"]
        ):
            if (
                raw_student.sis_user_id is None
            ):  # FIXME: delete for real class; not all sandbox student have SID
                raw_student.sis_user_id = random.randint(0, 100)

            if raw_student.sortable_name in dup_list:
                SID = str(raw_student.sis_user_id)
                raw_students[
                    raw_student.sortable_name + " (XXXXX" + SID[-4:] + ")"
                ] = raw_student.sis_user_id
            elif raw_student.sortable_name in raw_students.keys():
                dup_list.add(raw_student.sortable_name)

                orignal_SID = str(raw_students[raw_student.sortable_name])
                raw_students[
                    raw_student.sortable_name + " (XXXXX" + orignal_SID[-4:] + ")"
                ] = orignal_SID
                raw_students.pop(raw_student.sortable_name)

                dup_SID = str(raw_student.sis_user_id)
                raw_students[
                    raw_student.sortable_name + " (XXXXX" + dup_SID[-4:] + ")"
                ] = raw_student.sis_user_id
            else:
                raw_students[raw_student.sortable_name] = raw_student.sis_user_id

        students = raw_students.keys()
        answers = [{"answer_text": student, "answer_weight": 1} for student in students]
        answers.append(
            {"answer_text": "I did not submit with a partner.", "answer_weight": 1}
        )
        return {
            "question_name": "identify partner",
            "question_text": "<h3>Identify partner</h3><p>Who is your partner?</p>",
            "question_type": "multiple_choice_question",
            "answers": dict(enumerate(answers)),
            "points_possible": 1,
        }

    def __create_solo_justify_question(self) -> dict:
        return {
            "question_name": "Solo Submission Justification",
            "question_text": "<h3>Solo Submission Justification</h3><p>If you did not submit with a partner, please explain why. If you spoke with me already about your reason, please put that here and whether or not I approved your reason.</p>",
            "question_type": "essay_question",
            "points_possible": 1,
        }

    def __create_quantitative_contribution_question(self) -> list[dict]:
        choices = [
            "0% vs 100% ==> Your partner did (almost) everything while you didn't do (almost) anything",
            "25% vs 75% ==> Your partner contributed substantially more than you",
            "50% / 50% ==> You and your partner contributed (almost) equally",
            "75% vs 25% ==> You contributed substantially more than your partner",
            "100% vs 0% ==> You did (almost) everything while your partner didn't do (almost) anything",
        ]
        questions = []
        questions.append(
            {
                "question_name": "Quantitative contribution",
                "question_text": "<h3>Quantitative contribution</h3><p>Express your and your partner's respective contributions to the project in a quantitative way.</p>",
                "question_type": "text_only_question",
            }
        )
        questions.append(
            {
                "question_name": "Project contribution",
                "question_text": "<h3>Project contribution</h3><p>How would you quantify your and your partner's respective contribution to the project?</p>",
                "question_type": "multiple_choice_question",
                "answers": dict(
                    enumerate(
                        [
                            {"answer_text": choice, "answer_weight": 1}
                            for choice in choices
                        ]
                    )
                ),
                "points_possible": 1,
            }
        )
        return questions

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

    assignment_name = "testing partner eval prog(1)"

    quiz = PartnerEvalQuiz(course, assignment_name)
    quiz.upload_to_canvas()
