"""Internal class to store indivdiaul student evaluation grades

This class is not intended to be used outside of the scripts it's called from.
"""
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader
import json
import os
import pathlib
import statistics
from typing import Union
from utils import JsonDict


# all students are using the same template anyway, so just load once
cur_file_path = pathlib.Path(__file__)
template_path = cur_file_path.parent.resolve(True) / "templates"
environment = Environment(
    loader=FileSystemLoader(template_path), trim_blocks=True, lstrip_blocks=True
)
template = environment.get_template("report.csv")


class EvalIndividualStats:
    """Class to store an individual student's evaluation grades and final, overall grade
    :param name: the unique name of the student
    :param id: the Canvas ID of the student
    :param files: the list of quiz report files to grade the student on
    member vars
    :var self.name:  the cleaned name of the student (e.g. SmithJohn)
    :var self.id: the Canvas ID of the student
    :var self.files: the list of quiz report files to grade the student on
    :var self.qualitative_subjects: the list of qualitative subjects for qualitative subject categorization
    :var self.scores: all values associated with a student based on quiz reports alone
    :var self.averages: the average values from each category in self.scores

    :var self.qualitative_weight: grade weight of qualitative category
    :var self.average_qualitative: the average qualitative score
    :var self.average_qualitative_diff: the average qualitative score difference

    :var self.contribution_weight: grade weight of contribution category
    :var self.average_project_contribution: the average contribution score
    :var self.average_project_contribution_diff: the average contribution score difference

    :var self.final_score: the final, overall score the student will get
    :var self.csv_file_path: the path where the studuent score breakdown will be

    public functions
    ---
    write_to_csv(): write the final, overall evaluation report to a CSV
    """

    def __init__(self, name: str, id: int, files: list[str], csv_report_path: str):
        self.name = "".join(filter(str.isalnum, name))
        self.id = str(id)
        self.files = files
        self.csv_file_path = os.path.join(csv_report_path, f"{self.name}.csv")

        self.__get_metadata()
        self.assignments: list[str] = []
        self.scores: dict[str, list[Union[int, float, None]]] = defaultdict(
            list[Union[int, float, None]]
        )
        self.averages: dict[str, Union[int, float, None]] = {}

        self.final_score = self.__get_final_score()

    def write_to_csv(self) -> None:
        """
        write individual student stats to a CSV report
        :returns: None. Instead, a CSV file is written to self.csv_file_path
        """
        subjects = stringify_subjects(self.qualitative_subjects)
        average_qualitative_difference_str = (
            f"Average Qualitative Difference\n{subjects}"
        )
        overall_qualitative_str = f"Average of Overall Qualitative Averages\n{subjects}"
        content = template.render(
            obj=self,
            overall_qualitative_str=overall_qualitative_str,
            average_qualitative_diff_str=average_qualitative_difference_str,
        )
        with open(self.csv_file_path, "w") as f:
            f.write(content)

    def __get_metadata(self) -> None:
        """
        gets the qualitative_subjects, qualitative_weight, and contribution_weight
        from a single quiz report
        we assume that quiz reports all share these values in common
        :modifies: self.qualitative_subjects to store the qualitative_subjects
                   self.qualitative_weight to store the weight of qualitative category
                   self.contribution_weight to store the weight of contribution category
        """
        with open(self.files[0], "r") as f:
            json_file = json.load(f)
            self.qualitative_subjects = json_file["info"]["qualitative_subjects"]
            self.qualitative_weight = json_file["info"]["weighting"]["qualitative"]
            self.contribution_weight = json_file["info"]["weighting"][
                "project_contribution"
            ]

    def __get_final_score(self) -> float:
        """
        gets the final, overall evaluation score for a student
        :returns: the final, overall evalution score
        :modifies: self.qualitative_weight and self.contribution_weight to store the weighting of those categories
        """
        self.__get_scores(self.files)
        self.__get_qualitative_averages()
        self.__get_project_contribution_averages()
        self.__calculate_qualitative_score()
        self.__calculate_contribution_score()
        final_score = round(
            self.qualitative_weight * self.qualitative_score
            + self.contribution_weight * self.contribution_score,
            2,
        )
        return final_score

    def __get_scores(self, files: list[str]) -> None:
        """
        parse through all the quiz reports and stores quiz report scores
        into self.scores
        :param files: list of quiz report files
        :returns: None
        :modifies: self.scores to store quiz report scores
        """
        for file in files:
            with open(file) as f:
                json_file = json.load(f)
                self.__parse_quiz_grade(json_file)

    def __parse_quiz_grade(self, json_file: JsonDict) -> None:
        """
        goes through a single quiz report and extracts the values for a
        specific student
        :returns: None
        :modifies: self.assignments to store assignment names
        """
        self.assignments.append(json_file["info"]["quiz_name"])
        if self.id not in json_file:
            self.__give_default_scores()
        elif json_file[self.id]["valid_solo_submission"]:
            self.__give_solo_submission_scores(json_file)
        else:
            self.__give_quiz_scores(json_file)

    def __give_default_scores(self) -> None:
        """
        Gives a student scores of self 1, partner 1 in all qualitative subjects and
        0 in project contribution
        since they did not submit this assignment at all
        :returns: None
        :modifies: self.scores to store the quiz scores
        """
        # default self&partner qualitative score is 1
        for qualitative_subject in self.qualitative_subjects:
            self.scores[qualitative_subject + "Self"].append(1)
            self.scores[qualitative_subject + "Partner"].append(1)
            self.scores[qualitative_subject + "Average"].append(1)
            self.scores[qualitative_subject + "Diff"].append(0)

        self.scores["Qualitative Difference"].append(0)

        # default self&partner contribution score is 0
        for category in ["Self", "Partner", "Average", "Diff"]:
            self.scores["Project Contribution" + category].append(0)

    def __give_solo_submission_scores(self, json_file: JsonDict) -> None:
        """
        Gives a student solo submission scores since they are a solo submission
        :returns: None
        :modifies: self.scores to store the quiz scores
        """
        for qualitative_subject in self.qualitative_subjects:
            self_score = json_file[self.id][qualitative_subject][0]
            self.scores[qualitative_subject + "Self"].append(self_score)
            self.scores[qualitative_subject + "Partner"].append(None)
            self.scores[qualitative_subject + "Average"].append(self_score)
            self.scores[qualitative_subject + "Diff"].append(0)
        self.scores["Qualitative Difference"].append(0)
        self_score = json_file[self.id]["Project Contribution"][0]
        self.scores["Project Contribution" + "Self"].append(self_score)
        self.scores["Project Contribution" + "Partner"].append(None)
        self.scores["Project Contribution" + "Average"].append(self_score)
        self.scores["Project Contribution" + "Diff"].append(0)

    def __give_quiz_scores(self, json_file: JsonDict) -> None:
        """
        Gives a student self and partner submission scores since they submitted with a partner
        :returns: None
        :modifies: self.scores to store the quiz scores
        """
        qualitative_differences = []
        for qualitative_subject in self.qualitative_subjects:
            self_score = json_file[self.id][qualitative_subject][0]
            if len(json_file[self.id][qualitative_subject]) == 1:
                json_file[self.id][qualitative_subject].append(
                    1
                )  # default missing partner eval score
            partner_score = json_file[self.id][qualitative_subject][1]
            average_score = round(
                statistics.fmean(json_file[self.id][qualitative_subject]), 2
            )
            qualitative_difference = self_score - partner_score
            qualitative_differences.append(qualitative_difference)
            self.scores[qualitative_subject + "Self"].append(self_score)
            self.scores[qualitative_subject + "Partner"].append(partner_score)
            self.scores[qualitative_subject + "Average"].append(average_score)
            self.scores[qualitative_subject + "Diff"].append(qualitative_difference)
        self.scores["Qualitative Difference"].append(
            round(statistics.fmean(qualitative_differences), 2)
        )
        self_score = json_file[self.id]["Project Contribution"][0]
        if len(json_file[self.id]["Project Contribution"]) == 1:
            json_file[self.id]["Project Contribution"].append(
                0
            )  # default missing partner eval score
        partner_score = json_file[self.id]["Project Contribution"][1]
        average_score = round(
            statistics.fmean(json_file[self.id]["Project Contribution"]),
            2,
        )
        contrib_diff = self_score - partner_score
        self.scores["Project Contribution" + "Self"].append(self_score)
        self.scores["Project Contribution" + "Partner"].append(partner_score)
        self.scores["Project Contribution" + "Average"].append(average_score)
        self.scores["Project Contribution" + "Diff"].append(contrib_diff)

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

    def __get_qualitative_averages(self) -> None:
        """
        calculates the overall averages for each qualitative subject and the overall average of the qualitative category
        :returns: None
        :modifies: self.averages: the averages for each qualitative subject + [self, partner, average, or diff]
                   self.average_qualitative: the overall qualitative category average
                   self.average_qualitative_difference: the overall qualitative diff average
        """
        qualitative_averages = []

        for qualitative_subject in self.qualitative_subjects:
            self.averages[qualitative_subject + "Self"] = round(
                statistics.fmean(self.scores[qualitative_subject + "Self"]), 2
            )
            cleaned_partner = [
                ele
                for ele in self.scores[qualitative_subject + "Partner"]
                if ele is not None
            ]
            self.averages[qualitative_subject + "Partner"] = (
                round(statistics.fmean(cleaned_partner), 2) if cleaned_partner else None
            )
            self.averages[qualitative_subject + "Average"] = round(
                statistics.fmean(self.scores[qualitative_subject + "Average"]), 2
            )
            self.averages[qualitative_subject + "Diff"] = round(
                statistics.fmean(self.scores[qualitative_subject + "Diff"]), 2
            )
            qualitative_averages.append(self.averages[qualitative_subject + "Average"])
        self.average_qualitative = round(statistics.fmean(qualitative_averages), 2)

        self.average_qualitative_difference = round(
            statistics.fmean(self.scores["Qualitative Difference"]), 2
        )

    def __get_project_contribution_averages(self) -> None:
        """
        calculates the overall project contribution average
        :returns: None
        :modifies: self.average_project_contribution: the overall contrib cateogry average
                   self.average_project_contribution_difference: the overall contrib diff average
        """
        self.averages["Project Contribution" + "Self"] = round(
            statistics.fmean(self.scores["Project Contribution" + "Self"]), 2
        )
        cleaned_partner = [
            ele
            for ele in self.scores["Project Contribution" + "Partner"]
            if ele is not None
        ]
        self.averages["Project Contribution" + "Partner"] = (
            round(statistics.fmean(cleaned_partner), 2) if cleaned_partner else None
        )
        self.averages["Project Contribution" + "Average"] = round(
            statistics.fmean(self.scores["Project Contribution" + "Average"]), 2
        )
        self.averages["Project Contribution" + "Diff"] = round(
            statistics.fmean(self.scores["Project Contribution" + "Diff"]), 2
        )
        self.average_project_contribution = self.averages[
            "Project Contribution" + "Average"
        ]
        self.average_project_contribution_difference = self.averages[
            "Project Contribution" + "Diff"
        ]


def stringify_subjects(subjects: list[str]) -> str:
    """
    concatinates a list of subjects into a readable string where
    each line is roughly at most 45 characters
    :returns: one string of all subjects nicely formatted with newlines
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
