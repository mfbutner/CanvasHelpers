import re
import canvasapi
import pandas as pd
from canvasapi import Canvas
from studentClass import Student
import json

def parse_students(canvas_students):
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
                students_submitted[user_id].preferSame = 2
            elif answer_text == "I would prefer another person who does not have the same pronouns as I do.":
                students_submitted[user_id].preferSame = 0
            else:
                students_submitted[user_id].preferSame = 1

    # 0 - No preference (Default)
    # 1 - Synchronous
    # 2 - Asynchronous
    for answer in question_index["prefer_synchronous"]["answers"]:
        answer_text = answer["text"]
        for user_id in answer["user_ids"]:
            if answer_text == "Synchronously":
                students_submitted[user_id].preferAsy = 1
            elif answer_text == "Asynchronously":
                students_submitted[user_id].preferAsy = 2
            else:
                students_submitted[user_id].preferAsy = 0

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
                students_submitted[user_id].international = 0
            elif answer_text == "I would like to be placed with another international student.":
                students_submitted[user_id].international = 2
            else:
                students_submitted[user_id].international = 1

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
                students_submitted[user_id].confidence = 2
            elif answer_text == "I could really use some help.":
                students_submitted[user_id].confidence = 0
            else:
                students_submitted[user_id].confidence = 1

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
    priority_list = ["top","second","third","fourth","fifth"]
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
            str = answer["text"]
            first_close = str.find('>')
            end_close = str.rfind('<')
            students_submitted[user_id].pronouns = str[first_close + 1:end_close]

    # language_other
    for user_id, answer in question_index["language_other"].items():
        if students_submitted[user_id].language == "Not included":
            str = answer["text"]
            first_close = str.find('>')
            end_close = str.rfind('<')
            students_submitted[user_id].language = str[first_close + 1:end_close]

    # Returns nothing. Modifies students_submitted by filling their respective fields
    return


def parse(studentData:pd, CLASS_ID: int, canvasClass:canvasapi.course.Course):
    #Fill the dictionary and the student lists
    dictSt = {}
    #ECS 36B
    pronounsQ = '1252650'
    pronounsFree = '1252651'
    genderMatchQ = '1252652'
    syncQ = '1252653'
    timeQ = '1252654'
    commPreferenceQ = '1252655'
    commValuesQ = '1252656'
    leaderQ = '1252657'
    countryQ = '1091825'
    countryFree = '1091826'
    internationalQ = '1252658'
    languageQ = '1252659'
    languageFree = '1252660'
    groupWantsQ = '1252661'
    groupWantsFree = '1252662'
    priorityQ = '1252663'
    studentPerfQ = '1252664'

    #ECS 36A
    #Set default to ECS 36B, but it could also be 36A
    #This will need to be changed each time the quiz is changed
    if CLASS_ID == 574775: # ECS 36A
        pronounsQ = '1252518'
        pronounsFree = '1252519'
        genderMatchQ = '1252520'
        syncQ = '1252521'
        timeQ = '1252522'
        commPreferenceQ = '1252523'
        commValuesQ = '1252524'
        leaderQ = '1252525'
        countryQ = '1091825'
        countryFree = '1091826'
        internationalQ = '1252526'
        languageQ = '1252527'
        languageFree = '1252528'
        groupWantsQ = '1252529'
        groupWantsFree = '1252530'
        priorityQ = '1252531'
        studentPerfQ = '1252532'

