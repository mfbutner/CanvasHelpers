import canvasapi
from collections import defaultdict
import datetime
from grader_utils import *


class PartnerEvalQuizGrader:
    def __init__(
        self,
        course: canvasapi.course.Course,
        assignment_group: canvasapi.assignment.AssignmentGroup = None,
    ):
        self.course = course

        self.assignment_group = (
            assignment_group
            if assignment_group is not None
            else find_partner_eval_ag(course)
        )
        # make sure that assignment group has assignment attribute
        if not hasattr(self.assignment_group, "assignments"):
            self.assignment_group = course.get_assignment_group(
                self.assignment_group.id, include=["assignments"]
            )

        self.student_id_map = make_student_id_map(self.course)

    def __get_quiz_grades(self) -> list:
        quiz_grades = []
        for assignment_info in self.assignment_group.assignments:
            assignment = self.course.get_assignment(assignment_info["id"])
            if not hasattr(assignment, "quiz_id"):
                continue
            quiz_grades.append(self.__get_quiz_grade(assignment))
        return quiz_grades

    def __get_quiz_grade(self, assignment: canvasapi.assignment.Assignment) -> dict:
        quiz_grade = defaultdict(lambda: defaultdict(list))
        quiz = self.course.get_quiz(assignment.quiz_id)
        students_who_submitted = [
            submission.user_id for submission in quiz.get_submissions()
        ]
        quiz_grade["info"]["submissions"] = students_who_submitted

        stats = list(quiz.get_statistics())[0]
        # partner_id question is question 8
        partner_id_map = make_partner_id_map(
            self.student_id_map, stats.question_statistics[8]["answers"]
        )
        parse_self_evals(
            quiz_grade, stats.question_statistics[1:7], self.student_id_map
        )
        parse_partner_evals(
            quiz_grade, stats.question_statistics[10:16], partner_id_map
        )
        parse_contribution_evals(
            quiz_grade,
            stats.question_statistics[17],
            partner_id_map,
            self.student_id_map,
        )
        return quiz_grade

    def upload_grades_to_canvas(self, assignment_name="Group Work") -> None:
        quiz_grades = self.__get_quiz_grades()
        individual_students_stats = [
            PartnerEvalQuizIndividualStats(id, quiz_grades)
            for id in self.student_id_map.values()
        ]
        final_grades = {
            student.id: student.get_final_grade()
            for student in individual_students_stats
        }
        """
        assignment = self.course.create_assignment(
            assignment={
                "name": assignment_name,
                "description": "Your overall group work score based on the past Partner Evaluation assignments.",
                "assignment_group_id": self.assignment_group.id,
                "submission_types": ["none"],
                "points_possible": 100,
                "due_at": datetime.datetime.now().isoformat(),
                "lock_at": datetime.datetime.now().isoformat(),
                "unlock_at": datetime.datetime.now().isoformat(),
                "published": True,
            }
        )
        assignment.submissions_bulk_update(
            grade_data={
                id: {"posted_grade": grade} for id, grade in final_grades.items()
            }
        )
        """

        # debugging purposes
        for k, v in final_grades.items():
            print(f"ID {k} will receive {round(v,2 )} as their final score")


if __name__ == "__main__":
    url = "https://canvas.ucdavis.edu"
    key = str(input("Enter API key:"))

    canvas = canvasapi.Canvas(url, key)
    course = canvas.get_course(1599)  # sandbox course ID
    grader = PartnerEvalQuizGrader(course)
    grader.upload_grades_to_canvas("test grading")
