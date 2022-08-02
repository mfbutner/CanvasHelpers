import canvasapi
from collections import defaultdict
import csv
from collections import deque
import datetime
import json
import statistics
import random


class PartnerEvalQuizIndividualStats:
    def __init__(self, name: str, id: int, files: list):
        self.name = "".join(filter(str.isalnum, name))
        self.id = str(id)
        self.scores = defaultdict(list)

        self.detailed_scores = []
        detailed_scores_header = []
        self.qualitative_subjects = None
        self.quantitative_overall_subjects = None

        self.csv_file_path = (
            f"./quiz_results/individual_student_reports/{self.name}.csv"
        )
        f = open(self.csv_file_path, "w")
        self.writer = csv.writer(f)

        for file in files:
            with open(file, "r") as f:
                json_file = json.load(f)
                if len(detailed_scores_header) == 0:  # only make the header once
                    detailed_scores_header = self.__make_header(json_file)
                    self.detailed_scores.append(detailed_scores_header)
                if self.qualitative_subjects is None:  # only get once
                    self.qualitative_subjects = json_file["info"][
                        "qualitative_subjects"
                    ]
                if self.quantitative_overall_subjects is None:  # only get once
                    self.quantitative_overall_subjects = json_file["info"][
                        "quantitative_overall_subjects"
                    ]
                self.__parse_quiz_grade(json_file)

        self.__get_averages()
        # transpose detailed scores
        self.detailed_scores = [
            [row[i] for row in self.detailed_scores]
            for i in range(len(self.detailed_scores[0]))
        ]
        self.csv_file_info = deque(self.detailed_scores)
        self.csv_file_info.appendleft([""])  # empty row
        self.csv_file_info.appendleft(
            ["INDIVIDUAL ASSIGNMENT GRADES\nAND CALCULATIONS"]
        )
        self.csv_file_info.extendleft([""] for _ in range(4))  # empty rows
        self.csv_file_info.extendleft(self.__write_contribution_score())
        self.csv_file_info.extendleft(self.__write_qualitative_score())
        self.csv_file_info.appendleft([""])  # empty row
        self.csv_file_info.appendleft(self.__write_final_score())
        self.csv_file_info.appendleft([""])
        self.csv_file_info.appendleft(["FINAL SCORE CALCULATIONS"])
        self.writer.writerows(self.csv_file_info)
        f.close()

    def __write_final_score(self) -> list:
        self.final_score = 0.4 * self.qualitative_score + 0.6 * self.contribution_score
        return [
            "Final Score\n(40% Qualitative + 60% Project Contribution)",
            round(self.final_score, 2),
        ]

    def __write_qualitative_score(self) -> list:
        overall_qualitative_str = f"Overall Qualitative Averages\n{self.__stringify_subjects(self.qualitative_subjects)}"
        header = [
            "",
            "Score\n(if (diff > 0); then score=(avg - diff)/4*100;\nelse score=(avg - diff/2)/4*100)",
            f"Average of {overall_qualitative_str}",
            "Difference\n(Overall Average of\nAverage Qualitative Difference)",
        ]
        self.__calculate_qualitative_score()
        row = [
            "Qualitative",
            self.qualitative_score,
            self.average_qualitative,
            self.average_qualitative_difference,
        ]
        return [row, header]

    def __calculate_qualitative_score(self) -> None:
        if self.average_qualitative_difference > 0:
            self.qualitative_score = round(
                (
                    (self.average_qualitative - self.average_qualitative_difference)
                    / 4
                    * 100
                ),
                2,
            )
        else:
            self.qualitative_score = round(
                (
                    (
                        self.average_qualitative
                        - (self.average_qualitative_difference / 2)
                    )
                    / 4
                    * 100
                ),
                2,
            )

    def __write_contribution_score(self) -> list:
        header = [
            "",
            "Score\n(if (diff > 0); then score=(avg - diff)/50*100*100;\nelse score=(avg - diff/2)/50*100*100)",
            "Average Project Contribution",
            "Project Contribution Difference",
        ]
        self.__calculate_contribution_score()
        row = [
            "Project Contribution",
            self.contribution_score,
            self.average_project_contribution,
            self.average_project_contribution_difference,
        ]
        return [row, header]

    def __calculate_contribution_score(self) -> None:
        if self.average_project_contribution_difference > 0:
            self.contribution_score = round(
                (
                    (
                        self.average_project_contribution
                        - self.average_project_contribution_difference
                    )
                    / 50
                    * 100
                    * 100
                ),
                2,
            )
        else:
            self.contribution_score = round(
                (
                    (
                        self.average_project_contribution
                        - (self.average_project_contribution_difference / 2)
                    )
                    / 50
                    * 100
                    * 100
                ),
                2,
            )

    def __get_averages(self) -> None:
        averages_values = ["Overall Average"]
        qualitative_averages = []

        for qualitative_subject in self.qualitative_subjects:
            averages_values.append(
                f"Self: Not used in Final Grade Calculation\nPartner: Not used in Final Grade Calculation\nAverage: {round(statistics.fmean(self.scores[qualitative_subject]), 2)}\nDiff: Not used in Final Grade Calculation"
            )
            qualitative_averages.append(
                round(statistics.fmean(self.scores[qualitative_subject]), 2)
            )
        self.average_qualitative = round(statistics.fmean(qualitative_averages), 2)

        averages_values.append(
            round(statistics.fmean(self.scores["Qualitative Difference"]), 2)
        )
        self.average_qualitative_difference = round(float(averages_values[-1]), 2)

        # NOTE: there's only contribution for now
        for quantitative_overall_subject in self.quantitative_overall_subjects:
            averages_values.append(
                f"Self: Not used in Final Grade Calculation\nPartner: Not used in Final Grade Calculation\nAverage: {round(statistics.fmean(self.scores[quantitative_overall_subject]),2)}\nDiff: {round(statistics.fmean(self.scores['Project Contribution Difference']), 2)}"
            )
            self.average_project_contribution = round(
                statistics.fmean(self.scores[quantitative_overall_subject]), 2
            )
            self.average_project_contribution_difference = round(
                statistics.fmean(self.scores["Project Contribution Difference"]), 2
            )

        self.detailed_scores.append(averages_values)

    def __parse_quiz_grade(self, json_file: dict):
        row = []
        row.append(json_file["info"]["quiz_name"])
        if self.id not in json_file:
            for qualitative_subject in json_file["info"]["qualitative_subjects"]:
                row.append("Self: 1\nPartner: 1\nAverage: 1\nDiff (self - partner): 0")
                self.scores[qualitative_subject].append(1)
            row.append("0")  # average qualitative difference
            self.scores["Qualitative Difference"].append(0)
            for quantitative_overall_subject in json_file["info"][
                "quantitative_overall_subjects"
            ]:
                row.append("Self: 0\nPartner: 0\nAverage: 0\nDiff (self - partner): 0")
                self.scores[quantitative_overall_subject].append(0)
                self.scores["Project Contribution Difference"].append(
                    0
                )  # since contribution is the only one here
            self.detailed_scores.append(row)
            return
        if json_file[self.id]["valid_solo_submission"][0]:
            for qualitative_subject in json_file["info"]["qualitative_subjects"]:
                self_score = json_file[self.id][qualitative_subject][0]
                row.append(
                    f"Self: {self_score}\nPartner: N/A\nAverage: {self_score}\nDiff (self - partner): 0"
                )
                self.scores[qualitative_subject].append(self_score)
            row.append(0)  # average qualitative difference
            self.scores["Qualitative Difference"].append(0)
            for quantitative_overall_subject in json_file["info"][
                "quantitative_overall_subjects"
            ]:
                self_score = json_file[self.id][quantitative_overall_subject][0]
                row.append(
                    f"Self: {self_score}\nPartner: N/A\nAverage: {self_score}\nDiff (self - partner): 0"
                )
                self.scores[quantitative_overall_subject].append(self_score)
                self.scores["Project Contribution Difference"].append(
                    0
                )  # since contribution is the only one here
        else:
            qualitative_differences = []
            for qualitative_subject in json_file["info"]["qualitative_subjects"]:
                self_score = json_file[self.id][qualitative_subject][0]
                partner_score = json_file[self.id][qualitative_subject][1]
                average = round(
                    statistics.fmean(json_file[self.id][qualitative_subject]), 2
                )
                qualitative_difference = self_score - partner_score
                qualitative_differences.append(qualitative_difference)
                row.append(
                    f"Self: {self_score}\nPartner: {partner_score}\nAverage: {average}\nDiff (self - partner): {qualitative_difference}"
                )
                self.scores[qualitative_subject].append(average)
            row.append(
                round(statistics.fmean(qualitative_differences), 2)
            )  # average qualitative difference
            self.scores["Qualitative Difference"].append(
                round(statistics.fmean(qualitative_differences), 2)
            )
            quantitative_overall_differences = []
            for quantitative_overall_subject in json_file["info"][
                "quantitative_overall_subjects"
            ]:
                self_score = json_file[self.id][quantitative_overall_subject][0]
                partner_score = json_file[self.id][quantitative_overall_subject][1]
                average = round(
                    statistics.fmean(json_file[self.id][quantitative_overall_subject]),
                    2,
                )
                quantitative_overall_difference = self_score - partner_score
                quantitative_overall_differences.append(quantitative_overall_difference)
                row.append(
                    f"Self: {self_score}\nPartner: {partner_score}\nAverage: {average}\nDiff (self - partner): {quantitative_overall_difference}"
                )
                self.scores[quantitative_overall_subject].append(average)
                self.scores["Project Contribution Difference"].append(
                    round(statistics.fmean(quantitative_overall_differences), 2)
                )  # since contribution is the only one here
        self.detailed_scores.append(row)

    def __stringify_subjects(self, subjects: list) -> str:
        result = "("
        cur_line = ""
        for subject in subjects:
            if subject == subjects[-1]:
                if len(cur_line + subject) >= 45:
                    result += cur_line + "\n" + subject + ")"
                else:
                    result += cur_line + subject + ")"
            else:
                if len(cur_line + subject) >= 45:
                    result += cur_line + "\n"
                    cur_line = subject + ", "
                else:
                    cur_line += subject + ", "
        return result

    def __make_header(self, json_file: dict) -> list:
        header = ["Categories"]
        for qualitative_subject in json_file["info"]["qualitative_subjects"]:
            header.append(qualitative_subject)
        # TODO: make average_qualitative_difference_str its own function
        average_qualitative_difference_str = f"Average Qualitative Difference\n{self.__stringify_subjects(json_file['info']['qualitative_subjects'])}"
        header.append(average_qualitative_difference_str)
        # since there's only one quantitative_overall_subject (contribution)
        # we won't have an "Average Quantitative Overall Difference" column
        for quantitative_overall_subject in json_file["info"][
            "quantitative_overall_subjects"
        ]:
            header.append(quantitative_overall_subject)
        return header


