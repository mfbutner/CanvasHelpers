"""Script to validate a single Self and Peer Evaluation quiz on Canvas

Contains a SelfAndPeerEvaluationQuizValidator class that handles the quiz
validation. A quiz will be validated by 
    (1) generating a quiz report JSON file that lists all student scores, 
    (2) logging solo submissions and their justificaitons to a .txt file
    (3*) Assigning students a "Did you submit correctly assignment"
    (4*) Giving students with problematic quizzes a few extra days to resubmit
    * will only be executed on user choice
Requires an external JSON file of quiz questions to actually get question information.
Requires directory to store quiz report in 
Requires directory to store solo submission report in

Typical Usage example:

    python3 quiz_validator.py @validator_args.txt --questions_file_path ./questions.json
"""
import argparse
import canvasapi
from collections import defaultdict
import datetime
import json
import os
from typing import Union
from utils import find_ag, make_student_id_map

JsonValue = Union[str, int, float, bool, list["JsonValue"], "JsonDict"]
JsonDict = dict[str, JsonValue]


class SelfAndPeerEvaluationQuizValidator:
    """Class that stores the evaluation quiz validator logic

    You can validate a quiz by calling validate_quiz(create_validation_assignment, validation_assignment_name)
    A quiz will be validated by
        (1) generating a quiz report JSON file that lists all student scores,
        (2) logging solo submissions and their justificaitons to a .txt file
        (3*) Assigning students a "Did you submit correctly assignment"
        (4*) Giving students with problematic quizzes a few extra days to resubmit
    * will only be executed on user choice

    Typical Usage example:
        validator = SelfAndPeerEvaluationQuizValidator(
            course,
            json_questions,
            assignment_group_name,
            quiz_report_path,
            solo_sub_path,
        )
        validator.validate_quiz(
            create_validation_assignment, validation_assignment_name
        )
    """

    def __init__(
        self,
        course: canvasapi.course.Course,
        json_questions: JsonDict,
        assignment_group_name: str,
        quiz_report_path: str,
        solo_sub_path: str,
    ):
        self.course = course
        self.json_questions = [
            question
            for question in json_questions["questions"]
            if question["question_type"]
            != "text_only_question"  # text_only_question's aren't stored in canvas question statistics
        ]
        self.assignment_group = find_ag(course, assignment_group_name)
        self.quiz_report_path = quiz_report_path
        self.solo_sub_path = solo_sub_path
        self.assignment = self.__get_assignment()
        self.quiz = self.course.get_quiz(self.assignment.quiz_id)
        self.canvas_questions = (
            list(self.quiz.get_statistics())[0]
        ).question_statistics
        self.quiz_grades = defaultdict(lambda: defaultdict(list))
        self.quiz_errors = defaultdict(list)  # key: ID (int), value: list of error strs
        self.solo_submission_ids = list()  # list of IDs (int)
        self.student_id_map = make_student_id_map(self.course)

    def validate_quiz(
        self,
        create_validation_assignment: bool,
        validation_assignment_name: str,
        extra_days: int,
    ) -> None:
        """
        validates a evaluation quiz by
            1. parsing through all the questions and storing results into JSON file
            2. logging solo submissions into a .txt file
            3*. assigning students a "did you submit correctly" assignment
            4*. giving students with problematic quizzes a few extra days to resubmit
        * only exectued if user wants to
        If a validation assignment is created, students will be assigned a "did you submit it correctly" assignment for the quiz you asked to validate. Correct submissions will be given a 1/1 (100%). Incorrect submissions will be given a 0/1 (0%) and comments indicating which questions students need to go back and answer.
        :modifies: self.quiz_grades to store quiz results
                   self.solo_submissions to store solo submissions
        """
        print(f'Validating "{self.assignment.name}"...')
        self.__write_quiz_metadata()
        self.__parse_quiz_questions()
        with open(
            os.path.join(self.quiz_report_path, f"{self.assignment.name}.json"), "w"
        ) as outfile:
            json.dump(self.quiz_grades, outfile)
        print(f"Report saved to {self.quiz_report_path} as {self.assignment.name}.json")

        self.__log_solo_submissions()
        if create_validation_assignment:
            self.__create_validation_assignment(validation_assignment_name, extra_days)
        print(f"Finish validating {self.assignment.name}")

    def __create_validation_assignment(
        self, validation_assignment_name: str, extra_days: int
    ) -> None:
        """
        creates a "Did you submit correctly" assignment for all students
        and allows problematic students to resubmit the original quiz
        """
        name = (
            validation_assignment_name
            if validation_assignment_name is not None
            else self.assignment.name + " Validator"
        )
        print(f'Assigning students "{name}" assignment')
        now = datetime.datetime.now()
        validation_assignment = self.course.create_assignment(
            assignment={
                "name": name,
                "description": f"Whether you submitted {self.assignment.name} correctly. If you received a 0, please go back and resubmitt {self.assignment.name} with the commented corrections. This score is totally independent from the grade you will receive from your related project submission.",
                "assignment_group_id": self.assignment.assignment_group_id,
                "submission_types": ["none"],
                "points_possible": 1,
                "due_at": now,
                "lock_at": now,
                "unlock_at": now,
                "published": True,
                "omit_from_final_grade": True,
            }
        )
        grade_data = defaultdict(dict)
        for student_id in self.quiz_grades["info"]["submissions"]:
            if student_id in self.quiz_errors:
                grade_data[student_id]["posted_grade"] = 0
                grade_data[student_id]["text_comment"] = ",\n".join(
                    [str(error) for error in self.quiz_errors[student_id]]
                )
            else:
                grade_data[student_id]["posted_grade"] = 1
        validation_assignment.submissions_bulk_update(grade_data=grade_data)
        if self.quiz_errors:
            self.assignment.create_override(
                assignment_override={
                    "student_ids": list(self.quiz_errors.keys()),
                    "title": f"{self.assignment.name} make up",
                    "unlock_at": now,
                    "due_at": now + datetime.timedelta(days=extra_days),
                    "lock_at": now + datetime.timedelta(days=extra_days),
                }
            )

    def __log_solo_submissions(self) -> None:
        """
        log solo submssion id's and justifications to a .txt file
        """
        for index, json_question in enumerate(self.json_questions):
            if json_question["question_name"] == "Solo Submission Justification":
                question_id = self.canvas_questions[index]["id"]
                break
        justification_index = None

        outfile = open(
            os.path.join(
                self.solo_sub_path, f"{self.assignment.name}_solo_submissions.txt"
            ),
            "w",
        )
        outfile.writelines("id (name): justification\n")
        for user_id in self.solo_submission_ids:
            submission = self.assignment.get_submission(
                user_id, include="submission_history"
            )
            submission_data = submission.submission_history[0]["submission_data"]
            if justification_index is None:
                for index, _ in enumerate(submission_data):
                    if _["question_id"] == int(question_id):
                        justification_index = index
                        break

            justification = submission_data[justification_index]["text"]
            if justification == "":
                justification = "No justification provided."
            outfile.writelines(
                f'{user_id} ({self.quiz_grades[user_id]["name"]}): {justification}\n'
            )
        outfile.close()
        print(
            f"Solo submissions justifcations saved to {self.solo_sub_path} as {self.assignment.name}_solo_submissions.txt"
        )

    def __parse_quiz_questions(self) -> None:
        """
        parses through all quiz questions and stores results into self.quiz_grades
        :returns: None, instead self.quiz_grades, self.quiz_errors,
                  and self.solo_submission_ids are directly modified
        """
        self.__parse_qualitative_self_evals()
        self.partner_id_map = self.__make_partner_id_map()
        self.__parse_qualitative_partner_evals()
        self.__parse_contribution_evals()

    def __parse_contribution_evals(self) -> None:
        """
        parse the project contribution question and store results in self.quiz_grades[individual_student]["Project Contribution"]
        missing answers are stored into self.quiz_errors
        :returns: None, instead self.quiz_grades and self.quiz_errors are directly modified
        """
        contrib_mappings = {
            "No Answer": None,
            "0% vs 100% ==> Your partner did (almost) everything while you didn't do (almost) anything": 0,
            "25% vs 75% ==> Your partner contributed substantially more than you": 0.25,
            "50% vs 50% ==> You and your partner contributed (almost) equally": 0.5,
            "75% vs 25% ==> You contributed substantially more than your partner": 0.75,
            "100% vs 0% ==> You did (almost) everything while your partner didn't do (almost) anything": 1,
        }
        for index, json_question in enumerate(self.json_questions):
            if json_question["question_name"] == "Project Contribution":
                question_stats = self.canvas_questions[index]
                break
        subject = "Project Contribution"
        # initialize each student's Project Contribution to list of 2 elements
        for student_id in self.quiz_grades["info"]["submissions"]:
            self.quiz_grades[student_id][subject] = [None for _ in range(2)]

        for answer in question_stats["answers"]:
            try:
                for user_id in answer["user_ids"]:
                    partner_id = self.partner_id_map[user_id]
                    if partner_id == "Solo Submission":
                        continue  # we make sure solo submisisons get 100% contrib later
                    self.quiz_grades[user_id][subject][0] = contrib_mappings[
                        answer["text"]
                    ]
                    if partner_id == "Unknown":
                        continue
                    self.quiz_grades[partner_id][subject][1] = (
                        1 - contrib_mappings[answer["text"]]
                        if contrib_mappings[answer["text"]] is not None
                        else None
                    )
            except KeyError:  # skip answers that no students picked
                continue
        self.__sanitize_contribution_evals()

    def __sanitize_contribution_evals(self) -> None:
        """
        parse through each submission in self.quiz_grades and make sure it is correctly
        that is, every submission contains 2 contribution scores (1 if solo submission)
        if a student's partner did not evalute a student, give student their own score
        solo submisisons are given 1 (100%) contribution
        :returns: None, instead self.quiz_grades and self.quiz_errors are directly modified
        """
        subject = "Project Contribution"
        for student_id in self.quiz_grades["info"]["submissions"]:
            if self.partner_id_map[student_id] == "Solo Submission":
                self.quiz_grades[student_id][subject] = [1]
            else:
                if self.quiz_grades[student_id][subject][0] is None:
                    self.quiz_grades[student_id][subject][0] = 0
                    self.quiz_errors[student_id].append(f"Missing {subject} evaluation")
                # we don't need to error log partner not answering since
                # we're already logging when a student does not answer
                if self.quiz_grades[student_id][subject][1] is None:
                    self.quiz_grades[student_id][subject][1] = self.quiz_grades[
                        student_id
                    ][subject][0]

    def __parse_qualitative_partner_evals(self) -> None:
        """
        parses through the partner evaluation questions and stores results into
        self.quiz_grades[individaul_student][category]
        missing answers are stored into self.quiz_errors
        :returns: None, instead self.quiz_grades and self.quiz_errors are directly modified
        """
        qual_mappings = {
            "Strongly disagree": 1,
            "Disagree": 2,
            "Agree": 3,
            "Strongly agree": 4,
        }
        for index, json_question in enumerate(self.json_questions):
            if (
                json_question["grader_info"]["category"] != "qualitative_partner"
                or not json_question["grader_info"]["include_in_grade"]
            ):
                continue
            subject = json_question["question_name"]
            for answer in self.canvas_questions[index]["answers"]:
                try:
                    for user_id in answer["user_ids"]:
                        partner_id = self.partner_id_map[user_id]
                        if partner_id == "Unknown" or partner_id == "Solo Submission":
                            continue

                        if answer["text"] == "No Answer":
                            self.quiz_errors[user_id].append(
                                f"Missing partner {subject} evaluation"
                            )

                        self.quiz_grades[partner_id][subject].append(
                            qual_mappings[answer["text"]]
                        )
                except KeyError:  # skip answers that no students picked
                    continue

        self.__sanitize_qualitative_partner_evals()

    def __sanitize_qualitative_partner_evals(self) -> None:
        """
        parse through each submission in self.quiz_grades and make sure it is correctly
        that is, every submission contains a partner evaluation score for each subject
        if a student's partner did not evalute a student, give student their own score
        :returns: None, instead self.quiz_grades and self.quiz_errors are directly modified
        """
        for student_id in self.quiz_grades["info"]["submissions"]:
            for subject in self.quiz_grades["info"]["qualitative_subjects"]:
                if self.partner_id_map[student_id] == "Unknown":
                    self.quiz_grades[student_id][subject].append(1)
                else:
                    if (
                        len(self.quiz_grades[student_id][subject]) != 2
                        and self.partner_id_map[student_id] != "Solo Submission"
                    ):
                        self.quiz_grades[student_id][subject].append(
                            self.quiz_grades[student_id][subject][0]
                        )

    def __make_partner_id_map(self) -> dict[int, Union[int, str]]:
        """
        maps all submisison student_id's to their partner_id
        all pairings in this dict are valid. that is, each pairing claimed each other
        solo submissions have a partner called "Solo Submission" and the solo submitter
        id is logged to self.solo_submission_ids
        unknown partnerships have a partner called "Unknown"
        :returns: dict of id's to partner_id
        :modifies: self.quiz_grades to log whether a student is a valid solo submission
        """
        for index, json_question in enumerate(self.json_questions):
            if json_question["question_name"] == "Partner Identification":
                question_stats = self.canvas_questions[index]
        potential_pairings = {}
        for answer in question_stats["answers"]:
            try:
                if answer["text"] == "I did not submit with a partner.":
                    partner_id = "Solo Submission"
                else:
                    partner_id = self.student_id_map[answer["text"]]

                for user_id in answer["user_ids"]:
                    potential_pairings[user_id] = partner_id
                    if partner_id == "Solo Submission":
                        self.quiz_grades[user_id]["valid_solo_submission"] = True
                        self.solo_submission_ids.append(user_id)
                    else:
                        self.quiz_grades[user_id]["valid_solo_submission"] = False
            except KeyError:  # skip answers that no students picked
                continue
        return self.__finalize_partner_pairings(potential_pairings)

    def __finalize_partner_pairings(
        self, potential_pairings: dict[int, Union[int, str]]
    ) -> dict[int, Union[int, str]]:
        """
        verifies that each partnership is claimed by both partners
        otherwise, map both partners to "Unknown"
        :returns: dict of id's to partner_id
        :modifies: self.quiz_grades to log whether a studnet is a valid solo submission
        """
        final_pairings = {}
        for student_id in self.quiz_grades["info"]["submissions"]:
            if student_id not in potential_pairings:
                self.quiz_errors[student_id].append(f"Missing partner Identification")
                final_pairings[student_id] = "Unknown"
                self.quiz_grades[student_id]["valid_solo_submission"] = False
            else:
                partner_id = potential_pairings[student_id]
                if partner_id == "Solo Submission":
                    final_pairings[student_id] = "Solo Submission"
                elif potential_pairings[partner_id] != student_id:
                    self.quiz_errors[student_id].append(f"Cannot verify partnership")
                    final_pairings[student_id] = "Unknown"
                else:
                    final_pairings[student_id] = partner_id
        return final_pairings

    def __parse_qualitative_self_evals(self) -> None:
        """
        parses through the self evaluation questions and stores results into
        self.quiz_grades[individaul_student][category]
        missing answers are stores into self.quiz_errors
        Since self and partner evaluations should share the same subjects,
        we also store the subjects into self.quiz_grades["info"]["qualitative_subjects"]
        :returns: None, instead self.quiz_grades and self.quiz_errors are directly modified
        """
        qual_mappings = {
            "Strongly disagree": 1,
            "Disagree": 2,
            "Agree": 3,
            "Strongly agree": 4,
        }
        for index, json_question in enumerate(self.json_questions):
            if (
                json_question["grader_info"]["category"] != "qualitative_self"
                or not json_question["grader_info"]["include_in_grade"]
            ):
                continue
            subject = json_question["question_name"]
            self.quiz_grades["info"]["qualitative_subjects"].append(subject)
            for answer in self.canvas_questions[index]["answers"]:
                try:
                    for user_id in answer["user_ids"]:
                        self.quiz_grades[user_id][subject].append(
                            qual_mappings[answer["text"]]
                        )
                except KeyError:  # skip answers that no students picked
                    continue

        self.__sanitize_qualitative_self_evals()

    def __sanitize_qualitative_self_evals(self) -> None:
        """
        parse through each submission in self.quiz_grades and make sure it is correctly
        that is, every submission contains a self evaluation score for each subject
        if there is no score, log the error to quiz_errors and give 1 (default)
        :returns: None, instead self.quiz_grades and self.quiz_errors are directly modified
        """
        for student_id in self.quiz_grades["info"]["submissions"]:
            for subject in self.quiz_grades["info"]["qualitative_subjects"]:
                if (
                    subject not in self.quiz_grades[student_id]
                    or len(self.quiz_grades[student_id][subject]) != 1
                ):
                    self.quiz_errors[student_id].append(
                        f"Missing self {subject} evaluation"
                    )
                    self.quiz_grades[student_id][subject].append(1)  # default score

    def __write_quiz_metadata(self) -> None:
        """
        write info about an assignment's quiz_id, name, submissions, and submission names
        to self.quiz_grades
        :returns: None, instead self.quiz_grades is directly modified
        """
        self.quiz_grades["info"]["quiz_id"] = self.assignment.quiz_id
        self.quiz_grades["info"]["quiz_name"] = self.assignment.name
        self.quiz_grades["info"]["submissions"] = []
        self.quiz_grades["info"]["weighting"] = {
            "qualitative": 0.4,
            "project_contribution": 0.6,
        }
        for submission in self.assignment.get_submissions():
            if submission.workflow_state == "unsubmitted":
                continue
            user_id = submission.user_id
            if user_id not in self.student_id_map.values():
                continue  # student is no longer in course
            self.quiz_grades["info"]["submissions"].append(user_id)
            self.quiz_grades[user_id]["name"] = [
                name for name, uid in self.student_id_map.items() if uid == user_id
            ][0]

    def __get_assignment(self) -> canvasapi.assignment.Assignment:
        """
        gets the assignment in the assignment group to be validated
        :returns: assignment to be validated
        """
        possible_assignments = self.__list_assignments()
        assignment_num = None
        while True:
            assignment_num = input(
                f"Select which assignment to validate (0 - {len(possible_assignments) - 1}): ",
            )
            try:
                assignment_num = int(assignment_num)
                if 0 <= assignment_num < len(possible_assignments):
                    break
            except:
                continue
        assignment_id = possible_assignments[assignment_num][0]
        return self.course.get_assignment(assignment_id)

    def __list_assignments(self) -> list:
        """
        lists all evaluation assignments in a assignment group
        :returns: list of tuples with assignment_id, assignment_name
        """
        print(f'Here are the assignments in "{self.assignment_group.name}"')
        evaluation_assignments = []
        for assignment_info in self.assignment_group.assignments:
            if "quiz_id" not in assignment_info:
                continue
            evaluation_assignments.append(
                (assignment_info["id"], assignment_info["name"])
            )
            print(
                str(len(evaluation_assignments) - 1) + ".",
                evaluation_assignments[-1][1],
            )
        return evaluation_assignments