# the list of question ids of questions
    questionList = [pronounsQ, pronounsFree, genderMatchQ, syncQ, timeQ, commPreferenceQ, commValuesQ, leaderQ, internationalQ, languageQ, languageFree, groupWantsQ, groupWantsFree, priorityQ, studentPerfQ]
    # all columns in the student data csv. Need for full question string
    fullQuestionList = studentData.columns.values.tolist()
    # print(fullQuestionList)
    # numerical location of the question
    questionsLoc = []
    # iterate through all column names in csv and add location of matching id to list
    for loc, question in enumerate(fullQuestionList):
        for id in questionList:
            if id in question:
                questionsLoc.append(loc)
    # for item in questionList:
      #  questionsFull.append([word for word in fullQuestionList if item in word])
    #for item in questionsFull:
    #    questionLoc.append(studentData.columns.get_loc(item))
    questionsDict = dict(zip(questionList, questionsLoc))
    questionsDict['id'] = studentData.columns.get_loc('id')
    questionsDict['name'] = studentData.columns.get_loc('name')

    students_still_enrolled = canvasClass.get_users(enrollment_type=('student',), sort='username')
    students_still_enrolled = {student.id for student in students_still_enrolled}

    for row in studentData.itertuples(index=False, name=None):
        if row[questionsDict['id']] not in students_still_enrolled:
            continue

        #name and id
        tempStudent = Student(row[questionsDict['id']], row[questionsDict['name']])

        #pronouns that the student prefers
        tempArr = row[questionsDict[pronounsQ]]

        freeResponse = row[questionsDict[pronounsFree]]
        if len(tempArr) != 0:
            if tempArr == "Not Included":
                tempStudent.pronouns = freeResponse
            else:
                tempStudent.pronouns  = tempArr

        #preferSame is True if the student would like to share their group with someone of the same gender
        tempArr = row[questionsDict[genderMatchQ]]
        if type(tempArr) is str:
            if tempArr == "I would prefer another person who as the same pronouns as I do.":
                tempStudent.preferSame = 2
            elif tempArr == "I would prefer another person who does not have the same pronouns as I do.":
                tempStudent.preferSame = 0
            elif tempArr == "No preference":
                tempStudent.preferSame = 1


        #meeting times - Sun - Sat, Midnight-4, 4-8, 8-noon, etc  [0][0] is sunday at midnight to 4 time slot
        tempArr = row[questionsDict[timeQ]]
        if type(tempArr) is str:
            meetingTimes = tempArr.split(",")
            daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri","Sat"]
            for i in range(7):
                for j in range(1, 7):
                    if daysOfWeek[i] + str(j) in meetingTimes:
                        tempStudent.meetingTimes[i][(j - 1)] = True


        #asynch (2), synch (1), no pref (0)- how the student would like to meet
        studentSync = row[questionsDict[syncQ]]
        if type(studentSync) is str:
            if studentSync == "Synchronously":
                tempStudent.preferAsy = 1
            elif studentSync == "Asynchronously":
                tempStudent.preferAsy = 2
            else:
                tempStudent.preferAsy = 0

        #contact pref - Discord, Phone, Email, Canvas - 2 = yes, 1 = no preference, 0 = not comfortable
        tempArr = (row[questionsDict[commPreferenceQ]])
        if type(tempArr) is str:
            contactPreference = tempArr.split(",")
            # Parse which contact method student wants from a list
            if "Discord" in contactPreference:
                (tempStudent.contactPreference)[0] = True
            if "Text/Phone Number" in contactPreference:
                (tempStudent.contactPreference)[1] = True
            if "Email" in contactPreference:
                (tempStudent.contactPreference)[2] = True
            if "Canvas Groups" in contactPreference:
                (tempStudent.contactPreference)[3] = True

        #contact info - [DiscordHandle, PhoneNumber, personal@email.com]
        tempArr = (row[questionsDict[commValuesQ]])
        if type(tempArr) is str:
            contactInfo = tempArr.split(",")
            for i in range(3):
                tempStudent.contactInformation[i] = contactInfo[i]

        #prefer leader- True if they prefer to be the leader, false otherwise
        studentLeader = row[questionsDict[leaderQ]]
        if type(studentLeader) is str:
            if studentLeader == "I like to lead.":
                tempStudent.preferLeader = True
            else:
                tempStudent.preferLeader = False

        #country - Country of Origin
        '''
        tempArr = (row[studentData.columns.str.contains(countryQ)].tolist())
        freeResponse = row[studentData.columns.str.contains(countryFree)].tolist()
        
        if type(tempArr[0]) is str:
            countryResult = tempArr[0].split(",")
            if len(countryResult) == 2:
                if countryResult[0] == "Not Included":
                    tempStudent.countryOfOrigin = freeResponse[0]
                else:
                    tempStudent.countryOfOrigin = tempArr[0]
            elif len(countryResult) == 1:
                if countryResult[0] == "Yes" or tempArr[0] == "No":
                    #preferCountry - True if they would like to have a groupmate from the same country
                    if tempArr[0] == "No":
                        tempStudent.preferCountry = False
                    else: 
                        tempStudent.preferCountry = True 
                else:
                    if tempArr[1] == "No":
                        tempStudent.preferCountry = False
                    else: 
                        tempStudent.preferCountry = True
                    
        tempArr.clear()
        freeResponse.clear()
        '''

        #international student preference
        tempArr = row[questionsDict[internationalQ]]
        if type(tempArr) is str:
            if tempArr == "I would like to be placed with another international student.":
                tempStudent.international = 2
            elif tempArr == "No preference":
                tempStudent.international = 1
            elif tempArr == "I am not an international student.":
                tempStudent.international = 0

        #languages - Preferred language
        languageSelect = row[questionsDict[languageQ]]
        notIncluedeLanguage = row[questionsDict[languageFree]]
        if type(languageSelect) is str:
            if languageSelect == "Not Included":
                tempStudent.language = notIncluedeLanguage
            else:
                tempStudent.language = languageSelect


        #Preferred stuff to do - the drop downs and free response
        tempArr = (row[questionsDict[groupWantsQ]])
        # Take the array of one item and check if its the right type,
        # then assign to the variable
        if type(tempArr) is str:
            tempStudent.option1 = tempArr
        tempResponse = row[questionsDict[groupWantsFree]]
        if type(tempResponse) is str:
            tempStudent.freeResponse = tempResponse

        #Priority of what they want
        freeResponse = row[questionsDict[priorityQ]]
        if type(freeResponse) is str:
            priority = freeResponse.split(",")
            while len(priority) < 5:
                priority.append("default")
            tempStudent.priorityList = priority

        # how the student feels in the class
        tempArr = row[questionsDict[studentPerfQ]]
        if type(tempArr) is str:
            if tempArr == "I'm confident.":
                tempStudent.confidence = 2
            elif tempArr == "I have some questions.":
                tempStudent.confidence = 1
            elif tempArr == "I could really use some help.":
                tempStudent.confidence = 0

        #Add the student to the dictionary of all students
        dictSt[row[questionsDict['id']]] = tempStudent

    return dictSt