def find_partner_eval_ag(
    course: canvasapi.course.Course,
) -> canvasapi.assignment.AssignmentGroup:
    # returns AssignmentGroup named "Partner Evaluations"
    # ends program if no AssignmentGroup is found
    partner_eval_ag = None
    for ag in course.get_assignment_groups():
        if ag.name == "Partner Evalulations":
            partner_eval_ag = ag

    if partner_eval_ag is None:
        print('"Partner Evaluations" category does not exist!')
        print("Cannot grade, so ending program now")
        exit(1)

    return course.get_assignment_group(partner_eval_ag.id, include=["assignments"])


def make_student_id_map(course: canvasapi.course.Course) -> dict:
    # initially creates a dict where keys are student names and value is list [SID, canvas ID]
    # returns a dict where keys are student names and value is canvas ID (2nd element)
    # FIXME: messy way to handle dupes
    raw_students = defaultdict(list)
    dup_list = set()
    for raw_student in course.get_users(sort="username", enrollment_type=["student"]):
        if (
            raw_student.sis_user_id is None
        ):  # FIXME: delete for real class; not all sandbox student have SID
            raw_student.sis_user_id = random.randint(0, 100)

        if raw_student.sortable_name in dup_list:
            SID = str(raw_student.sis_user_id)
            raw_students[raw_student.sortable_name + " (XXXXX" + SID[-4:] + ")"].extend(
                [raw_student.sis_user_id, raw_student.id]
            )
        elif raw_student.sortable_name in raw_students.keys():
            dup_list.add(raw_student.sortable_name)

            # rewrite the initial dupe student to include their id
            orignal_SID = str(raw_students[raw_student.sortable_name])
            raw_students[
                raw_student.sortable_name + " (XXXXX" + orignal_SID[-4:] + ")"
            ].extend(raw_students[raw_student.sortable_name])
            raw_students.pop(raw_student.sortable_name)

            dup_SID = str(raw_student.sis_user_id)
            raw_students[
                raw_student.sortable_name + " (XXXXX" + dup_SID[-4:] + ")"
            ].extend([raw_student.sis_user_id, raw_student.id])
        else:
            raw_students[raw_student.sortable_name].extend(
                [raw_student.sis_user_id, raw_student.id]
            )

    student_id_map = {student: raw_students[student][1] for student in raw_students}
    return student_id_map


