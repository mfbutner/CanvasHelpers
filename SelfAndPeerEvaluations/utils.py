import canvasapi
from collections import defaultdict
import csv
from collections import deque
import json
import statistics
import random


class PartnerEvalQuizIndividualStats:
    def __init__(self, name: str, id: int, files: list):
        self.name = "".join(filter(str.isalnum, name))
        self.id = str(id)
        self.scores = defaultdict(list)

        self.detailed_scores = []
        self.qualitative_subjects = None
        self.quantitative_overall_subjects = None

        self.csv_file_path = (
            f"./quiz_results/individual_student_reports/{self.name}.csv"
        )
        f = open(self.csv_file_path, "w")
        self.writer = csv.writer(f)

        self.__read_files(files)
        self.__get_averages()
        # transpose detailed scores
        self.detailed_scores = [
            [row[i] for row in self.detailed_scores]
            for i in range(len(self.detailed_scores[0]))
        ]
        self.__format_csv_info()
        self.writer.writerows(self.csv_file_info)
        f.close()

    def __format_csv_info(self) -> None:
        """
        formats self.csv_file_info for writing
        """
        self.csv_file_info = deque(self.detailed_scores)
        self.csv_file_info.appendleft(["diff = self - partner"])
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

    def __give_default_scores(self, json_file: dict, row: list) -> None:
        # default self&partner qualitative score is 1
        for qualitative_subject in json_file["info"]["qualitative_subjects"]:
            row.append("Self: 1\nPartner: 1\nAverage: 1\nDiff (self - partner): 0")
            self.scores[qualitative_subject + "Self"].append(1)
            self.scores[qualitative_subject + "Partner"].append(1)
            self.scores[qualitative_subject + "Average"].append(1)
            self.scores[qualitative_subject + "Diff"].append(0)

        row.append("0")  # average qualitative difference
        self.scores["Qualitative Difference"].append(0)

        # default self&partner contribution score is 0
        row.append("Self: 0\nPartner: 0\nAverage: 0\nDiff (self - partner): 0")
        self.scores["Project Contribution" + "Self"].append(0)
        self.scores["Project Contribution" + "Partner"].append(0)
        self.scores["Project Contribution" + "Average"].append(0)
        self.scores["Project Contribution" + "Diff"].append(0)

    def __give_solo_submission_scores(self, json_file: dict, row: list) -> None:
        for qualitative_subject in json_file["info"]["qualitative_subjects"]:
            self_score = json_file[self.id][qualitative_subject][0]
            row.append(
                f"Self: {self_score}\nPartner: N/A\nAverage: {self_score}\nDiff (self - partner): 0"
            )
            self.scores[qualitative_subject + "Self"].append(self_score)
            self.scores[qualitative_subject + "Average"].append(self_score)
            self.scores[qualitative_subject + "Diff"].append(0)
        row.append(0)  # average qualitative difference
        self.scores["Qualitative Difference"].append(0)
        for quantitative_overall_subject in json_file["info"][
            "quantitative_overall_subjects"
        ]:
            self_score = json_file[self.id][quantitative_overall_subject][0]
            row.append(
                f"Self: {self_score}\nPartner: N/A\nAverage: {self_score}\nDiff (self - partner): 0"
            )
            self.scores["Project Contribution" + "Self"].append(self_score)
            self.scores["Project Contribution" + "Average"].append(self_score)
            self.scores["Project Contribution" + "Diff"].append(0)

    def __give_quiz_scores(self, json_file: dict, row: list) -> None:
        qualitative_differences = []
        for qualitative_subject in json_file["info"]["qualitative_subjects"]:
            self_score = json_file[self.id][qualitative_subject][0]
            partner_score = json_file[self.id][qualitative_subject][1]
            average_score = round(
                statistics.fmean(json_file[self.id][qualitative_subject]), 2
            )
            qualitative_difference = self_score - partner_score
            qualitative_differences.append(qualitative_difference)
            row.append(
                f"Self: {self_score}\nPartner: {partner_score}\nAverage: {average_score}\nDiff (self - partner): {qualitative_difference}"
            )
            self.scores[qualitative_subject + "Self"].append(self_score)
            self.scores[qualitative_subject + "Partner"].append(partner_score)
            self.scores[qualitative_subject + "Average"].append(average_score)
            self.scores[qualitative_subject + "Diff"].append(qualitative_difference)
        row.append(
            round(statistics.fmean(qualitative_differences), 2)
        )  # average qualitative difference
        self.scores["Qualitative Difference"].append(
            round(statistics.fmean(qualitative_differences), 2)
        )
        self_score = json_file[self.id]["Project Contribution"][0]
        partner_score = json_file[self.id]["Project Contribution"][1]
        average_score = round(
            statistics.fmean(json_file[self.id]["Project Contribution"]),
            2,
        )
        contrib_diff = self_score - partner_score
        row.append(
            f"Self: {self_score}\nPartner: {partner_score}\nAverage: {average_score}\nDiff (self - partner): {contrib_diff}"
        )
        self.scores["Project Contribution" + "Self"].append(self_score)
        self.scores["Project Contribution" + "Partner"].append(partner_score)
        self.scores["Project Contribution" + "Average"].append(average_score)
        self.scores["Project Contribution" + "Diff"].append(contrib_diff)

    def __read_files(self, files: list) -> None:
        """
        parse through all the quiz reports and writes info about
        qualitative_subjects to self.qualitative_subjects
        """
        detailed_scores_header = []
        for file in files:
            with open(file, "r") as f:
                json_file = json.load(f)
                if len(detailed_scores_header) == 0:  # only make the header once
                    detailed_scores_header = self.__make_detailed_header(json_file)
                    self.detailed_scores.append(detailed_scores_header)
                if self.qualitative_subjects is None:  # only get once
                    self.qualitative_subjects = json_file["info"][
                        "qualitative_subjects"
                    ]
                self.__parse_quiz_grade(json_file)

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

    def __get_qualitative_averages(self, averages_values: list) -> None:
        qualitative_averages = []

        for qualitative_subject in self.qualitative_subjects:
            self_avg = round(
                statistics.fmean(self.scores[qualitative_subject + "Self"]), 2
            )
            partner_avg = (
                round(statistics.fmean(self.scores[qualitative_subject + "Partner"]), 2)
                if self.scores[qualitative_subject + "Partner"] is not None
                else "N/A"
            )
            avg_avg = round(
                statistics.fmean(self.scores[qualitative_subject + "Average"]), 2
            )
            diff_avg = round(
                statistics.fmean(self.scores[qualitative_subject + "Diff"]), 2
            )
            averages_values.append(
                f"Self*: {self_avg}\nPartner*: {partner_avg}\nAverage: {avg_avg}\nDiff*: {diff_avg}"
            )
            qualitative_averages.append(avg_avg)
        self.average_qualitative = round(statistics.fmean(qualitative_averages), 2)

        averages_values.append(
            round(statistics.fmean(self.scores["Qualitative Difference"]), 2)
        )
        self.average_qualitative_difference = round(float(averages_values[-1]), 2)

    def __get_project_contribution_averages(self, averages_values: list) -> None:
        self_avg = round(
            statistics.fmean(self.scores["Project Contribution" + "Self"]), 2
        )
        partner_avg = (
            round(statistics.fmean(self.scores["Project Contribution" + "Partner"]), 2)
            if self.scores["Project Contribution" + "Partner"] is not None
            else "N/A"
        )
        avg_avg = round(
            statistics.fmean(self.scores["Project Contribution" + "Average"]), 2
        )
        diff_avg = round(
            statistics.fmean(self.scores["Project Contribution" + "Diff"]), 2
        )
        averages_values.append(
            f"Self*: {self_avg}\nPartner*: {partner_avg}\nAverage: {avg_avg}\nDiff: {diff_avg}"
        )
        self.average_project_contribution = avg_avg
        self.average_project_contribution_difference = diff_avg

    def __get_averages(self) -> None:
        averages_values = ["Overall Average\n* -> Not used in Final Grade Calculation"]
        self.__get_qualitative_averages(averages_values)
        self.__get_project_contribution_averages(averages_values)
        self.detailed_scores.append(averages_values)

    def __parse_quiz_grade(self, json_file: dict):
        row = []
        row.append(json_file["info"]["quiz_name"])
        if self.id not in json_file:
            self.__give_default_scores(json_file, row)
        elif json_file[self.id]["valid_solo_submission"][0]:
            self.__give_solo_submission_scores(json_file, row)
        else:
            self.__give_quiz_scores(json_file, row)
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

    def __make_detailed_header(self, json_file: dict) -> list:
        header = ["Categories"]
        for qualitative_subject in json_file["info"]["qualitative_subjects"]:
            header.append(qualitative_subject)
        average_qualitative_difference_str = f"Average Qualitative Difference\n{self.__stringify_subjects(json_file['info']['qualitative_subjects'])}"
        header.append(average_qualitative_difference_str)
        # since there's only one quantitative_overall_subject (contribution)
        # we won't have an "Average Quantitative Overall Difference" column
        header.append("Project Contribution")
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
    """
    Creates a mapping of unique student sortable names to canvas ID's
    If student sortable names are duplicate, then last 4 or 5 digits are appended to student sortable name
    :returns: dict where key is unique sortable name and value is canvas ID
    """
    raw_students = defaultdict(list)
    dup_list = set()
    for raw_student in course.get_users(sort="username", enrollment_type=["student"]):
        if (
            raw_student.sis_user_id is None
        ):  # FIXME: delete for real class; not all sandbox student have SID
            raw_student.sis_user_id = random.randint(0, 100)

        if raw_student.sortable_name in dup_list:
            add_another_duplicate_student(raw_student, raw_students)
        elif raw_student.sortable_name in raw_students.keys():
            add_first_duplicate_student(raw_student, dup_list, raw_students)
        else:
            raw_students[raw_student.sortable_name] = [
                raw_student.sis_user_id,
                raw_student.id,
            ]

    student_id_map = {student: raw_students[student][1] for student in raw_students}
    return student_id_map