def parseEmails(dictSt:dict, canvasClass:Canvas):
    missingSt = {}

    # update student dictionary to include people who did not take, as well as list composed of students who did not take the test
    # the class and add default emails to all students
    for user in canvasClass.get_users(enrollment_type=['student']):
        if user.id not in dictSt:
            if not hasattr(user, 'email'):
                continue
            name = user.sortable_name.split(",")
            temp = Student(user.id, user.name, user.email, name[1], name[0])
            missingSt[user.id] = temp
        else:
            name = user.sortable_name.split(",")
            tempStudent = dictSt[user.id]
            tempStudent.schoolEmail = user.email
            tempStudent.firstName = name[1]
            tempStudent.lastName = name[0]
            dictSt[user.id] = tempStudent

    return missingSt

# temporary stopgap for adding partner option
# add the actual question to the full quiz
def parsePartnerQuiz (quizData:pd, CLASS_ID:int , dictSt:dict, missingSt:dict) :

    personNameQ = '1162587'
    personEmailQ =  '1162588'
    if CLASS_ID == 516271 :
        personNameQ = '1162590'
        personEmailQ = '1162591'

    questionList = [personNameQ, personEmailQ]    # all columns in the student data csv. Need for full question string
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
            if id in dictSt :
                dictSt[id].partner = temp
            else :
                missingSt[id].partner = temp

        temp = row[questionsDict[personEmailQ]]
        if type(temp) is str and (len(temp)):

            if id in dictSt :
                dictSt[id].partnerEmail = temp
            else :
                missingSt[id].partnerEmail = temp
