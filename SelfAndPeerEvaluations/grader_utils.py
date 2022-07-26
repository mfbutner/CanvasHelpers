import canvasapi
from collections import defaultdict
import random
import re
import statistics


class PartnerEvalQuizIndividualStats:
    def __init__(self, id: int, quiz_grades: list):
        self.id = id
        self.scores = defaultdict(list)

        for quiz_grade in quiz_grades:
            self.__parse_quiz_grade(quiz_grade)

        self.scores["engagement_score"].append(self.__get_engagement_score())
        self.scores["contribution_score"].append(self.__get_contribution_score())

    def get_final_grade(self):
        final_score = (
            0.4 * self.scores["engagement_score"][0]
            + 0.6 * self.scores["contribution_score"][0]
        )
        print(self.scores)
        return final_score

    def __parse_quiz_grade(self, quiz_grade: dict) -> None:
        self.scores["organization_avgs"].append(
            statistics.fmean(quiz_grade[self.id]["Organization/planning"])
        )
        self.scores["communication_avgs"].append(
            statistics.fmean(quiz_grade[self.id]["Communication"])
        )
        self.scores["teamwork_avgs"].append(
            statistics.fmean(quiz_grade[self.id]["Teamwork/cooperation"])
        )
        self.scores["attitude_avgs"].append(
            statistics.fmean(quiz_grade[self.id]["Attitude"])
        )
        self.scores["ideas_avgs"].append(
            statistics.fmean(quiz_grade[self.id]["Contribution of ideas"])
        )
        self.scores["code_avgs"].append(
            statistics.fmean(quiz_grade[self.id]["Contribution of code"])
        )
        self.scores["contribution_avgs"].append(
            statistics.fmean(quiz_grade[self.id]["Project contribution"])
        )
        deviation_1_vals = self.__get_deviation_1_vals(quiz_grade)
        self.scores["deviation_1_scores"].append(statistics.fmean(deviation_1_vals))
        self.scores["deviation_2_scores"].append(self.__get_deviation_2_val(quiz_grade))

    def __get_deviation_1_vals(self, quiz_grade: dict) -> list:
        deviation_1_vals = []
        if self.id not in quiz_grade["info"]["submissions"]:
            deviation_1_vals.append(0)
            return deviation_1_vals

        for quality in quiz_grade[self.id].keys():
            if quality == "Project contribution":
                continue

            if len(quiz_grade[self.id][quality]) == 1:
                deviation_1_vals.append(0)
            else:
                deviation_1_vals.append(
                    quiz_grade[self.id][quality][0] - quiz_grade[self.id][quality][1]
                )
        return deviation_1_vals

    def __get_deviation_2_val(self, quiz_grade: dict) -> float:
        if (
            self.id in quiz_grade["info"]["submissions"]
            and len(quiz_grade[self.id]["Project contribution"]) > 1
        ):
            return (
                quiz_grade[self.id]["Project contribution"][0]
                - quiz_grade[self.id]["Project contribution"][1]
            )
        else:
            return 0

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


def make_partner_id_map(student_id_map: dict, answers: dict) -> dict:
    # returns a dict where keys are student canvas ID and value is partner's canvas ID
    partner_id_map = defaultdict(str)
    rematching_list = list(student_id_map.values())
    for answer in answers:
        try:
            # get the partner_id
            if answer["text"] == "I did not submit with a partner.":
                partner_id = "None"
            else:
                partner_id = student_id_map[answer["text"]]

            if len(answer["user_ids"]) == 1:
                partner_id_map[answer["user_ids"][0]] = partner_id
                rematching_list.remove(answer["user_ids"][0])
        except KeyError:  # skip responses that don't correspond to students
            continue

    # rematch missing students
    for student_user_id in rematching_list:
        # use the student id as the value and find the partner id from the keys
        # this assumes that the partner correctly identified the student so exactly one partner to one student
        # if there is no partner who identified the student, then the student's partner_id is None
        partner_id = [
            key for key, value in partner_id_map.items() if value == student_user_id
        ]
        partner_id_map[student_user_id] = partner_id[0] if len(partner_id) else "None"
    return partner_id_map


