import canvasapi
from collections import defaultdict
import random
import re
import statistics


class PartnerEvalQuizGrader:
    def __init__(
        self,
        course: canvasapi.course.Course,
        assignment_group: canvasapi.assignment.AssignmentGroup = 0,
    ):
        # TODO: make sure that get_assignment_groups is called with include=['assignment']
        self.course = course

        self.assignment_group = (
            assignment_group
            if assignment_group
            else self.__find_partner_eval_ag(course)
        )
        if not hasattr(self.assignment_group, "assignments"):
            print(
                "ERROR: The assignment group was not called with the include assignments flag."
            )
            exit(1)

        self.students = self.__get_students()

    def __find_partner_eval_ag(
        self, course: canvasapi.course.Course
    ) -> canvasapi.assignment.AssignmentGroup:
        partner_eval_ag = None

        for ag in course.get_assignment_groups():
            # FIXME: this is too strict
            #        we should be able to match similar assignment groups
            #        or, allow user to create their own ag
            if ag.name == "Partner Evalulations":
                partner_eval_ag = ag

        if partner_eval_ag is None:
            print('"Partner Evaluations" category does not exist!')
            print("Cannot grade, so ending program now")
            exit()

        return course.get_assignment_group(partner_eval_ag.id, include=["assignments"])

    def __get_quiz_grades(self):
        self.quiz_grades = []
        for assignment_info in self.assignment_group.assignments:
            self.quiz_grades.append(self.__get_quiz_grade(assignment_info))

    def __get_quiz_grade(self, assignment_info: dict):
        quiz_grade = defaultdict(lambda: defaultdict(list))
        assignment_id = assignment_info["id"]
        # we assume all assignments in assignment group are valid quizzes
        assignment = self.course.get_assignment(assignment_id)
        quiz = self.course.get_quiz(assignment.quiz_id)
        stats = list(quiz.get_statistics())[0]  # what is happening here
        # partner_id question is question 8
        partner_id_map = self.__get_partner_id_map(
            stats.question_statistics[8]["answers"]
        )
        qual_mappings = {
            "Strongly disagree": 1,
            "Disagree": 2,
            "Agree": 3,
            "Strongly agree": 4,
        }
        # self evals
        for question_stats in stats.question_statistics[10:16]:
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
        # partner evals
        for question_stats in stats.question_statistics[10:16]:
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
        # contribution
        contrib_mappings = {
            "0% vs 100% ==> Your partner did (almost) everything while you didn't do (almost) anything": 0,
            "25% vs 75% ==> Your partner contributed substantially more than you ": 0.25,
            "50% / 50% ==> You and your partner contributed (almost) equally": 0.5,
            "75% vs 25% ==> You contributed substantially more than your partner": 0.75,
            "100% vs 0% ==> You did (almost) everything while your partner didn't do (almost) anything": 1,
        }
        reg_str = "<h3>(.*?)</h3>"
        subject = re.match(
            reg_str, stats.question_statistics[17]["question_text"]
        ).group(1)
        for answer in stats.question_statistics[17]["answers"]:
            try:
                for user_id in answer["user_ids"]:
                    quiz_grade[user_id][subject].append(
                        contrib_mappings[answer["text"]]
                    )
                    quiz_grade[partner_id_map[user_id]][subject].append(
                        1 - contrib_mappings[answer["text"]]
                    )
            except KeyError:  # skip responses that have no students
                continue
        return quiz_grade

    def __get_partner_id_map(self, answers: dict):
        partner_dict = defaultdict(str)
        rematching_list = []
        for answer in answers:
            # get the partner id (value)
            try:
                if answer["text"] == "I did not submit with a partner.":
                    partner_id = "None"
                else:
                    partner_id = self.students[answer["text"]]
                # check if multiple students picked the same partner
                if len(answer["user_ids"]) > 1:
                    # TODO: match the mixmatches
                    print("too many students picked this person!")
                    print("we need to match")

                    for user_id in answer["user_id"]:
                        rematching_list.append(user_id)

                    # we assume that at least one person of the pair picked correctly
                elif len(answer["user_ids"]) == 1:
                    partner_dict[answer["user_ids"][0]] = partner_id
            except KeyError:  # skip responses that don't correspond to students
                continue

        # rematch missing students
        for student_user_id in rematching_list:
            partner_id = str(
                [key for key, value in partner_dict.items() if value == student_user_id]
            )
            partner_dict[student_user_id] = partner_id

        return partner_dict

    # make dict where keys are student names and value is student canvas user ids
    # FIXME: messy and hacky way to handle dupes
    def __get_students(self) -> dict:
        raw_students = defaultdict(list)
        dup_list = set()
        for raw_student in self.course.get_users(
            sort="username", enrollment_type=["student"]
        ):
            if (
                raw_student.sis_user_id is None
            ):  # FIXME: delete for real class; not all sandbox student have SID
                raw_student.sis_user_id = random.randint(0, 100)

            if raw_student.sortable_name in dup_list:
                SID = str(raw_student.sis_user_id)
                raw_students[
                    raw_student.sortable_name + " (XXXXX" + SID[-4:] + ")"
                ].extend([raw_student.sis_user_id, raw_student.id])
            elif raw_student.sortable_name in raw_students.keys():
                dup_list.add(raw_student.sortable_name)
                SID = str(raw_student.sis_user_id)

                orignal_SID = str(raw_students[raw_student.sortable_name])
                raw_students[
                    raw_student.sortable_name + " (XXXXX" + SID[-4:] + ")"
                ].extend([raw_student.sis_user_id, raw_student.id])
                raw_students.pop(raw_student.sortable_name)

                dup_SID = str(raw_student.sis_user_id)
                raw_students[
                    raw_student.sortable_name + " (XXXXX" + SID[-4:] + ")"
                ].extend([raw_student.sis_user_id, raw_student.id])
            else:
                raw_students[raw_student.sortable_name].extend(
                    [raw_student.sis_user_id, raw_student.id]
                )

        clean_students = {student: raw_students[student][1] for student in raw_students}
        return clean_students

    def upload_grades_to_canvas(self):
        # TODO: actually uplaod to canvas
        self.__get_quiz_grades()
        self.__make_individual_stats()
        grades = self.__make_final_grades()
        for k, v in grades.items():
            print(f"ID {k} will receive {round(v,2 )} as their final score")

    def __make_individual_stats(self):
        # iterate through each student in the current roster
        self.student_indivdual_stats = [
            PartnerEvalQuizIndividualStats(id, self.quiz_grades)
            for id in self.students.values()
        ]

    def __make_final_grades(self) -> dict:
        grades = defaultdict(float)
        grades = {
            student.id: student.get_final_grade()
            for student in self.student_indivdual_stats
        }
        return grades


