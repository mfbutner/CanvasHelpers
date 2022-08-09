import canvasapi
from collections import defaultdict
import datetime
import json
import os
from utils import *


class PartnerEvalQuizGrader:
    def __init__(
        self,
        course: canvasapi.course.Course,
        json_questions: dict,
        assignment_group: canvasapi.assignment.AssignmentGroup = None,
    ):
        self.course = course
        self.json_questions = json_questions

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

    def upload_final_grades_to_canvas(
        self, assignment_name="Overall Evaluation Grade"
    ) -> None:
        files = []
        print("We'll be basing final grade off of these files:")
        print("These files will be processed in proper sorted order.")
        for filename in os.listdir("./quiz_results/quiz_reports"):
            print("   ", filename)
            files.append(os.path.join("./quiz_results/quiz_reports/", filename))

        individual_students_stats = []
        csv_files = {}
        for name, id in self.student_id_map.items():
            individual_students_stats.append(
                PartnerEvalQuizIndividualStats(name, id, sorted(files))
            )
            csv_files[id] = individual_students_stats[-1].csv_file_path

        print("ok i made the csvs")
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
        print("Uploading final grades and csv files to Canvas")
        print("This might take a while")
        assignment.submissions_bulk_update(
            grade_data={
                student.id: {"posted_grade": student.final_score}
                for student in individual_students_stats
            }
        )

        # wait for assignment to get submissions
        # if you don't wait, assignment.get_submissions() returns 0 submissions
        while not len(list(assignment.get_submissions())):
            continue

        for submission in assignment.get_submissions():
            if submission.user_id not in self.student_id_map.values():
                continue  # submisssion is a "ghost submission" (from Canvas's Test Student)
            submission.upload_comment(csv_files[submission.user_id])

        # debugging purposes
        for student in individual_students_stats:
            print(
                f"ID {student.id} will receive {student.final_score} as their final score"
            )

        print("Finished upload!")


if __name__ == "__main__":
    url = "https://canvas.ucdavis.edu"
    key = str(input("Enter API key:"))

    canvas = canvasapi.Canvas(url, key)
    course = canvas.get_course(1599)  # sandbox course ID
    with open("./self_and_partner_evaluation_questions.json") as f:
        json_questions = json.load(f)
    grader = PartnerEvalQuizGrader(course, json_questions)
    grader.upload_final_grades_to_canvas("overall grading test")