def make_partner_id_map(
    quiz_grade: dict,
    student_id_map: dict,
    canvas_questions: list,
    json_questions: list,
    quiz_errors: dict,
    solo_submissions: list,
) -> dict:
    # returns a dict where keys are student canvas ID and value is partner's canvas ID
    # all parings in this dict are valid

    question_stats = None
    for _ in canvas_questions:
        question_info = json_questions[_["position"] - 1]
        if question_info["question_name"] == "Partner Identification":
            question_stats = _

    potential_pairings = {}
    final_pairings = {}
    for answer in question_stats["answers"]:
        try:
            # get the partner_id
            if answer["text"] == "I did not submit with a partner.":
                partner_id = "Solo Submission"
            else:
                partner_id = student_id_map[answer["text"]]

            for index, user_id in enumerate(answer["user_ids"]):
                potential_pairings[user_id] = partner_id
                if partner_id == "Solo Submission":
                    quiz_grade[user_id]["valid_solo_submission"].append(True)
                    solo_submissions.append(f'{user_id}: {answer["user_names"][index]}')
                else:
                    quiz_grade[user_id]["valid_solo_submission"].append(False)

        except KeyError:  # skip responses that don't correspond to students
            continue
    # check that each pair claimed each other
    for student_id in quiz_grade["info"]["submissions"]:
        partner_id = potential_pairings[student_id]
        if partner_id == "Solo Submission":
            final_pairings[student_id] = "Solo Submission"
            continue
        if potential_pairings[partner_id] != student_id:
            quiz_errors[student_id].append(f"Cannot verify partnership")
            final_pairings[student_id] = "Unknown"
        else:
            final_pairings[student_id] = partner_id

    return final_pairings


