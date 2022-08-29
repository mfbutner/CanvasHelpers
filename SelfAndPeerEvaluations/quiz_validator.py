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
from utils import find_ag, make_unique_student_id_map

JsonValue = Union[str, int, float, bool, list["JsonValue"], "JsonDict"]
JsonDict = dict[str, JsonValue]


class SelfAndPeerEvaluationQuizValidator:
    """Class that stores the evaluation quiz validator logic

    You can validate a quiz by calling validate_quiz(reopen_assignment, extra_days)
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
            quiz_errors_path
        )
        validator.validate_quiz(
            reopen_assignment, extra_days
        )
    """

    def __init__(
        self,
        course: canvasapi.course.Course,
        json_questions: JsonDict,
        assignment_group_name: str,
        quiz_report_path: str,
        solo_sub_path: str,
        quiz_errors_path: str,
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
        self.quiz_errors_path = quiz_errors_path

        self.assignment = self.__get_assignment()
        self.quiz = self.course.get_quiz(self.assignment.quiz_id)
        self.canvas_questions = (
            list(self.quiz.get_statistics())[0]
        ).question_statistics
        self.quiz_grades = defaultdict(lambda: defaultdict(list))
        self.quiz_errors = defaultdict(list)  # key: ID (int), value: list of error strs
        self.quiz_potential_errors = defaultdict(
            list[str]
        )  # key: ID (int), value: id mismatch message
        self.solo_submission_ids = list()  # list of IDs (int)
        students = course.get_users(
            enrollment_type=["student"], enrollment_state=["active"]
        )
        self.student_id_map = make_unique_student_id_map(students)

    def validate_quiz(
        self,
        reopen_assignment: bool = False,
        extra_days: int = 2,
    ) -> None:
        """
        validates a evaluation quiz by
            1. parsing through all the questions and storing results into JSON file
            2. logging solo submissions into a .txt file
            3*. assigning students a "did you submit correctly" assignment
            4*. giving students with problematic quizzes a few extra days to resubmit
        * only exectued if user wants to
        :modifies: self.quiz_grades to store quiz results
                   self.solo_submissions to store solo submissions
        """
        print(f'Validating "{self.assignment.name}"...')
        self.__write_quiz_metadata()
        self.__parse_quiz_questions()

        self.__log_quiz_report()
        self.__log_quiz_errors()
        self.__log_solo_submissions()

        self.__create_or_update_validation_assignment()

        self.__reopen_assignment(reopen_assignment, extra_days)
        print(f"Finish validating {self.assignment.name}")

    def __log_quiz_report(self) -> None:
        """
        log the overall quiz report that details scores for every student
        :returns: None. Instead, a .json file is created for the quiz report
        """
        with open(
            os.path.join(self.quiz_report_path, f"{self.assignment.name}.json"), "w"
        ) as outfile:
            json.dump(self.quiz_grades, outfile)
        print(
            f'Report saved to {os.path.join(self.quiz_report_path, f"{self.assignment.name}.json")}'
        )

    def __log_quiz_errors(self) -> None:
        """
        logs students who had quiz errors to a .txt file
        :returns: None. Instead, a .txt file is created if there are any quiz errors
        """
        if not self.quiz_errors and not self.quiz_potential_errors:
            return
        with open(
            os.path.join(
                self.quiz_errors_path, f"{self.assignment.name}_quiz_errors.txt"
            ),
            "w",
        ) as outfile:
            if self.quiz_errors:
                outfile.write("id (name): errors\n")
                for user_id in self.quiz_errors:
                    outfile.write(
                        f'{user_id} ({self.quiz_grades[user_id]["name"]}): {self.quiz_errors[user_id]}\n'
                    )
            if self.quiz_potential_errors:
                outfile.write("\n")
                outfile.write("id (name): potential errors\n")
                for user_id in self.quiz_potential_errors:
                    outfile.write(
                        f"{user_id} ({self.quiz_grades[user_id]['name']}): {self.quiz_potential_errors[user_id]}\n"
                    )
        print(
            f'Students with quiz errors saved to {os.path.join(self.quiz_errors_path, f"{self.assignment.name}_quiz_errors.txt")}'
        )

    def __create_or_update_validation_assignment(self) -> None:
        """
        creates/updates a "Did you submit correctly" assignment for all students
        and allows problematic students to resubmit the original quiz if we're
        reopening the assignment
        :returns: None. Instead, a validation assignment is uploaded to Canvas
        """
        name = self.assignment.name + " Validator"
        validation_assignment = self.__validator_assignment_exists(name)
        if validation_assignment is None:
            print(f'Assigning students "{name}" assignment')
            now = datetime.datetime.now()
            validation_assignment = self.course.create_assignment(
                assignment={
                    "name": name,
                    "description": f"<p>The grade for this assignment is based off of whether you submitted {self.assignment.name} correctly. A 100% on this assignment means that there were no issues with your submission for {self.assignment.name} and you don't to do anything.</p><p>If you received anything besides a 100%, look at the comments on your submission for {self.assignment.name} for what the problems with your submission are. {self.assignment.name} has been reopened for you. Please check the assignment for your new due date. Please correct your errors and resubmit the assignment. After {self.assignment.name} closes again, it will be regraded and your score updated. This update to your scores is done manually, so it may take a day or two for your instructor to update your scores.</p><p>If there are still issues with your submission after the assignment closes for the second time, please contact your TAs and explain to them what went wrong and they will decide whether or not to update your grade based on that explanation.</p>",
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
        else:
            print(f'Updating students "{name}" assignment')
        grade_data = defaultdict(dict)
        for student in self.student_id_map.values():
            student_id = student.id
            if student_id in self.quiz_grades["info"]["submissions"]:
                if student_id in self.quiz_errors:
                    grade_data[student_id]["posted_grade"] = 0
                    grade_data[student_id]["text_comment"] = ",\n".join(
                        [str(error) for error in self.quiz_errors[student_id]]
                    )
                else:
                    grade_data[student_id]["posted_grade"] = 1
                if student_id in self.quiz_potential_errors:
                    if "text_comment" not in grade_data[student_id]:
                        grade_data[student_id]["text_comment"] = ""
                    else:
                        grade_data[student_id]["text_comment"] += ",\n"
                    grade_data[student_id]["text_comment"] += ",\n".join(
                        [str(error) for error in self.quiz_potential_errors[student_id]]
                    )
            else:
                grade_data[student_id]["posted_grade"] = 0
                grade_data[student_id][
                    "text_comment"
                ] = f"No submission for {self.assignment.name}"
        validation_assignment.submissions_bulk_update(grade_data=grade_data)

    def __reopen_assignment(
        self, reopen_assignment: bool = False, extra_days: int = 2
    ) -> None:
        """
        reopens the assignment for students with errors to resubmit if reopen_assignment is True
        :returns: None, instead reopens the assignment for students with errors
        """
        now = datetime.datetime.now()
        if reopen_assignment:
            print(f"Reopening {self.assignment.name}")
            if self.quiz_errors or self.quiz_potential_errors:
                self.assignment.create_override(
                    assignment_override={
                        "student_ids": list(
                            set(self.quiz_errors.keys())
                            | set(self.quiz_potential_errors.keys())
                        ),
                        "title": f"{self.assignment.name} make up",
                        "unlock_at": now,
                        "due_at": (now + datetime.timedelta(days=extra_days)).replace(
                            hour=23, minute=59
                        ),
                        "lock_at": (now + datetime.timedelta(days=extra_days)).replace(
                            hour=23, minute=59
                        ),
                    }
                )

    def __validator_assignment_exists(
        self, name: str
    ) -> canvasapi.assignment.Assignment:
        """
        check if validator assignment already exists
        :param name: the name of the validation assignment
        :returns: canvasapi.Assignment of the validator assignment if it exists
        """
        for assignment in self.course.get_assignments_for_group(self.assignment_group):
            if assignment.name == name:
                return assignment
        return None

    def __log_solo_submissions(self) -> None:
        """
        log solo submssion id's and justifications to a .txt file
        :returns: None. Instead, a .txt file is written to log solo submission justifcations if there are any solo submisions
        """
        for index, json_question in enumerate(self.json_questions):
            if json_question["question_name"] == "Solo Submission Justification":
                question_id = self.canvas_questions[index]["id"]
                break
        justification_index = None

        if not self.solo_submission_ids:
            return

        with open(
            os.path.join(
                self.solo_sub_path, f"{self.assignment.name}_solo_submissions.txt"
            ),
            "w",
        ) as outfile:
            outfile.write("id (name): justification\n")
            for user_id in self.solo_submission_ids:
                submission = self.assignment.get_submission(
                    user_id, include="submission_history"
                )
                submission_data = submission.submission_history[0]["submission_data"]
                if justification_index is None:
                    for index, question in enumerate(submission_data):
                        if question["question_id"] == int(question_id):
                            justification_index = index
                            break

                justification = submission_data[justification_index]["text"]
                if justification.strip() == "":
                    justification = "No justification provided."
                outfile.write(
                    f'{user_id} ({self.quiz_grades[user_id]["name"]}): {justification}\n'
                )
        print(
            f'Solo submissions justifcations saved to {os.path.join(self.solo_sub_path, f"{self.assignment.name}_solo_submissions.txt")}'
        )

    def __parse_quiz_questions(self) -> None:
        """
        parses through all quiz questions and stores results into self.quiz_grades
        :returns: None
        :modifies: self.quiz_grades to log quiz results,
                   self.quiz_errors to log students who have quiz errors and what they are,
                   self.partner_id_map to map students to their partners
                   self.solo_submission_ids to log which students were solo submissions
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
        :modifies: self.quiz_grades to log contribution results,
                   self.quiz_errors to log students who have quiz errors and what they are
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
        :returns: None
        :modifies: self.quiz_grades to log contribution results,
                   self.quiz_errors to log students who have quiz errors and what they are
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
        :returns: None
        :modifies: self.quiz_grades to log qualitative partner quiz results,
                   self.quiz_errors to log students who have quiz errors and what they are
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
                        if partner_id == "Solo Submission":
                            continue

                        if answer["text"] == "No Answer":
                            self.quiz_errors[user_id].append(
                                f"Missing partner {subject} evaluation"
                            )

                        if partner_id != "Unknown":
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
        :returns: None
        :modifies: self.quiz_grades to log qualitative partner quiz results,
                   self.quiz_errors to log students who have quiz errors and what they are
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
                break
        potential_pairings = {}
        for answer in question_stats["answers"]:
            try:
                if answer["text"] == "I did not submit with a partner.":
                    partner_id = "Solo Submission"
                else:
                    partner_id = self.student_id_map[answer["text"]].id

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
        :modifies: self.quiz_grades to log whether a student is a valid solo submission
                   self.quiz_errors to log incorrect identifications
                   self.quiz_potential_errors to log potential incorrect indentifications
        """
        final_pairings = self.__get_confirmed_pairings(potential_pairings)

        # validate the rest of the students who aren't in confirmed pairings
        for student_id in self.quiz_grades["info"]["submissions"]:
            if student_id in final_pairings:
                continue
            claimed_partner_id = potential_pairings[student_id]
            if (
                claimed_partner_id in final_pairings
                and final_pairings[claimed_partner_id] != "Unknown"
            ):
                self.__log_known_pairing_mismatch(
                    student_id, claimed_partner_id, final_pairings
                )
            else:  # partner's partner someone else (that didn't claim partner), or Unknown
                if claimed_partner_id in potential_pairings:
                    self.__log_potential_pairing_mismatch(
                        student_id, claimed_partner_id, potential_pairings
                    )
                else:
                    self.quiz_errors[student_id].append(
                        f"Looks like your partner did not identify their partner, so we cannot verify your partnership with them. Please double check your submission and make sure that there are no errors."
                    )

            final_pairings[student_id] = "Unknown"

        return final_pairings

    def __get_confirmed_pairings(
        self, potential_pairings: dict[int, Union[int, str]]
    ) -> dict[int, Union[int, str]]:
        """
        get confirmed pairs (both students claimed each other, or solo submission)
            and students who didn't answer the identification question
        :returns: dict of confirmed, finalized pairings
        :modifies: self.quiz_errors to log students who didn't answer or picked themselve
        """
        confirmed_pairings = {}
        for student_id in self.quiz_grades["info"]["submissions"]:
            try:
                if student_id not in potential_pairings:  # no answer
                    confirmed_pairings[student_id] = "Unknown"
                    self.quiz_errors[student_id].append(
                        f"Missing partner identification"
                    )
                    self.quiz_grades[student_id]["valid_solo_submission"] = False
                    continue
                partner_id = potential_pairings[student_id]
                if (
                    partner_id == student_id
                ):  # student picked themselves as their partner instead of picking "Solo Submiion"
                    confirmed_pairings[student_id] = "Solo Submission"
                    self.quiz_potential_errors[student_id].append(
                        f'Looks like you picked yourself as your partner instead of selecting "I did not submit with a partner." Please double check your submission and make sure that there are no errors. You won\'t lose any points.'
                    )
                    self.quiz_grades[student_id]["valid_solo_submission"] = True
                    self.solo_submission_ids.append(student_id)
                elif (
                    partner_id == "Solo Submission"
                    or potential_pairings[partner_id] == student_id
                ):
                    confirmed_pairings[student_id] = partner_id
            except KeyError:  # student and/or partner did not answer question
                continue
        return confirmed_pairings

    def __log_known_pairing_mismatch(
        self,
        student_id: int,
        claimed_partner_id: int,
        final_pairings: dict[int, Union[int, str]],
    ) -> None:
        """
        log error of student trying to claim partnership with a known pair. that is,
        the student is trying to say one member of a known pair is their partner when
        in reality, the known pair are partners and the student is in the wrong
        student will receive an "Unknown" partner while known pair is unaffected
        :returns: none
        :modifies: self.quiz_errors to log student error
                   self.quiz_potential_errors to inform known pair of the issue
        """
        student_id_name = self.quiz_grades[student_id]["name"]
        claimed_partner_name = self.quiz_grades[claimed_partner_id]["name"]
        if final_pairings[claimed_partner_id] == "Solo Submission":
            self.quiz_errors[student_id].append(
                f"Looks like you claimed {claimed_partner_name} as your partner, but {claimed_partner_name} said that they worked alone. Please double check your submission and make sure that there are no errors."
            )
            self.quiz_potential_errors[claimed_partner_id].append(
                f"Looks like you said you worked alone, but {student_id_name} claimed you as their partner. Please make double check your submission and make sure that there are no errors. You won't lose any points."
            )
        else:
            claimed_partner_partner_id = final_pairings[claimed_partner_id]
            claimed_partner_partner_name = self.quiz_grades[claimed_partner_partner_id][
                "name"
            ]
            self.quiz_errors[student_id].append(
                f"Looks like you claimed {claimed_partner_name} as your partner, but {claimed_partner_name} and {claimed_partner_partner_name} claimed each other as partners. Please double check your submission and make sure that there are no errors."
            )
            self.quiz_potential_errors[claimed_partner_id].append(
                f"Looks like you and {claimed_partner_partner_name} claimed each other as partners, but {student_id_name} claimed you as their partner. Please double check your submission and make sure that there are no errors. You won't lose any points."
            )
            self.quiz_potential_errors[claimed_partner_partner_id].append(
                f"Looks like you and {claimed_partner_name} claimed each other as partners, but {student_id_name} claimed {claimed_partner_name} as their partner. Please double check your submission and make sure that there are no errors. You won't lose any points."
            )

    def __log_potential_pairing_mismatch(
        self,
        student_id: int,
        claimed_partner_id: int,
        potential_pairings: dict[int, Union[int, str]],
    ) -> None:
        """
        log error of student trying to claim partnership with another student who
        claimed someone else (that we cannot confirm is actually that other student's
        partner)
        :returns: none
        :modifies: self.quiz_errors to log student error
        """
        claimed_partner_partner_id = potential_pairings[claimed_partner_id]
        claimed_partner_partner_name = "Unknown"
        if claimed_partner_partner_id in self.quiz_grades["info"]["submissions"]:
            # partner claimed a student who submitted the assignment, so we can
            # quickly look up that student's name
            claimed_partner_partner_name = self.quiz_grades[claimed_partner_partner_id][
                "name"
            ]
        elif claimed_partner_partner_id != "Unknown":
            # we'll have to look them up the hard way (via the known, student_id_map)
            # NOTE: If claimed_partner_partner is no longer in course, and self.student_id_map or the quiz wasn't updated to account for that,
            #       there could be some lookup error
            claimed_partner_partner_name = [
                student
                for student in self.student_id_map.values()
                if student.id == claimed_partner_partner_id
            ][0].sortable_name
        self.quiz_errors[student_id].append(
            f"Looks like your partner claimed {claimed_partner_partner_name} as their partner. Please double check your submission and make sure that there are no errors."
        )

    def __parse_qualitative_self_evals(self) -> None:
        """
        parses through the self evaluation questions and stores results into
        self.quiz_grades[individaul_student][category]
        missing answers are stores into self.quiz_errors
        Since self and partner evaluations should share the same subjects,
        we also store the subjects into self.quiz_grades["info"]["qualitative_subjects"]
        :returns: None
        :modifies: self.quiz_grades to log qualitative self quiz results,
                   self.quiz_errors to log students who have quiz errors and what they are
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
        :returns: None
        :modifies: self.quiz_grades to log qualitative self quiz results,
                   self.quiz_errors to log students who have quiz errors and what they are
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
        :modifies: self.quiz_grades to log quiz metdadata
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
            students = self.student_id_map.values()
            self.quiz_grades["info"]["submissions"].append(user_id)
            self.quiz_grades[user_id]["name"] = [
                name
                for name, student in self.student_id_map.items()
                if student.id == user_id
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
        type=str,
        default="https://canvas.ucdavis.edu/",
        help="Your Canvas URL. By default, https://canvas.ucdavis.edu",
    )
    parser.add_argument(
        "--key", dest="canvas_key", type=str, required=True, help="Your Canvas API key."
    )
    parser.add_argument(
        "--course_id",
        dest="course_id",
        type=int,
        required=True,
        help="The id of the course.\nThis ID is located at the end of /coures in the Canvas URL.",
    )
    parser.add_argument(
        "--assignment_group_name",
        dest="assignment_group_name",
        required=True,
        type=str,
        help="The name of the assignment group where the "
        "Self and Peer Evaluation quiz assignments are located."
        "If the assignment group is not found, you will be asked to select it from a list of assignment groups.",
    )
    parser.add_argument(
        "--reopen_assignment",
        dest="reopen_assignment",
        action="store_true",
        required=False,
        help="Whether or not to reopen the assignment for students to resubmit and ammend their issues. If this flag is passed, the assignment will be reopened for students to resubmit the assignment.",
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
        help="The path to the directory where you want to store the solo submissions log.\nIt's ok if the directory path has a trailing `/`.\nNOTE: The log WILL override any exist log with the same name.",
    )
    parser.add_argument(
        "--quiz_errors_path",
        dest="quiz_errors_path",
        type=str,
        required=True,
        help="The path to the directory where you want to store the quiz errors log.\nIt's ok if the directory path has a trailing `/`.\nNOTE: The log WILL override any exist log with the same name.",
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
        args.quiz_errors_path,
    )
    validator.validate_quiz(
        args.reopen_assignment,
        args.extra_days,
    )
