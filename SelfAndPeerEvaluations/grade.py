from os import wait
import canvasapi
from collections import defaultdict
import random
import re
import statistics


if __name__ == "__main__":
    url = "https://canvas.ucdavis.edu"
    key = str(input("Enter API key:"))

    canvas = canvasapi.Canvas(url, key)
    course = canvas.get_course(1599)  # sandbox course ID

    # make dict where keys are student names and value is student canvas user ids
    # FIXME: messy and hacky way to handle dupes
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
            SID = str(raw_student.sis_user_id)

            orignal_SID = str(raw_students[raw_student.sortable_name])
            raw_students[raw_student.sortable_name + " (XXXXX" + SID[-4:] + ")"].extend(
                [raw_student.sis_user_id, raw_student.id]
            )
            raw_students.pop(raw_student.sortable_name)

            dup_SID = str(raw_student.sis_user_id)
            raw_students[raw_student.sortable_name + " (XXXXX" + SID[-4:] + ")"].extend(
                [raw_student.sis_user_id, raw_student.id]
            )
        else:
            raw_students[raw_student.sortable_name].extend(
                [raw_student.sis_user_id, raw_student.id]
            )

    clean_students = {student: raw_students[student][1] for student in raw_students}

    # get assignment group
    partner_eval_ag = None
    for ag in course.get_assignment_groups():
        if ag.name == "Partner Evalulations":
            partner_eval_ag = ag
    ag = partner_eval_ag
    ag = course.get_assignment_group(ag.id, include=["assignments"])

    assignments = []

    # iterate through all the assignment in an assignment group
    for ass_dict in ag.assignments:
        # get the single assignment
        ass_id = ass_dict["id"]
        ass = course.get_assignment(
            ass_id
        )  # we assume all assignments in assignment group are valid quizzes
        quiz = course.get_quiz(ass.quiz_id)
        print("==== Working on " + str(quiz.id) + " ====")

        # get the list of students user_id's who submitted
        user_ids = []
        for student in quiz.get_submissions():
            user_ids.append(student.user_id)

        stats = list(quiz.get_statistics())[0]  # what is happening here

        # make partner dict; key: student, value: their partner
        # FIXME: maybe this can just be a list of sets? saves on space????
        partner_dict = defaultdict(str)
        rematching_list = []
        # print(stats.question_statistics[8])  # HACK: partner identify q is at index 8
        for answer in stats.question_statistics[8]["answers"]:
            # get the partner id (value)
            try:
                if answer["text"] == "I did not submit with a partner.":
                    partner_id = "None"
                else:
                    partner_id = clean_students[answer["text"]]
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
        """
        print("Here are the partner mappings I found")
        for k, v in partner_dict.items():
            print("Key: " + str(k) + ", Value: " + str(v))
        """

        # iterate through the questions
        assignment = defaultdict(lambda: defaultdict(list))
        # key: user_id
        # value: dict where key: question prompt: value: list of scores (from partner and self)
        qual_mappings = {
            "Strongly disagree": 1,
            "Disagree": 2,
            "Agree": 3,
            "Strongly agree": 4,
        }
        # self evals
        for question_stats in stats.question_statistics[1:7]:
            reg_str = "<h3>(.*?)</h3>"
            subject = re.match(reg_str, question_stats["question_text"]).group(1)
            for answer in question_stats["answers"]:
                try:
                    for user_id in answer["user_ids"]:
                        assignment[user_id][subject].append(
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
                        assignment[partner_dict[user_id]][subject].append(
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
                    assignment[user_id][subject].append(
                        contrib_mappings[answer["text"]]
                    )
                    assignment[partner_dict[user_id]][subject].append(
                        1 - contrib_mappings[answer["text"]]
                    )
            except KeyError:  # skip responses that have no students
                continue

        assignments.append(assignment)
    print("finally we're done going through all the assignments")
    print("we will proceed to collect averages for each assignmnet")

    # iterate through each student in the current roster
    student_assignment_stats = defaultdict(lambda: defaultdict(float))
    subject_set = set()
    for student_user_id in clean_students.values():
        for assignment in assignments:
            if student_user_id not in assignment.keys():
                # TODO: give students 0s / the defaults all around
                continue
            project_engagement_deviations = []
            for subject in assignment[student_user_id]:
                subject_set.add(subject)
                student_assignment_stats[student_user_id][subject] = statistics.fmean(
                    assignment[student_user_id][subject]
                )
                if subject != "Project contribution":
                    project_engagement_deviations.append(
                        assignment[student_user_id][subject][0]
                        - assignment[student_user_id][subject][1]
                    )
                else:
                    student_assignment_stats[student_user_id]["deviation #2"] = (
                        assignment[student_user_id][subject][0]
                        - assignment[student_user_id][subject][1]
                    )
            student_assignment_stats[student_user_id][
                "deviation #1"
            ] = statistics.fmean(project_engagement_deviations)

    # step 3 (actually get overall grades)
    student_assignment_grades = defaultdict(float)
    for student_user_id in clean_students.values():
        project_engagement_averages = []
        for subject in subject_set:
            subject_avgs = []
            print(subject)

    """
    student_user_ids = clean_students.values()
    for student_user_id in student_user_ids:
        print("working on", student_user_id)
        engagement_averages = []
        engagement_deviations = []
        contribution_average = []
        contribution_deviations = []
        # get engagement averages
        for assignment in assignments:
            if student_user_id not in assignment.keys():
                print(f"   user {student_user_id} did not submit this assignment")
                continue
            print(assignment[student_user_id])
            # print(assignment.keys())
            # print(assignment.values())
            print(assignment[student_user_id].values())

    for assignment in assignments:
        for key, value in assignment.items():
            print("here are the results for", key)
            for subject in value:
                print("    scores for " + subject + ": ", value[subject])
    """