def parse_self_evals(quiz_grade: dict, questions: list, student_id_map: dict) -> None:
    # maps students self evaluations to themselves
    qual_mappings = {
        "No Answer": 1,
        "Strongly disagree": 1,
        "Disagree": 2,
        "Agree": 3,
        "Strongly agree": 4,
    }
    for question_stats in questions:
        for answer in question_stats["answers"]:
            reg_str = "<h3>(.*?)</h3>"
            subject = re.match(reg_str, question_stats["question_text"]).group(1)
            try:
                for user_id in answer["user_ids"]:
                    quiz_grade[user_id][subject].append(qual_mappings[answer["text"]])
            except KeyError:  # skip responses that have no students
                continue
    # give default self eval scores for students who did not submit
    for student_id in student_id_map.values():
        if student_id not in quiz_grade.keys():
            quiz_grade[student_id]["Organization/planning"].append(1)
            quiz_grade[student_id]["Communication"].append(1)
            quiz_grade[student_id]["Teamwork/cooperation"].append(1)
            quiz_grade[student_id]["Attitude"].append(1)
            quiz_grade[student_id]["Contribution of ideas"].append(1)
            quiz_grade[student_id]["Contribution of code"].append(1)


def parse_partner_evals(
    quiz_grade: dict, questions: list, partner_id_map: dict
) -> None:
    # maps parterns's partner evaluation to their partner
    # we do not map "No Answer" to 1. instead, the partner will get duplicate scores
    qual_mappings = {
        "Strongly disagree": 1,
        "Disagree": 2,
        "Agree": 3,
        "Strongly agree": 4,
    }
    for question_stats in questions:
        for answer in question_stats["answers"]:
            reg_str = "<h3>(.*?)</h3>"
            subject = re.match(reg_str, question_stats["question_text"]).group(1)
            try:
                for user_id in answer["user_ids"]:
                    quiz_grade[partner_id_map[user_id]][subject].append(
                        qual_mappings[answer["text"]]
                    )
            except KeyError:  # skip responses that have no students
                continue


def parse_contribution_evals(
    quiz_grade: dict, question: dict, partner_id_map: dict, student_id_map: dict
) -> None:
    # maps students contribution evalution to themselves and their partner
    contrib_mappings = {
        "No Answer": 0,
        "0% vs 100% ==> Your partner did (almost) everything while you didn't do (almost) anything": 0,
        "25% vs 75% ==> Your partner contributed substantially more than you": 0.25,
        "50% / 50% ==> You and your partner contributed (almost) equally": 0.5,
        "75% vs 25% ==> You contributed substantially more than your partner": 0.75,
        "100% vs 0% ==> You did (almost) everything while your partner didn't do (almost) anything": 1,
    }
    missing_submissions = list(student_id_map.values())
    reg_str = "<h3>(.*?)</h3>"
    subject = re.match(reg_str, question["question_text"]).group(1)
    # we have to do it self first then partner loop
    # self loop
    for answer in question["answers"]:
        try:
            for user_id in answer["user_ids"]:
                missing_submissions.remove(user_id)
                quiz_grade[user_id][subject].append(contrib_mappings[answer["text"]])
        except KeyError:  # skip responses that have no students
            continue
    # give missing_submissions student a 0 in contribution
    for student_id in missing_submissions:
        quiz_grade[student_id][subject].append(0)
    # partner loop
    for answer in question["answers"]:
        try:
            for user_id in answer["user_ids"]:
                quiz_grade[partner_id_map[user_id]][subject].append(
                    1 - contrib_mappings[answer["text"]]
                )
        except KeyError:  # skip responses that have no students
            continue