def create_arguement_parser() -> argparse.ArgumentParser:
    """
    Creates the quiz_validator arguement parser
    :returns: quiz_validator arguement parser
    """
    parser = argparse.ArgumentParser(
        prog="quiz_validator",
        description="Script to validate a single Self and Peer Evaluation quiz on Canvas\nRead args from file by prefixing file_name with '@' (e.g. python3 quiz_validator.py @my_args.txt)",
        fromfile_prefix_chars="@",
    )
    parser.add_argument(
        "--canvas_url",
        dest="canvas_url",
        required=True,
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
        help="The id of the course.\nThis ID is located at the end of /coures in the Canvas URL.",
    )
    parser.add_argument(
        "--assignment_group_name",
        dest="assignment_group_name",
        required=True,
        help="The name of the assignment group where the "
        "Self and Peer Evaluation quiz assignments are located."
        "If the assignment group is not found, you will be asked to select it from a list of assignment groups.",
    )
    parser.add_argument(
        "--create_validation_assignment",
        action="store_true",
        required=False,
        help="Whether or not to create the validation assignment.",
    )
    parser.add_argument(
        "--validation_assignment_name",
        dest="validation_assignment_name",
        type=str,
        required=False,
        help="The name of the validation assignment.\nIf no name is passed, but a validation assignment is created, the assignment will be named '{validated_assignment} Validator.",
    )
    parser.add_argument(
        "--extra_days",
        dest="extra_days",
        type=int,
        default=2,
        required=False,
        help="The number of extra days students will get to resubmit the quiz that had issues with. By default, it is 2 extra days.",
    )
    parser.add_argument(
        "--questions_path",
        dest="questions_path",
        type=str,
        required=True,
        help="The path to the JSON file of questions the quiz is off of.",
    )
    parser.add_argument(
        "--quiz_report_path",
        dest="quiz_report_path",
        type=str,
        required=True,
        help="The path to the directory where you want to store the quiz report.\nIt's ok if the directory path has a trailing `/`.\nNOTE: The report WILL override any exist report with the same name.",
    )
    parser.add_argument(
        "--solo_sub_path",
        dest="solo_sub_path",
        type=str,
        required=True,
        help="The path to the directory where you want to store the solo submissions log.\nIt's ok if the directory path has a trailing `/`.",
    )
    return parser


if __name__ == "__main__":
    parser = create_arguement_parser()
    args = parser.parse_args()

    canvas = canvasapi.Canvas(args.canvas_url, args.canvas_key)
    course = canvas.get_course(args.course_id)
    with open(args.questions_path) as f:
        json_questions = json.load(f)
    validator = SelfAndPeerEvaluationQuizValidator(
        course,
        json_questions,
        args.assignment_group_name,
        args.quiz_report_path,
        args.solo_sub_path,
    )
    validator.validate_quiz(
        args.create_validation_assignment,
        args.validation_assignment_name,
        args.extra_days,
    )
