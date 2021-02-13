from canvasapi import Canvas
import pprint
import math
import pandas as pd
from studentClass import Student

def parse(studentData:pd, CLASS_ID: int):
    #Fill the dictionary and the student lists
    dictSt = {}
    pronounsQ = '1106598'
    pronounsFree = '1106599'
    genderMatchQ = '1106600'
    syncQ = '1106601'
    timeQ = '1106602'
    commPreferenceQ = '1106603'
    commValuesQ = '1106604'
    leaderQ = '1106605'
    countryQ = '1091825'
    countryFree = '1091826'
    internationalQ = '1106606'
    languageQ = '1106607'
    languageFree = '1106608'
    groupWantsQ = '1106609'
    groupWantsFree = '1106610'
    priorityQ = '1106611'
    studentPerfQ = '1106612'

    #Set default to ECS 154A, but it could also be 36A
    #This will need to be changed each time the quiz is changed
    if CLASS_ID == 516271:
        pronounsQ = '1106640'
        pronounsFree = '1106641'
        genderMatchQ = '1106642'
        syncQ = '1106643'
        timeQ = '1106644'
        commPreferenceQ = '1106645'
        commValuesQ = '1106646'
        leaderQ = '1106647'
        countryQ = '1091825'
        countryFree = '1091826'
        internationalQ = '1106648'
        languageQ = '1106649'
        languageFree = '1106650'
        groupWantsQ = '1106651'
        groupWantsFree = '1106652'
        priorityQ = '1106653'
        studentPerfQ = '1106654'

# the list of question ids of questions 
    questionList = [pronounsQ, pronounsFree, genderMatchQ, syncQ, timeQ, commPreferenceQ, commValuesQ, leaderQ, internationalQ, languageQ, languageFree, groupWantsQ, groupWantsFree, priorityQ, studentPerfQ]
    # all columns in the student data csv. Need for full question string
    fullQuestionList = studentData.columns.values.tolist()
    # print(fullQuestionList)
    # numerical location of the question
    questionsLoc = []
    # iterate through all column names in csv and add location of matching id to list
    i = 0
    for question in fullQuestionList:
        for id in questionList:
            if id in question:
                questionsLoc.append(i)
        i += 1
    # for item in questionList:
      #  questionsFull.append([word for word in fullQuestionList if item in word])
    #for item in questionsFull:
    #    questionLoc.append(studentData.columns.get_loc(item))
    questionsDict = dict(zip(questionList, questionsLoc)) 
    questionsDict['id'] = studentData.columns.get_loc('id')
    questionsDict['name'] = studentData.columns.get_loc('name')

    for row in studentData.itertuples(index=False, name=None):

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
            contactPreference.clear()
        

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
