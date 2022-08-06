from StableGrouping.shared.studentClass import Student
from StableGrouping.matching.matchingFunc import match_international
from StableGrouping.matching.matchingFunc import match_language
from StableGrouping.matching.matchingFunc import match_time
from StableGrouping.matching.matchingFunc import match_activity
from StableGrouping.matching.matchingFunc import match_gender
from StableGrouping.matching.matchingFunc import match_partner
from StableGrouping.matching.checkValidGroup import is_valid_group


# Reward a group with at least one person of each confidence level, or minorly reward with two confidence levels
def scoreAtLeastOneConfidenceLevel(studentList: list):
    lowConfidenceFlag = False
    medConfidenceFlag = False
    highConfidenceFlag = False
    for student in studentList:
        if student.confidence == 0:
            lowConfidenceFlag = True
        elif student.confidence == 1:
            medConfidenceFlag = True
        elif student.confidence == 2:
            highConfidenceFlag = True
    if lowConfidenceFlag and medConfidenceFlag and highConfidenceFlag:
        return 150
    elif lowConfidenceFlag and medConfidenceFlag or medConfidenceFlag and highConfidenceFlag or lowConfidenceFlag and highConfidenceFlag:
        return 100

    return 0


# Score student2 by student1's metric, return the score
def scoreOneByOne(student1: Student, student2: Student, matchDict: dict):
    # Assign weights to the priorty list
    scoreWeights = [50, 30, 15, 5, 0]
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
                score = score + scoreWeights[i]
        elif student1.priority_list[i] == "Language":
            if match_language(student1, student2):
                score = score + scoreWeights[i]
        elif student1.priority_list[i] == "Matching Time to Meet":
            if match_time(student1, student2):
                score = score + scoreWeights[i]
        elif student1.priority_list[i] == "What They Want to Do":
            if match_activity(student1, student2):
                score = score + scoreWeights[i]
        elif student1.priority_list[i] == "Gender":
            if match_gender(student1, student2):
                score = score + scoreWeights[i]
        else:
            print("Error: This index of the priority list does not meet any acceptable criteria", student1.name, i)

    # If the two students have matched before, punish it harshly in score
    # The punishment needs to be high enough to make groups with only one match still poor
    tempList = [student1, student2]
    score = score - 2000 * is_valid_group(matchDict, tempList)

    return score


# Score studentPair2 by studentPair1's metric, return the score
def scoreTwoByTwo(studentPair1: list, studentPair2: list, matchBefore):
    # Default to a score of 0
    score = 0

    # If anybody has asked for anybody else, score high
    for student1 in studentPair1:
        for student2 in studentPair2:
            if match_partner(student1, student2) or match_partner(student2, student1):
                score += 40000

    # Measure each student in the second pair by the first two's preferences
    for student1 in studentPair1:
        for student2 in studentPair2:
            score = score + scoreOneByOne(student1, student2, matchBefore)

    # Put them all in a list in order to make the rest of the code smoother
    studentList = [studentPair1[0], studentPair1[1], studentPair2[0], studentPair2[1]]

    # Reward extra a group where 4 people speak the same language
    # Assume that they do until you prove they don't
    language = True
    for i in range(3):
        if studentList[i].language != studentList[(i + 1)].language:
            language = False

    # If the language flag is still true, reward the group
    if language:
        score = score + 800

    # Reward a group with at least one leader
    flagLeader = False
    for i in range(3):
        if studentList[i].prefer_leader:
            flagLeader = True
            break

    if flagLeader:
        score = score + 50

    # Reward a group with a mix of people from multiple confidence levels
    score = score + scoreAtLeastOneConfidenceLevel(studentList)

    # Return the total calculated score
    return score


# Score a group of people by the preferences of one person, preferably for four people or more
def scoreGroupByOne(student: Student, group: list, matchedBefore: dict):
    score = 0

    # If anyone likes anyone else, score high
    for student1 in group:
        if match_partner(student1, student) or match_partner(student, student1):
            score += 40000

    # check the individual score by each student
    for student2 in group:
        score = score + scoreOneByOne(student, student2, matchedBefore)

    # Reward extra a group that all speaks that same langauge
    groupSameLanguage = True
    for i in range(len(group) - 1):
        if group[i].language != group[(i + 1)].language:
            groupSameLanguage = False

    if groupSameLanguage and student.language == group[0].language:
        score = score + 800

    # Punish harshly if the student is alone without another speaker of their language
    matchStudentLanguage = False
    for student2 in group:
        if student.language == student2.language:
            matchStudentLanguage = True
            break
    if not matchStudentLanguage:
        score = score - 800

    # Reward a group with at least one person of each confidence level
    tempList = []
    for student2 in group:
        tempList.append(student2)

    tempList.append(student)
    score = score + scoreAtLeastOneConfidenceLevel(tempList)

    return score


# Score a person by the group preferences of multiple people, preferably for four or more
def scoreOneByGroup(student: Student, group: list, matchedBefore: dict):
    score = 0

    for student1 in group:
        if match_partner(student1, student) > 0 or match_partner(student, student1) > 0:
            score += 40000

    for student1 in group:
        score = score + scoreOneByOne(student1, student, matchedBefore)

    # Reward extra a group that all speaks that same langauge
    groupSameLanguage = True
    for i in range(len(group) - 1):
        if group[i].language != group[(i + 1)].language:
            groupSameLanguage = False

    if groupSameLanguage and student.language == group[0].language:
        score = score + 800

    # Punish harshly if the student is alone without another speaker of their language
    matchStudentLanguage = False
    for student2 in group:
        if student.language == student2.language:
            matchStudentLanguage = True
            break

    if not matchStudentLanguage:
        score = score - 800

    # Reward a group with at least one person of each confidence level
    tempList = []
    for student2 in group:
        tempList.append(student2)

    tempList.append(student)
    score = score + scoreAtLeastOneConfidenceLevel(tempList)

    return score