class PartnerEvalQuizIndividualStats:
    def __init__(self, id: int, quiz_grades: list):
        self.id = id
        org_avgs = []
        com_avgs = []
        coop_avgs = []
        atti_avgs = []
        idea_avgs = []
        code_avgs = []
        contrib_avgs = []
        deviation_1_avgs = []
        deviation_2_avgs = []

        for quiz_grade in quiz_grades:
            if id not in quiz_grade.keys():
                # student did not submit this assignment give them defaults
                org_avgs.append(0)
                com_avgs.append(0)
                coop_avgs.append(0)
                atti_avgs.append(0)
                idea_avgs.append(0)
                code_avgs.append(0)
                contrib_avgs.append(0)
                deviation_1_avgs.append(0)
                deviation_2_avgs.append(0)
                continue
            org_avgs.append(statistics.fmean(quiz_grade[id]["Organization/planning"]))
            com_avgs.append(statistics.fmean(quiz_grade[id]["Communication"]))
            coop_avgs.append(statistics.fmean(quiz_grade[id]["Teamwork/cooperation"]))
            atti_avgs.append(statistics.fmean(quiz_grade[id]["Attitude"]))
            idea_avgs.append(statistics.fmean(quiz_grade[id]["Contribution of ideas"]))
            code_avgs.append(statistics.fmean(quiz_grade[id]["Contribution of code"]))
            contrib_avgs.append(
                statistics.fmean(quiz_grade[id]["Project contribution"])
            )
            deviation_1_avgs.append(
                statistics.fmean(
                    quiz_grade[id][quality][0] - quiz_grade[id][quality][1]
                    for quality in quiz_grade[id].keys()
                    if quality != "Project contribution"
                )
            )
            deviation_2_avgs.append(
                quiz_grade[id]["Project contribution"][0]
                - quiz_grade[id]["Project contribution"][1]
            )

        project_engagement_avgs = []
        for quality in org_avgs, com_avgs, coop_avgs, atti_avgs, idea_avgs, code_avgs:
            project_engagement_avgs.append(statistics.fmean(quality))
        self.project_engagement_avg = statistics.fmean(project_engagement_avgs)
        self.project_engagement_deviation = statistics.fmean(deviation_1_avgs)
        self.project_contrib_avg = statistics.fmean(contrib_avgs)
        self.project_contrib_deviation = statistics.fmean(deviation_2_avgs)

    def get_final_grade(self):
        if self.project_engagement_deviation > 0:
            project_engagement_score = (
                (self.project_engagement_avg - self.project_contrib_deviation) / 4 * 100
            )
        else:
            project_engagement_score = (
                (self.project_engagement_avg + (self.project_engagement_deviation / 2))
                / 4
                * 100
            )
        if self.project_contrib_deviation > 0:
            project_contrib_score = (
                (self.project_contrib_avg - self.project_contrib_deviation)
                / 50
                * 100
                * 100
            )
        else:
            project_contrib_score = (
                (self.project_contrib_avg + (self.project_contrib_deviation / 2))
                / 50
                * 100
                * 100
            )
        final_score = 0.4 * project_engagement_score + 0.6 * project_contrib_score
        return final_score


if __name__ == "__main__":
    url = "https://canvas.ucdavis.edu"
    key = str(input("Enter API key:"))

    canvas = canvasapi.Canvas(url, key)
    course = canvas.get_course(1599)  # sandbox course ID
    grader = PartnerEvalQuizGrader(course)
    grader.upload_grades_to_canvas()