def add_another_duplicate_student(
    dupe_student: canvasapi.user.User, raw_students: dict
) -> None:
    """
    Adds in the duplicate student with their last 4 or 5 SID digits appened to their name
    Modifies students in raw_students if necessary
    :param dupe_student: the duplicate student to be added to raw_students
    :param raw_students: the dict of all students
    :returns: None, instead, raw_students is directly modified
    """
    duplicate_name = dupe_student.sortable_name
    dupe_SID = str(dupe_student.sis_user_id)
    if duplicate_name + " (XXXXX" + dupe_SID[-4:] + ")" in raw_students:
        in_dict_SID = raw_students[duplicate_name + " (XXXXX" + dupe_SID[-4:] + ")"][0]
        raw_students.pop(raw_students[duplicate_name + " (XXXXX" + dupe_SID[-4:] + ")"])
        raw_students[duplicate_name + " (XXXXX" + in_dict_SID[-5:] + ")"] = in_dict_SID
        raw_students[duplicate_name + " (XXXXX" + dupe_SID[-5:] + ")"] = [
            dupe_SID,
            dupe_student.id,
        ]
    else:
        raw_students[duplicate_name + " (XXXXX" + dupe_SID[-4:] + ")"] = [
            dupe_SID,
            dupe_student.id,
        ]


