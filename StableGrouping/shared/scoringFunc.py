from StableGrouping.shared.studentClass import Student
from StableGrouping.matching.checkValidGroup import is_valid_group
from StableGrouping.matching.matchingFunc import match_international, match_language, match_time, match_activity, \
    match_gender, match_partner


# Reward a group with at least one person of each confidence level, or minor reward with two confidence levels
def score_at_least_one_confidence_level(student_list: list):
    low_confidence_flag = False
    med_confidence_flag = False
    high_confidence_flag = False
    for student in student_list:
        if student.confidence == 0:
            low_confidence_flag = True
        elif student.confidence == 1:
            med_confidence_flag = True
        elif student.confidence == 2:
            high_confidence_flag = True
    if low_confidence_flag and med_confidence_flag and high_confidence_flag:
        return 150
    elif low_confidence_flag and med_confidence_flag or med_confidence_flag and high_confidence_flag or low_confidence_flag and high_confidence_flag:
        return 100

    return 0


# Score student2 by student1's metric, return the score
def score_one_by_one(student1: Student, student2: Student, match_dict: dict):
    # Assign weights to the priority list
    score_weights = [50, 30, 15, 5, 0]
    score = 0

    if match_partner(student1, student2) > 0 and match_partner(student2, student1) > 0:
        score += 40000

    for i in range(4):
        # If the priority list hits default, score no further
        if not student1.priority_list[i]:
            break
        # If the student priority is matched, add its weight to the score
        elif student1.priority_list[i] == "International":
            if match_international(student1, student2):
                score += score_weights[i]
        elif student1.priority_list[i] == "Language":
            if match_language(student1, student2):
                score += score_weights[i]
        elif student1.priority_list[i] == "Matching Time to Meet":
            if match_time(student1, student2):
                score += score_weights[i]
        elif student1.priority_list[i] == "What They Want to Do":
            if match_activity(student1, student2):
                score += score_weights[i]
        elif student1.priority_list[i] == "Gender":
            if match_gender(student1, student2):
                score += score_weights[i]
        else:
            print("Error: This index of the priority list does not meet any acceptable criteria", student1.name, i)

    # If the two students have matched before, punish it harshly in score
    # The punishment needs to be high enough to make groups with only one match still poor
    temp_list = [student1, student2]
    score = score - 2000 * is_valid_group(match_dict, temp_list)

    return score


# Score student_pair2 by student_pair1's metric, return the score
def score_two_by_two(student_pair1: list, student_pair2: list, match_before):
    # Default to a score of 0
    score = 0

    # If anybody has asked for anybody else, score high
    for student1 in student_pair1:
        for student2 in student_pair2:
            if match_partner(student1, student2) or match_partner(student2, student1):
                score += 40000

    # Measure each student in the second pair by the first two's preferences
    for student1 in student_pair1:
        for student2 in student_pair2:
            score += score_one_by_one(student1, student2, match_before)

    # Put them all in a list in order to make the rest of the code smoother
    student_list = [student_pair1[0], student_pair1[1], student_pair2[0], student_pair2[1]]

    # Reward extra a group where 4 people speak the same language
    # Assume that they do until you prove they don't
    language = True
    for i in range(3):
        if student_list[i].language != student_list[(i + 1)].language:
            language = False

    # If the language flag is still true, reward the group
    if language:
        score += 800

    # Reward a group with at least one leader
    flag_leader = False
    for i in range(3):
        if student_list[i].prefer_leader:
            flag_leader = True
            break

    if flag_leader:
        score += 50

    # Reward a group with a mix of people from multiple confidence levels
    score += score_at_least_one_confidence_level(student_list)

    # Return the total calculated score
    return score


# Score a group of people by the preferences of one person, preferably for four people or more
def score_group_by_one(student: Student, group: list, matched_before: dict):
    score = 0

    # If anyone likes anyone else, score high
    for student1 in group:
        if match_partner(student1, student) or match_partner(student, student1):
            score += 40000

    # check the individual score by each student
    for student2 in group:
        score += score_one_by_one(student, student2, matched_before)

    # Reward extra a group that all speaks that same langauge
    group_same_language = True
    for i in range(len(group) - 1):
        if group[i].language != group[(i + 1)].language:
            group_same_language = False

    if group_same_language and student.language == group[0].language:
        score += 800

    # Punish harshly if the student is alone without another speaker of their language
    match_student_language = False
    for student2 in group:
        if student.language == student2.language:
            match_student_language = True
            break
    if not match_student_language:
        score = score - 800

    # Reward a group with at least one person of each confidence level
    temp_list = []
    for student2 in group:
        temp_list.append(student2)

    temp_list.append(student)
    score += score_at_least_one_confidence_level(temp_list)

    return score


# Score a person by the group preferences of multiple people, preferably for four or more
def score_one_by_group(student: Student, group: list, matched_before: dict):
    score = 0

    for student1 in group:
        if match_partner(student1, student) > 0 or match_partner(student, student1) > 0:
            score += 40000

    for student1 in group:
        score += score_one_by_one(student1, student, matched_before)

    # Reward extra a group that all speaks that same langauge
    group_same_language = True
    for i in range(len(group) - 1):
        if group[i].language != group[(i + 1)].language:
            group_same_language = False

    if group_same_language and student.language == group[0].language:
        score += 800

    # Punish harshly if the student is alone without another speaker of their language
    match_student_language = False
    for student2 in group:
        if student.language == student2.language:
            match_student_language = True
            break

    if not match_student_language:
        score = score - 800

    # Reward a group with at least one person of each confidence level
    temp_list = []
    for student2 in group:
        temp_list.append(student2)

    temp_list.append(student)
    score += score_at_least_one_confidence_level(temp_list)

    return score