def parse_qualitative_self_evals(
    quiz_grade: dict,
    canvas_questions: list,
    json_questions: list,
    quiz_errors: dict,
) -> None:
    # maps students self evaluations to themselves
    qual_mappings = {
        "Strongly disagree": 1,
        "Disagree": 2,
        "Agree": 3,
        "Strongly agree": 4,
    }
    subjects = []
    # parse through each qualitative_self question
    for question_stats in canvas_questions:
        question_info = json_questions[question_stats["position"] - 1]
        if (
            question_info["grader_info"]["category"] != "qualitative_self"
            or not question_info["grader_info"]["include_in_grade"]
        ):
            continue
        subject = question_info["question_name"]
        subjects.append(subject)
        for answer in question_stats["answers"]:
            try:
                for user_id in answer["user_ids"]:
                    quiz_grade[user_id][subject].append(qual_mappings[answer["text"]])
            except KeyError:  # skip responses that have no students
                continue
    quiz_grade["info"]["qualitative_subjects"] = subjects
    # parse through each submission and make sure that they submitted correctly
    for student_id in quiz_grade["info"]["submissions"]:
        for subject in subjects:
            if (
                subject not in quiz_grade[student_id]
                or len(quiz_grade[student_id][subject]) != 1
            ):
                quiz_errors[student_id].append(f"Missing self {subject} evaluation")
                quiz_grade[student_id][subject].append(1)  # default score


def parse_qualitative_partner_evals(
    quiz_grade: dict,
    canvas_questions: list,
    json_questions,
    partner_id_map: dict,
    quiz_errors: dict,
) -> None:
    # maps parterns's partner evaluation to their partner
    qual_mappings = {
        "Strongly disagree": 1,
        "Disagree": 2,
        "Agree": 3,
        "Strongly agree": 4,
    }
    # parse through each qualitative_partner question
    for question_stats in canvas_questions:
        question_info = json_questions[question_stats["position"] - 1]
        if (
            question_info["grader_info"]["category"] != "qualitative_partner"
            or not question_info["grader_info"]["include_in_grade"]
        ):
            continue
        subject = question_info["question_name"]
        for answer in question_stats["answers"]:
            try:
                for user_id in answer["user_ids"]:
                    if answer["text"] == "No Answer":
                        quiz_errors[user_id].append(
                            f"Missing partner {subject} evaluation"
                        )

                    partner_id = partner_id_map[user_id]
                    if partner_id == "Unknown" or partner_id == "Solo Submission":
                        continue
                    quiz_grade[partner_id][subject].append(
                        qual_mappings[answer["text"]]
                    )
            except KeyError:  # skip responses that have no students
                continue
    # parse through each submission and make sure that they submitted correctly
    for student_id in quiz_grade["info"]["submissions"]:
        for subject in quiz_grade["info"]["qualitative_subjects"]:
            if partner_id_map[student_id] == "Unknown":
                quiz_grade[student_id][subject].append(1)  # misidentified partner -> 1
            else:
                if (
                    len(quiz_grade[student_id][subject]) != 2
                    and partner_id_map[student_id] != "Solo Submission"
                ):
                    # student's partner did not evaluate student on this subject
                    # give student their own score as evaluation
                    quiz_grade[student_id][subject].append(
                        quiz_grade[student_id][subject][0]
                    )


