import re
from enum import Enum
from studentClass import Student
import pandas as pd
import json


class PreferGender(Enum):
    same_pronouns = 2
    diff_pronouns = 0
    dont_care_pronouns = 1


class PreferAsync(Enum):
    like_sync = 1
    like_async = 2
    dont_care_async = 0


class PreferInternat(Enum):
    not_internat = 0
    prefer_internat_partner = 2
    dont_care_internat = 1


class confident(Enum):
    is_confident = 2
    not_confident = 0
    default_confidence = 1


def parse_students(canvas_students):
    # TODO: The equivalent of this in the old code ignored students without emails. Check if this is needed
    all_students = {}
    for student in canvas_students:
        student_instance = Student()
        student_instance.idNum = student.id
        student_instance.name = student.name
        name = student.sortable_name.split(",")
        if len(name) == 1:
            student_instance.firstName = name[0]
        elif len(name) != 0:
            student_instance.firstName = name[1]
            student_instance.lastName = name[0]
        student_instance.schoolEmail = student.email
        all_students[student.id] = student_instance

    return all_students


def reindex_essay_questions(course, quiz, question_index):
    quiz_assignment = course.get_assignment(quiz.assignment_id)
    quiz_submissions = quiz_assignment.get_submissions(include="submission_history")
    quiz_filtered_submissions = [submission for submission in quiz_submissions if submission.submitted_at != None]

    for question_key, question in question_index.items():
        question_type = question["question_type"]
        if question_type != "essay_question" and question_type != "fill_in_multiple_blanks_question":
            continue

        question_id = question["id"]
        reindexed_dict = {}
        question_index[question_key] = reindexed_dict

        # TODO: Account for people submitting twice (Keep latest using submission.attempt)
        for submission in quiz_filtered_submissions:
            # TODO: Check to make sure submission_history is always a single item
            submitter_id = submission.user_id
            submission_details = submission.submission_history[0]["submission_data"]
            for answer in submission_details:
                if str(answer["question_id"]) == question_id:
                    reindexed_dict[submitter_id] = answer
                    break

    print("===== Reindexed Essay Questions ======")


def index_questions(course, quiz, config):
    statistics = list(quiz.get_statistics())[0]
    all_questions = statistics.question_statistics

    # Returns this object with None replaced with the corresponding item from all_questions
    question_index = {
        "pronouns_select": None,
        "pronouns_other": None,
        "prefer_same_gender": None,
        "prefer_synchronous": None,
        "time_free": None,
        "prefer_communication_method": None,
        "prefer_communication_info": None,
        "prefer_to_lead": None,
        "prefer_other_international": None,
        "language_select": None,
        "language_other": None,
        "activity_select": None,
        "activity_specify": None,
        "priorities": None,
        "confidence": None
    }

    patterns = config["patterns"]
    for question in all_questions:
        for index_key in question_index.keys():
            # TODO: Fix possibility that multiple questions could match
            if re.search(patterns[index_key], question["question_text"]):
                question_index[index_key] = question
                continue

        # Warning: No matches found for this question
        if question not in question_index.values():
            print("No Match for Question:")
            print(question["question_text"])

    print("===== Question Indexing Complete =====")
    print("===== See Missed Questions Above =====")

    # Change the format of free response (essay_question) questions by replacing their key: values with responses instead of useless data
    # Modifies question_index directly
    reindex_essay_questions(course, quiz, question_index)

    return question_index


def filter_students_submitted(all_students, quiz_submissions):
    students_submitted = {}
    for submission in quiz_submissions:
        for student in all_students.values():
            # Side effect: If the student is not found in all_students, the submission is ignored
            # The student either may be no longer enrolled or something has gone wrong
            if student.idNum != submission.user_id:
                continue

            students_submitted[student.idNum] = student
            break
    return students_submitted


def remove_any_tags(source_str):
    first_close = source_str.find('>')
    end_close = source_str.rfind('<')
    return source_str[first_close + 1:end_close]


