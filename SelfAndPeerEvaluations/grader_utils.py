import canvasapi
from collections import defaultdict
import csv
import datetime
import json
import os
import statistics
import random


class PartnerEvalQuizIndividualStats:
    def __init__(self, name: str, id: int):
        self.name = "".join(filter(str.isalnum, name))
        self.id = str(id)
        self.scores = defaultdict(list)

        self.header = []
        self.qualitative_subjects = None
        self.quantitative_overall_subjects = None

        self.csv_file_path = (
            f"./quiz_results/individual_student_reports/{self.name}.txt"
        )
        f = open(self.csv_file_path, "w")
        self.writer = csv.writer(f)

        for filename in os.listdir("./quiz_results/quiz_reports"):
            with open(os.path.join("./quiz_results/quiz_reports/", filename), "r") as f:
                json_file = json.load(f)
                if len(self.header) == 0:  # only make the header once
                    self.__make_header(json_file)
                    self.writer.writerow(self.header)
                if self.qualitative_subjects is None:  # only get once
                    self.qualitative_subjects = json_file["info"][
                        "qualitative_subjects"
                    ]
                if self.quantitative_overall_subjects is None:  # only get once
                    self.quantitative_overall_subjects = json_file["info"][
                        "quantitative_overall_subjects"
                    ]
                self.__parse_quiz_grade(json_file)

        self.writer.writerow(["" for _ in range(len(self.header))])  # empty row
        self.__get_averages()
        self.writer.writerow(["" for _ in range(len(self.header))])  # empty row
        self.__write_qualitative_score()
        self.writer.writerow(["" for _ in range(len(self.header))])  # empty row
        self.__write_contribution_score()
        self.writer.writerow(["" for _ in range(len(self.header))])  # empty row
        self.__write_final_score()
        f.close()

    def __write_final_score(self) -> None:
        self.final_score = 0.4 * self.qualitative_score + 0.6 * self.contribution_score
        self.writer.writerow(["Final Score", self.final_score])

    def __write_qualitative_score(self) -> None:
        header = [
            "",
            "Average (Average of Qualitative Cateogry Averages in row above)",
            "Difference",
            "Score (if (diff > 0); then score=(avg - diff)/4*100; else score=(avg + diff/2)/4*100)",
            "Final Grade Weight",
        ]
        self.__calculate_qualitative_score()
        row = [
            "Qualitative",
            self.average_qualitative,
            self.average_qualitative_difference,
            self.qualitative_score,
            "40%",
        ]
        self.writer.writerow(header)
        self.writer.writerow(row)

    def __calculate_qualitative_score(self) -> None:
        if self.average_qualitative_difference > 0:
            self.qualitative_score = (
                (self.average_qualitative - self.average_qualitative_difference)
                / 4
                * 100
            )
        else:
            self.qualitative_score = (
                (self.average_qualitative - (self.average_qualitative_difference / 2))
                / 4
                * 100
            )

    def __write_contribution_score(self) -> None:
        header = [
            "",
            "Average Project Contribution (in row above)",
            "Project Contribution Difference",
            "Score (if (diff > 0); then score=(avg - diff)/50*100*100; else score=(avg + diff/2)/50*100*100)",
            "Final Grade Weight",
        ]
        self.__calculate_contribution_score()
        row = [
            "Project Contribution",
            self.average_project_contribution,
            self.average_project_contribution_difference,
            self.contribution_score,
            "60%",
        ]
        self.writer.writerow(header)
        self.writer.writerow(row)

    def __calculate_contribution_score(self) -> None:
        if self.average_project_contribution_difference > 0:
            self.contribution_score = (
                (
                    self.average_project_contribution
                    - self.average_project_contribution_difference
                )
                / 50
                * 100
                * 100
            )
        else:
            self.contribution_score = (
                (
                    self.average_project_contribution
                    - (self.average_project_contribution_difference / 2)
                )
                / 50
                * 100
                * 100
            )

    def __get_averages(self) -> None:
        averages_header = [""]
        averages_values = ["Values"]
        qualitative_averages = []

        for qualitative_subject in self.qualitative_subjects:
            averages_header.append(f"Average of Average {qualitative_subject}")
            averages_values.append(statistics.fmean(self.scores[qualitative_subject]))
            qualitative_averages.append(averages_values[-1])
        self.average_qualitative = statistics.fmean(qualitative_averages)

        averages_header.append("Average of Average Qualitative Difference")
        averages_values.append(statistics.fmean(self.scores["Qualitative Difference"]))
        self.average_qualitative_difference = float(averages_values[-1])

        # NOTE: there's only contribution for now
        for quantitative_overall_subject in self.quantitative_overall_subjects:
            averages_header.append(f"Average of Average {quantitative_overall_subject}")
            averages_header.append(
                f"Average of {quantitative_overall_subject} Difference"
            )
            averages_values.append(
                statistics.fmean(self.scores[quantitative_overall_subject])
            )
            self.average_project_contribution = float(averages_values[-1])
            averages_values.append(
                statistics.fmean(self.scores["Project Contribution Difference"])
            )
            self.average_project_contribution_difference = float(averages_values[-1])

        self.writer.writerow(averages_header)
        self.writer.writerow(averages_values)

    def __parse_quiz_grade(self, json_file: dict):
        row = []
        row.append(json_file["info"]["quiz_name"])
        if self.id not in json_file:
            for qualitative_subject in json_file["info"]["qualitative_subjects"]:
                row.extend([1, 1, 1, 0])
                self.scores[qualitative_subject].append(1)
            row.append(0)  # average qualitative difference
            self.scores["Qualitative Difference"].append(0)
            for quantitative_overall_subject in json_file["info"][
                "quantitative_overall_subjects"
            ]:
                row.extend([0, 0, 0, 0])
                self.scores[quantitative_overall_subject].append(0)
            self.scores["Project Contribution Difference"].append(
                0
            )  # since contribution is the only one here
            self.writer.writerow(row)
            return
        if json_file[self.id]["valid_solo_submission"][0]:
            for qualitative_subject in json_file["info"]["qualitative_subjects"]:
                self_score = json_file[self.id][qualitative_subject][0]
                row.extend([self_score, "N/A", self_score, 0])
                self.scores[qualitative_subject].append(self_score)
            row.append(0)  # average qualitative difference
            self.scores["Qualitative Difference"].append(0)
            for quantitative_overall_subject in json_file["info"][
                "quantitative_overall_subjects"
            ]:
                self_score = json_file[self.id][quantitative_overall_subject][0]
                row.extend([self_score, "N/A", self_score, 0])
                self.scores[quantitative_overall_subject].append(self_score)
            self.scores["Project Contribution Difference"].append(
                0
            )  # since contribution is the only one here
        else:
            qualitative_differences = []
            for qualitative_subject in json_file["info"]["qualitative_subjects"]:
                self_score = json_file[self.id][qualitative_subject][0]
                partner_score = json_file[self.id][qualitative_subject][1]
                average = statistics.fmean(json_file[self.id][qualitative_subject])
                qualitative_difference = self_score - partner_score
                qualitative_differences.append(qualitative_difference)
                row.extend([self_score, partner_score, average, qualitative_difference])
                self.scores[qualitative_subject].append(average)
            row.append(
                statistics.fmean(qualitative_differences)
            )  # average qualitative difference
            self.scores["Qualitative Difference"].append(
                statistics.fmean(qualitative_differences)
            )
            quantitative_overall_differences = []
            for quantitative_overall_subject in json_file["info"][
                "quantitative_overall_subjects"
            ]:
                self_score = json_file[self.id][quantitative_overall_subject][0]
                partner_score = json_file[self.id][quantitative_overall_subject][1]
                average = statistics.fmean(
                    json_file[self.id][quantitative_overall_subject]
                )
                quantitative_overall_difference = self_score - partner_score
                quantitative_overall_differences.append(quantitative_overall_difference)
                row.extend(
                    [
                        self_score,
                        partner_score,
                        average,
                        quantitative_overall_difference,
                    ]
                )
                self.scores[quantitative_overall_subject].append(average)
            self.scores["Project Contribution Difference"].append(
                statistics.fmean(quantitative_overall_differences)
            )  # since contribution is the only one here
        self.writer.writerow(row)

    def __make_header(self, json_file: dict):
        self.header.append("Assignment Name")
        for qualitative_subject in json_file["info"]["qualitative_subjects"]:
            self.header.append(f"Self {qualitative_subject}")
            self.header.append(f"Partner {qualitative_subject}")
            self.header.append(f"Average {qualitative_subject}")
            self.header.append(f"{qualitative_subject} Difference (self - partner)")
        qualitative_subjects = ", ".join(
            str(_) for _ in json_file["info"]["qualitative_subjects"]
        )
        self.header.append(f"Average Qualitative Difference ({qualitative_subjects})")
        # since there's only one quantitative_overall_subject (contribution)
        # we won't have an "Average Quantitative Overall Difference" column
        for quantitative_overall_subject in json_file["info"][
            "quantitative_overall_subjects"
        ]:
            self.header.append(f"Self {quantitative_overall_subject}")
            self.header.append(f"Partner {quantitative_overall_subject}")
            self.header.append(f"Average {quantitative_overall_subject}")
            self.header.append(
                f"{quantitative_overall_subject} Difference (self - partner)"
            )

    def get_final_grade(self):
        final_score = (
            0.4 * self.scores["engagement_score"][0]
            + 0.6 * self.scores["contribution_score"][0]
        )
        return final_score

    def __get_engagement_score(self) -> float:
        quality_avgs = []
        for quality, values in self.scores.items():
            if quality not in [
                "organization_avgs",
                "communication_avgs",
                "teamwork_avgs",
                "attitude_avgs",
                "ideas_avgs",
                "code_avgs",
            ]:
                continue
            quality_avgs.append(statistics.fmean(values))
        engagement_avg = statistics.fmean(quality_avgs)
        engagment_deviation = statistics.fmean(self.scores["deviation_1_scores"])
        if engagment_deviation > 0:
            return (engagement_avg - engagment_deviation) / 4 * 100
        else:
            return (engagement_avg - (engagment_deviation / 2)) / 4 * 100

    def __get_contribution_score(self) -> float:
        contribution_avg = statistics.fmean(self.scores["contribution_avgs"])
        contribution_deviation = statistics.fmean(self.scores["deviation_2_scores"])
        if contribution_deviation > 0:
            return (contribution_avg - contribution_deviation) / 50 * 100 * 100
        else:
            return (contribution_avg - (contribution_deviation / 2)) / 50 * 100 * 100


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

    potential_pairings = defaultdict(str)
    final_pairings = defaultdict(str)
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
    quiz = course.get_quiz(assignment.quiz_id)
    grade_data = defaultdict(dict)
    quiz_extensions = []
    for student_id in quiz_grade["info"]["submissions"]:
        if student_id in quiz_errors:
            grade_data[student_id]["posted_grade"] = 0
            grade_data[student_id]["text_comment"] = "\n".join(
                [str(error) for error in quiz_errors[student_id]]
            )
            quiz_extensions.append(
                {
                    "user_id": student_id,
                    "extra_attempts": 10,
                    "manually_unlocked": True,
                    "end_at": datetime.datetime.now() + datetime.timedelta(days=2),
                }
            )
        else:
            grade_data[student_id]["posted_grade"] = assignment.points_possible
    assignment.submissions_bulk_update(grade_data=grade_data)

    if len(quiz_extensions) == 0:
        return
    quiz.set_extensions(quiz_extensions)