def parse_quantitative_overall_evals(
    quiz_grade: dict,
    canvas_questions: list,
    json_questions: list,
    partner_id_map: dict,
    quiz_errors: dict,
):
    contrib_mappings = {
        "No Answer": None,
        "0% vs 100% ==> Your partner did (almost) everything while you didn't do (almost) anything": 0,
        "25% vs 75% ==> Your partner contributed substantially more than you": 0.25,
        "50% / 50% ==> You and your partner contributed (almost) equally": 0.5,
        "75% vs 25% ==> You contributed substantially more than your partner": 0.75,
        "100% vs 0% ==> You did (almost) everything while your partner didn't do (almost) anything": 1,
    }
    subjects = []
    # parse through each quantitative_overall question
    for question_stats in canvas_questions:
        question_info = json_questions[question_stats["position"] - 1]
        if (
            question_info["grader_info"]["category"] != "quantitative_overall"
            or not question_info["grader_info"]["include_in_grade"]
        ):
            continue
        subject = question_info["question_name"]
        subjects.append(subject)

        # make sure that each student's subject is a list of 2 elements
        for student_id in quiz_grade["info"]["submissions"]:
            quiz_grade[student_id][subject] = [None for _ in range(2)]

        for answer in question_stats["answers"]:
            try:
                for user_id in answer["user_ids"]:
                    partner_id = partner_id_map[user_id]
                    if partner_id == "Solo Submission":
                        continue
                    # get self contribution
                    quiz_grade[user_id][subject][0] = contrib_mappings[answer["text"]]

                    # get partner contribution
                    if partner_id == "Unknown":
                        continue
                    quiz_grade[partner_id][subject][1] = (
                        1 - contrib_mappings[answer["text"]]
                        if contrib_mappings[answer["text"]] is not None
                        else None
                    )
            except KeyError:  # skip responses that have no students
                continue
    quiz_grade["info"]["quantitative_overall_subjects"] = subjects
    # parse through each submission and make sure that they submitted correctly
    for student_id in quiz_grade["info"]["submissions"]:
        for subject in quiz_grade["info"]["quantitative_overall_subjects"]:
            if partner_id_map[student_id] == "Solo Submission":
                quiz_grade[student_id][subject] = [1]
            else:
                # student did not answer so give them 0 in contribution
                if quiz_grade[student_id][subject][0] is None:
                    quiz_grade[student_id][subject][0] = 0
                    quiz_errors[student_id].append(f"Missing {subject} evaluation")

                # student's partner did not answer (don't need to error log since
                # it will be error logged when parsing student's partner)
                if quiz_grade[student_id][subject][1] is None:
                    quiz_grade[student_id][subject][1] = (
                        quiz_grade[student_id][subject][0]
                        if quiz_grade[student_id][subject][0] is not None
                        else 0
                    )


def update_quiz_assignment_grade(
    course: canvasapi.course.Course,
    assignment: canvasapi.assignment.Assignment,
    quiz_grade: dict,
    quiz_errors: dict,
) -> None:
    # TODO: move the validator assignment into it's own function
    # TODO: move the assignment override into it's own function
    # TODO: make a validator assignment assignment group?
    validator_assignment = course.create_assignment(
        assignment={
            "name": f"{assignment.name} Validator",
            "description": f"Whether you submitted {assignment.name} correctly. If you received a 0, please go back and resubmitt {assignment.name} with the commented corrections.",
            "assignment_group_id": assignment.assignment_group_id,
            "submission_types": ["none"],
            "points_possible": 1,
            "due_at": datetime.datetime.now().isoformat(),
            "lock_at": datetime.datetime.now().isoformat(),
            "unlock_at": datetime.datetime.now().isoformat(),
            "published": True,
        }
    )
    grade_data = defaultdict(dict)
    for student_id in quiz_grade["info"]["submissions"]:
        if student_id in quiz_errors:
            grade_data[student_id]["posted_grade"] = 0
            grade_data[student_id]["text_comment"] = ",\n".join(
                [str(error) for error in quiz_errors[student_id]]
            )
        else:
            grade_data[student_id]["posted_grade"] = 1
    validator_assignment.submissions_bulk_update(grade_data=grade_data)
    if len(quiz_errors.keys()) == 0:  # all students submitted perfectly
        return
    else:
        assignment.create_override(
            assignment_override={
                "student_ids": list(quiz_errors.keys()),
                "title": f"{assignment.name} make up override",
                "unlock_at": datetime.datetime.now(),
                "due_at": datetime.datetime.now() + datetime.timedelta(days=2),
                "lock_at": datetime.datetime.now() + datetime.timedelta(days=2),
            }
        )