def parse_submissions(students_submitted, course, quiz, config):
    question_index = index_questions(course, quiz, config)

    for answer in question_index["pronouns_select"]["answers"]:
        answer_text = answer["text"]
        for user_id in answer["user_ids"]:
            students_submitted[user_id].pronouns = answer_text

    # 0 - Not same pronouns
    # 1 - No preference (Default)
    # 2 - Prefer the same pronouns
    # Using if statements for now

    for answer in question_index["prefer_same_gender"]["answers"]:
        answer_text = answer["text"]
        for user_id in answer["user_ids"]:
            if answer_text == "I would prefer another person who as the same pronouns as I do.":
                students_submitted[user_id].preferSame = PreferGender.same_pronouns.value
            elif answer_text == "I would prefer another person who does not have the same pronouns as I do.":
                students_submitted[user_id].preferSame = PreferGender.diff_pronouns.value
            else:
                students_submitted[user_id].preferSame = PreferGender.dont_care_pronouns.value

    # 0 - No preference (Default)
    # 1 - Synchronous
    # 2 - Asynchronous
    for answer in question_index["prefer_synchronous"]["answers"]:
        answer_text = answer["text"]
        for user_id in answer["user_ids"]:
            if answer_text == "Synchronously":
                students_submitted[user_id].preferAsy = PreferAsync.like_sync.value
            elif answer_text == "Asynchronously":
                students_submitted[user_id].preferAsy = PreferAsync.like_async.value
            else:
                students_submitted[user_id].preferAsy = PreferAsync.dont_care_async.value

    for answer in question_index["prefer_to_lead"]["answers"]:
        answer_text = answer["text"]
        for user_id in answer["user_ids"]:
            students_submitted[user_id].preferLeader = (answer_text == "I like to lead.")

    # 0 - Not international (Default)
    # 1 - No preference
    # 2 - Is international and would like to match with international
    for answer in question_index["prefer_other_international"]["answers"]:
        answer_text = answer["text"]
        for user_id in answer["user_ids"]:
            if answer_text == "I am not an international student.":
                students_submitted[user_id].international = PreferInternat.not_internat.value
            elif answer_text == "I would like to be placed with another international student.":
                students_submitted[user_id].international = PreferInternat.prefer_internat_partner.value
            else:
                students_submitted[user_id].international = PreferInternat.dont_care_internat.value

    # Q7 on the Canvas quiz question
    # Default: "default"
    # Sets option1 (option2 ignored)
    for answer in question_index["activity_select"]["answers"]:
        answer_text = answer["text"]
        for user_id in answer["user_ids"]:
            students_submitted[user_id].option1 = answer_text

    # 0 - Could use some help
    # 1 - Have some questions (Default)
    # 2 - Confident
    for answer in question_index["confidence"]["answers"]:
        answer_text = answer["text"]
        for user_id in answer["user_ids"]:
            if answer_text == "I'm confident.":
                students_submitted[user_id].confidence = confident.is_confident.value
            elif answer_text == "I could really use some help.":
                students_submitted[user_id].confidence = confident.not_confident.value
            else:
                students_submitted[user_id].confidence = confident.default_confidence.value

    # time_free
    daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for answer in question_index["time_free"]["answer_sets"]:
        answer_text = answer["text"]
        day_text = answer_text[0:3]
        if day_text in daysOfWeek:
            first_index = daysOfWeek.index(day_text)
            second_index = int(answer_text[3]) - 1
            for response in answer["answers"]:
                available = response["correct"]
                if not available:
                    continue

                for user_id in response["user_ids"]:
                    students_submitted[user_id].meetingTimes[first_index][second_index] = available

    # priorities
    priority_list = ["top", "second", "third", "fourth", "fifth"]
    for answer in question_index["priorities"]["answer_sets"]:
        answer_text = answer["text"]
        if answer_text in priority_list:
            index = priority_list.index(answer["text"])
            for tmp in answer["answers"]:
                for user_id in tmp["user_ids"]:
                    students_submitted[user_id].priorityList[index] = tmp["text"]

    # language_select
    for answer in question_index["language_select"]["answer_sets"][0]["answers"]:
        answer_text = answer["text"]
        for user_id in answer["user_ids"]:
            students_submitted[user_id].language = answer_text

    # pronouns_other
    for user_id, answer in question_index["pronouns_other"].items():
        if students_submitted[user_id].pronouns == "Not Included":
            students_submitted[user_id].pronouns = remove_any_tags(answer["text"])

    # language_other
    for user_id, answer in question_index["language_other"].items():
        if students_submitted[user_id].language == "Not included":
            students_submitted[user_id].language = remove_any_tags(answer["text"])

    # prefer_communication_method
    communication_method_dict = {
        "Discord": 0,
        "Text/Phone Number": 1,
        "Email": 2,
        "Canvas Groups": 3
    }
    for answer_set in question_index["prefer_communication_method"]["answers"]:
        answer_text = answer_set["text"]
        contact_index = communication_method_dict[answer_text]
        for user_id in answer_set["user_ids"]:
            students_submitted[user_id].contactPreference[contact_index] = True

    # prefer_communication_info
    for user_id, answer in question_index["prefer_communication_info"].items():
        students_submitted[user_id].contactInformation[0] = answer["answer_for_Discord"]
        students_submitted[user_id].contactInformation[1] = answer["answer_for_Phone"]
        students_submitted[user_id].contactInformation[2] = answer["answer_for_Email"]

    # activity_specify
    for user_id, answer in question_index["activity_specify"].items():
        students_submitted[user_id].freeResponse = remove_any_tags(answer["text"])

    # Returns nothing. Modifies students_submitted by filling their respective fields
    return


# temporary stopgap for adding partner option
# add the actual question to the full quiz
def parsePartnerQuiz(quizData: pd, CLASS_ID: int, dictSt: dict, missingSt: dict):
    personNameQ = '1162587'
    personEmailQ = '1162588'
    if CLASS_ID == 516271:
        personNameQ = '1162590'
        personEmailQ = '1162591'

    questionList = [personNameQ, personEmailQ]  # all columns in the student data csv. Need for full question string
    fullQuestionList = quizData.columns.values.tolist()
    # print(fullQuestionList)
    # numerical location of the question
    questionsLoc = []
    # iterate through all column names in csv and add location of matching id to list
    for loc, question in enumerate(fullQuestionList):
        for id in questionList:
            if id in question:
                questionsLoc.append(loc)
    # make a dictionary where question id matches to the question location
    questionsDict = dict(zip(questionList, questionsLoc))
    questionsDict['id'] = quizData.columns.get_loc('id')
    questionsDict['name'] = quizData.columns.get_loc('name')

    for row in quizData.itertuples(index=False, name=None):
        id = row[questionsDict['id']]
        temp = row[questionsDict[personNameQ]]
        if type(temp) is str and (len(temp)):
            if id in dictSt:
                dictSt[id].partner = temp
            else:
                missingSt[id].partner = temp

        temp = row[questionsDict[personEmailQ]]
        if type(temp) is str and (len(temp)):

            if id in dictSt:
                dictSt[id].partnerEmail = temp
            else:
                missingSt[id].partnerEmail = temp