def add_first_duplicate_student(
    dupe_student: canvasapi.user.User, dupe_list: set, raw_students: dict
) -> None:
    """
    Adds in the duplicate student with their last 4 or 5 SID digits appended to their name
    Also removes the original student in the raw_students dict and
    adds the original student back with their last 4 or 5 SID digits appended to their name
    :param dupe_student: the duplicate student to be added to raw_students
    :param dup_list: the list of sortable_names that have duplicate students
    :param raw_students: the dict of all students
    :returns: None, instead, dup_list and raw_students are directly modified
    """
    duplicate_name = dupe_student.sortable_name
    dupe_list.add(duplicate_name)

    in_dict_SID = str(raw_students[dupe_student.sortable_name][0])
    dupe_SID = str(dupe_student.sis_user_id)
    for index in range(4, 6):
        if in_dict_SID[-index:] == dupe_SID[-index:]:
            continue
        # add duplicate student in with appened SID
        raw_students[duplicate_name + " (XXXXX" + dupe_SID[-index:] + ")"] = [
            dupe_SID,
            dupe_student.id,
        ]
        # add original student back in with appened SID
        raw_students[
            duplicate_name + " (XXXXX" + in_dict_SID[-index:] + ")"
        ] = raw_students[dupe_student.sortable_name]
        raw_students.pop(dupe_student.sortable_name)
        break
