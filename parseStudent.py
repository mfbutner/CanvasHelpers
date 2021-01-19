from canvasapi import Canvas
import pprint
import math
import pandas as pd
from studentClass import Student

def parse(studentData:pd, canvasClass:Canvas):
    #Fill the dictionary and the student lists
    dictSt = {}
    pronounsQ = '1091818'
    pronounsFree = '1091819'
    genderMatchQ = '1091820'
    syncQ = '1091821'
    timeQ = '1095858'
    commPreferenceQ = '1091822'
    commValuesQ = '1091823'
    leaderQ = '1091824'
    countryQ = '1091825'
    countryFree = '1091826'
    languageQ = '1091827'
    languageFree = '1091828'
    groupWantsQ = '1091829'
    groupWantsFree = '1091830'
    priorityQ = '1095859'
    for index, row in studentData.iterrows():

        #name and id
        tempStudent = Student(row['name'], row['id'])

        #pronouns that the student prefers
        tempArr = row[studentData.columns.str.contains(pronounsQ)].tolist()
        freeResponse = row[studentData.columns.str.contains(pronounsFree)].tolist()
        if len(tempArr) != 0:
            if tempArr[0] == "Not Included":
                tempStudent.pronouns = freeResponse[0]
            else:
                tempStudent.pronouns  = tempArr[0]
        tempArr.clear()
        freeResponse.clear()

        #preferSame is True if the student would like to share their group with someone of the same gender
        tempArr = row[studentData.columns.str.contains(genderMatchQ)].tolist()
        if len(tempArr) != 0:
            if tempArr[0] == "If possible, I would prefer another person with the same pronouns as me.":
                tempStudent.preferSame = True
            else:
                tempStudent.preferSame = False

        tempArr.clear()

        #meeting times - Sun - Sat, Midnight-4, 4-8, 8-noon, etc  [0][0] is sunday at midnight to 4 time slot
        tempArr = row[studentData.columns.str.contains(commPreferenceQ)].tolist()
        if type(tempArr[0]) is str:
            meetingTimes = tempArr[0].split(",")
            daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri","Sat"]
            for i in range(7):
                for j in range(1, 7):
                    if daysOfWeek[i] + str(j) in meetingTimes:
                        tempStudent.meetingTimes[i][(j - 1)] = True
                    
        
        tempArr.clear()

        #asynch (2), synch (1), no pref (0)- how the student would like to meet
        studentSync = row[studentData.columns.str.contains(syncQ)].tolist()
        if type(studentSync[0]) is str:
            if studentSync == "Synchronously":
                tempStudent.preferAsy = 1
            elif studentSync == "Asynchronously":
                tempStudent.preferAsy = 2
            else:
                tempStudent.preferAsy = 0
        #contact pref - Discord, Phone, Email, Canvas - 2 = yes, 1 = no preference, 0 = not comfortable
        tempArr = (row[studentData.columns.str.contains(commPreferenceQ)].tolist())
        if type(tempArr[0]) is str:
            print(tempArr)
            contactPreference = tempArr[0].split(",")
            # Parse which contact method student wants from a list
            if "Discord" in contactPreference:
                tempStudent.contactPreference[0] = True
            if "Test/Phone Number" in contactPreference:
                tempStudent.contactPreference[1] = True
            if "Email" in contactPreference:
                tempStudent.contactPreference[3] = True 
            if "Canvas Groups" in contactPreference: 
                tempStudent.contactPreference[4] = True
           
        tempArr.clear()

        #contact info - [DiscordHandle, PhoneNumber, personal@email.com]
        tempArr = (row[studentData.columns.str.contains(commValuesQ)].tolist())
        if type(tempArr[0]) is str:
            contactInfo = tempArr[0].split(",")
            for i in range(3):
                tempStudent.contactInformation[i] = contactInfo[i]
        tempArr.clear()

        #prefer leader- True if they prefer to be the leader, false otherwise
        studentLeader = row[studentData.columns.str.contains(leaderQ)].tolist()
        if type(studentLeader[0]) is str:
            if studentLeader[0] == "I like to lead.":
                tempStudent.preferLeader = True
            else:
                tempStudent.preferLeader = False

        #country - Country of Origin
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

        #languages - Preferred language
        languageSelect = row[studentData.columns.str.contains(languageQ)].tolist()
        notIncluedeLanguage = row[studentData.columns.str.contains(languageFree)].tolist()
        if type(languageSelect[0]) is str:
            if languageSelect == "Not Included":
                tempStudent.language = notIncluedeLanguage[0]
            else:
                tempStudent.language = languageSelect[0]
            
        freeResponse.clear()
        notIncluedeLanguage.clear()

        #Preferred stuff to do - the drop downs and free response
        tempArr = (row[studentData.columns.str.contains(groupWantsQ)].tolist())
        # Take the array of one item and check if its the right type,
        # then assign to the variable
        if type(tempArr[0]) is str:
            tempStudent.option1 = tempArr[0]
        tempResponse = row[studentData.columns.str.contains(groupWantsFree)].tolist()
        if len(tempResponse) != 0:
            tempStudent.freeResponse = tempResponse[0]

        tempArr.clear()
        tempResponse.clear()
        
        
        #Priority of what they want
        freeResponse = (row[studentData.columns.str.contains(priorityQ)])
        if type(freeResponse[0]) is str:
            priority = freeResponse[0].split(",")
            tempStudent.priorityList = freeResponse[0]



        #Add the student to the dictionary of all students
        dictSt['id'] = tempStudent
        
    

    # update student dictionary to include people who did not take, as well as list composed of students who did not take the test
    # the class and add default emails to all students
    for user in canvasClass.get_users(enrollment_type=['student']):
        if user.id not in dictSt:
            temp = Student(user.id, user.name, user.email)
            dictSt[user.id] = temp
        else:
            dictSt[user.id].schoolEmail = user.email

    return dictSt