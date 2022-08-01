import canvasapi
from collections import defaultdict
import datetime
import json
import os
from grader_utils import *


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

    def __get_assignment(self) -> canvasapi.assignment.Assignment:
        print(f'Here are the assignments in "{self.assignment_group.name}"')
        possible_assignments = []
        for index, assignment_info in enumerate(self.assignment_group.assignments):
            if "quiz_id" not in assignment_info:
                continue
            possible_assignments.append(
                (assignment_info["id"], assignment_info["name"])
            )
            print(str(index) + ".", possible_assignments[index][1])

        while True:
            print(
                f"Select which assignment to validate (0 - {len(possible_assignments) - 1})",
                end=": ",
            )
            assignment_num = input()
            try:
                assignment_num = int(assignment_num)
            except ValueError:
                continue
            if assignment_num < 0 or assignment_num >= len(possible_assignments):
                continue
            else:
                break

        assignment_id = possible_assignments[assignment_num][0]
        return self.course.get_assignment(assignment_id)

    def validate_quiz(self) -> None:
        assignment = self.__get_assignment()
        quiz_grade = defaultdict(lambda: defaultdict(list))
        quiz = self.course.get_quiz(assignment.quiz_id)

        quiz_grade["info"]["quiz_id"] = assignment.quiz_id
        quiz_grade["info"]["quiz_name"] = assignment.name
        quiz_grade["info"]["submissions"] = []
        for submission in quiz.get_submissions():
            user_id = submission.user_id
            quiz_grade["info"]["submissions"].append(user_id)
            quiz_grade[user_id]["name"].append(
                self.course.get_user(user_id).sortable_name
            )

        quiz_errors = defaultdict(list)
        quiz_errors["quiz_id"].append(assignment.quiz_id)

        solo_submissions = list()

        canvas_questions = (list(quiz.get_statistics())[0]).question_statistics
        parse_qualitative_self_evals(
            quiz_grade,
            canvas_questions,
            self.json_questions["questions"],
            quiz_errors,
        )
        partner_id_map = make_partner_id_map(
            quiz_grade,
            self.student_id_map,
            canvas_questions,
            self.json_questions["questions"],
            quiz_errors,
            solo_submissions,
        )
        parse_qualitative_partner_evals(
            quiz_grade,
            canvas_questions,
            self.json_questions["questions"],
            partner_id_map,
            quiz_errors,
        )
        parse_quantitative_overall_evals(
            quiz_grade,
            canvas_questions,
            self.json_questions["questions"],
            partner_id_map,
            quiz_errors,
        )
        # write out quiz results
        with open(
            f"./quiz_results/quiz_reports/{assignment.name}.json", "w"
        ) as outfile:
            json.dump(quiz_grade, outfile)

        # write out solo submissions
        outfile = open(
            f"./quiz_results/solo_submissions/{assignment.name}_solo_submissions.txt",
            "w",
        )
        outfile.writelines("id: user_name\n")
        for solo_submission in solo_submissions:
            outfile.writelines(solo_submission + "\n")
        outfile.close()

        # update quiz assignment grade and comment on student errors
        update_quiz_assignment_grade(self.course, assignment, quiz_grade, quiz_errors)

    def upload_final_grades_to_canvas(
        self, assignment_name="Overall Evaluation Grade"
    ) -> None:
        print("We'll be basing final grade off of these files:")
        for filename in os.listdir("./quiz_results/quiz_reports"):
            print("   ", filename)
        individual_students_stats = [
            PartnerEvalQuizIndividualStats(name, id)
            for name, id in self.student_id_map.items()
        ]
        final_grades = {}
        csv_files = {}
        for student in individual_students_stats:
            final_grades[int(student.id)] = student.final_score
            csv_files[int(student.id)] = student.csv_file_path
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
        for student in individual_students_stats:
            submission = assignment.get_submission(int(student.id))
            submission.edit(
                submission={
                    "posted_grade": student.final_score,
                    "text_comment": "See attached file for final grade calculation.",
                }
            )
        print("done grades")
        for student in individual_students_stats:
            submission = assignment.get_submission(int(student.id))
            """
            submission.upload_comment(
                "./quiz_results/individual_student_reports/test.csv"
            )
            """
            submission.upload_comment(
                f"./quiz_results/individual_student_reports/{student.name}.csv"
            )
            # submission.upload_comment(student.csv_file_path)

        # debugging purposes
        for k, v in final_grades.items():
            print(f"ID {k} will receive {round(v,2 )} as their final score")

        print("Finished upload!")


if __name__ == "__main__":
    url = "https://canvas.ucdavis.edu"
    key = str(input("Enter API key:"))

    canvas = canvasapi.Canvas(url, key)
    course = canvas.get_course(1599)  # sandbox course ID
    with open("./self_and_partner_evaluation_questions.json") as f:
        json_questions = json.load(f)
    grader = PartnerEvalQuizGrader(course, json_questions)
    # grader.validate_quiz()
    grader.upload_final_grades_to_canvas("test grading files")
