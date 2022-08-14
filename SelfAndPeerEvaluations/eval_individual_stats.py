"""Internal class to store indivdiaul student evaluation grades

This class is not intended to be used outside of the scripts it's called from.
"""
from collections import defaultdict, deque
import csv
import json
import os
import statistics
from typing import Union

JsonValue = Union[str, int, float, bool, list["JsonValue"], "JsonDict"]
JsonDict = dict[str, JsonValue]


class EvalIndividualStats:
    """Class to store an individual student's evaluation grades and final, overall grade
    :param name: the sortable name of the student (e.g. Smith, John)
    :param id: the Canvas ID of the student
    :param files: the list of quiz report files to grade the student on
    member vars
    :var self.name:  the cleaned name of the student (e.g. SmithJohn)
    :var self.id: the Canvas ID of the student
    :var self.files: the list of quiz report files to grade the student on
    :var self.qualitative_subjects: the list of qualitative subjects for qualitative subject categorization
    :var self.scores: all values associated with a student based on quiz reports
    :var self.detailed_scores: self.scores formatted for CSV writing
    :var self.csv_file_path: the path where the studuent score breakdown will be
    :var self.final_score: the final, overall score the student will get
    public functions
    write_to_csv()
    """

    def __init__(self, name: str, id: int, files: list[str], csv_report_path: str):
        self.name = "".join(filter(str.isalnum, name))
        self.id = str(id)
        self.scores = defaultdict(list[Union[int, float]])
        self.files = files

        self.qualitative_subjects = self.__get_qualitative_subjects()

        self.csv_file_path = os.path.join(csv_report_path, f"{self.name}.csv")

        self.final_score = self.__get_final_score()
        self.__format_csv_info()

    def write_to_csv(self) -> None:
        """
        write individual student stats to a report
        """
        with open(self.csv_file_path, "w") as f:
            writer = csv.writer(f)
            writer.writerows(self.csv_file_info)

    def __get_qualitative_subjects(self) -> list[str]:
        with open(self.files[0], "r") as f:
            json_file = json.load(f)
            return json_file["info"]["qualitative_subjects"]

    def __get_final_score(self) -> float:
        self.__get_detailed_scores()
        self.__calculate_qualitative_score()
        self.__calculate_contribution_score()
        with open(self.files[0], "r") as f:
            json_file = json.load(f)
            qualitative_weight = json_file["info"]["weighting"]["qualitative"]
            contribution_weight = json_file["info"]["weighting"]["project_contribution"]
        final_score = round(
            qualitative_weight * self.qualitative_score
            + contribution_weight * self.contribution_score,
            2,
        )
        return final_score

    def __get_detailed_scores(self) -> None:
        """
        gets the individual student detailed score breakdown from all assignments
        :returns: None
        :modifies: self.detailed_scores
        """
        self.detailed_scores = []
        self.__read_files(self.files)
        self.__get_averages()
        # transpose detailed scores
        self.detailed_scores = [
            [row[i] for row in self.detailed_scores]
            for i in range(len(self.detailed_scores[0]))
        ]

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

    def __give_default_scores(self, json_file: JsonDict, row: list[str]) -> None:
        """
        Gives a student scores of self 1, partner 1 in all qualitative subjects and
        0 in project contribution
        since they did not submit this assignment at all
        :returns: None
        :modifies: row (where row is the assignment scores to be written in the CSV)
        """
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

    def __give_solo_submission_scores(
        self, json_file: JsonDict, row: list[str]
    ) -> None:
        """
        Gives a student solo submission scores since they are a solo submission
        :returns: None
        :modifies: row (where row is the assignment scores to be written in the CSV)
        """
        for qualitative_subject in json_file["info"]["qualitative_subjects"]:
            self_score = json_file[self.id][qualitative_subject][0]
            row.append(
                f"Self: {self_score}\nPartner: N/A\nAverage: {self_score}\nDiff (self - partner): 0"
            )
            self.scores[qualitative_subject + "Self"].append(self_score)
            # this is a solo submission, so no partner
            self.scores[qualitative_subject + "Average"].append(self_score)
            self.scores[qualitative_subject + "Diff"].append(0)
        row.append(0)  # average qualitative difference
        self.scores["Qualitative Difference"].append(0)
        self_score = json_file[self.id]["Project Contribution"][0]
        row.append(
            f"Self: {self_score}\nPartner: N/A\nAverage: {self_score}\nDiff (self - partner): 0"
        )
        self.scores["Project Contribution" + "Self"].append(self_score)
        # this is a solo submission, so no partner
        self.scores["Project Contribution" + "Average"].append(self_score)
        self.scores["Project Contribution" + "Diff"].append(0)

    def __give_quiz_scores(self, json_file: JsonDict, row: list[str]) -> None:
        """
        Gives a student self and partner submission scores since they submitted with a partner
        :returns: None
        :modifies: row (where row is the assignment scores to be written in the CSV)
        """
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

    def __read_files(self, files: list[str]) -> None:
        """
        parse through all the quiz reports and writes info about
        qualitative_subjects to self.qualitative_subjects
        """
        # make the detailed score header just once
        with open(files[0], "r") as f:
            detailed_scores_header = self.__make_detailed_header(json.load(f))
            self.detailed_scores.append(detailed_scores_header)

        for file in files:
            with open(file, "r") as f:
                json_file = json.load(f)
                self.__parse_quiz_grade(json_file)

    def __write_final_score(self) -> list[Union[float, int, str]]:
        """
        :returns: a properly formated CSV row for the final score output
        """
        return [
            "Final Score\n(40% Qualitative + 60% Project Contribution)",
            self.final_score,
        ]

    def __write_qualitative_score(self) -> list[list[Union[float, int, str]]]:
        """
        :returns: properly formated CSV rows for the qualitative score output
        """
        overall_qualitative_str = f"Overall Qualitative Averages\n{self.__stringify_subjects(self.qualitative_subjects)}"
        header = [
            "",
            "Score\n(if (diff > 0); then score=(avg - diff)/4*100;\nelse score=(avg - diff/2)/4*100)",
            f"Average of {overall_qualitative_str}",
            "Difference\n(Overall Average of\nAverage Qualitative Difference)",
        ]
        row = [
            "Qualitative",
            self.qualitative_score,
            self.average_qualitative,
            self.average_qualitative_difference,
        ]
        return [row, header]

    def __calculate_qualitative_score(self) -> None:
        """
        calculates the overall qualitative score
        :returns: None
        :modifies: self.qualitative_score
        """
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

    def __write_contribution_score(self) -> list[list[Union[float, int, str]]]:
        """
        :returns: properly formated CSV rows for the contribution score output
        """
        header = [
            "",
            "Score\n(if (diff > 0); then score=(avg - diff)/50*100*100;\nelse score=(avg - diff/2)/50*100*100)",
            "Average Project Contribution",
            "Project Contribution Difference",
        ]
        row = [
            "Project Contribution",
            self.contribution_score,
            self.average_project_contribution,
            self.average_project_contribution_difference,
        ]
        return [row, header]

    def __calculate_contribution_score(self) -> None:
        """
        calculates the overall (project) contribution score
        :returns: None
        :modifies: self.contribution_score
        """
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
        """
        calculates the overall averages for each qualitative subject and the overall average of the qualitative category
        :returns: None
        :modifies: averages_values: a list of formatted cateogry averages
                   self.average_qualitative: the overall qualitative cateogry average
                   self.average_qualitative_difference: the overall qualitative diff average
        """
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
        """
        calculates the overall project contribution average
        :returns: None
        :modifies: averages_values: a list of formatted cateogry averages
                   self.average_project_contribution: the overall contrib cateogry average
                   self.average_project_contribution_difference: the overall contrib diff average
        """
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
        """
        appends a row of "averages_values" to self.detailed_scores for CSV writing later
        "averages_values" contains averages of self, partner, average, diff for each
        qualitative category and project contribution
        :returns: None
        :modifies: self.detailed_scores
        """
        averages_values = ["Overall Average\n* -> Not used in Final Grade Calculation"]
        self.__get_qualitative_averages(averages_values)
        self.__get_project_contribution_averages(averages_values)
        self.detailed_scores.append(averages_values)

    def __parse_quiz_grade(self, json_file: JsonDict) -> None:
        """
        goes through a single quiz report and extracts the values for a
        specific student
        :returns: None
        :modifies: self.detailed_scores
        """
        row = []
        row.append(json_file["info"]["quiz_name"])
        if self.id not in json_file:
            self.__give_default_scores(json_file, row)
        elif json_file[self.id]["valid_solo_submission"]:
            self.__give_solo_submission_scores(json_file, row)
        else:
            self.__give_quiz_scores(json_file, row)
        self.detailed_scores.append(row)

    def __stringify_subjects(self, subjects: list[str]) -> str:
        """
        concatinates a list of subjects into a readable string where
        each line is roughly at most 45 characters
        :returns: one string of all subjects
        """
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

    def __make_detailed_header(self, json_file: JsonDict) -> list[str]:
        """
        creates a header for the detailed_scores section of the CSV that
        contains each qualitative subject and project contribution and overall averages
        :returns: list of strings to be in the header
        """
        header = ["Categories"]
        for qualitative_subject in json_file["info"]["qualitative_subjects"]:
            header.append(qualitative_subject)
        average_qualitative_difference_str = f"Average Qualitative Difference\n{self.__stringify_subjects(json_file['info']['qualitative_subjects'])}"
        header.append(average_qualitative_difference_str)
        # since there's only one quantitative_overall_subject (contribution)
        # we won't have an "Average Quantitative Overall Difference" column
        header.append("Project Contribution")
        return header
