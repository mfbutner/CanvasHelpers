from canvasapi import Canvas
import pprint
import pandas as pd
from studentClass import Student

def parse(studentData:pd, canvasClass:Canvas.Course):
    #Fill the dictionary and the student lists
    dictSt = {}
    for index, row in studentData.iterrows():

        #name and id
        tempStudent = Student(row['name'], row['id'])

        #pronouns that the student prefers
        tempStudent.pronouns = row[studentData.columns.str.contains('1085146')].item()

        #preferSame is True if the student would like to share their group with someone of the same gender
        if row[studentData.columns.str.contains('1085148')].item() == "If possible, I would prefer another person with the same pronouns as me.":
            tempStudent.preferSame = True
        else:
            tempStudent.preferSame = False

        #meeting times - Sun - Sat, Midnight-4, 4-8, 8-noon, etc  [0][0] is sunday at midnight to 4 time slot
        

        #asynch (2), synch (1), no pref (0)- how the student would like to meet
        studentSync = row[studentData.columns.str.contains('1085149')].item()
        if studentSync == "Synchronously":
            tempStudent.preferAsy = 1
        elif studentSync == "Asynchronously":
            tempStudent.preferAsy = 2
        else:
            tempStudent.preferAsy = 0
        #contact pref - Discord, Phone, Email, Canvas - 2 = yes, 1 = no preference, 0 = not comfortable
        tempArr = (row[studentData.column.str.contains('1085150')].item()).split(",")
        for i in range(4):
            if tempArr[i] == "No":
                tempStudent.contactPreference[i] = 0
            elif tempArr[i] == "Yes":
                tempStudent.contactPreference[i] = 2
            else:
                tempStudent.contactPreference[i] = 1
        tempArr.clear()

        #contact info - [DiscordHandle, PhoneNumber, personal@email.com]
        tempArr = (row[studentData.column.str.contains('1085151')].item()).split(",")
        for i in range(3):
            tempStudent.contactInformation[i] = tempArr[i]
        tempArr.clear()

        #prefer leader- True if they prefer to be the leader, false otherwise
        studentLeader = row[studentData.column.str.contains('1085152')].item()
        if studentLeader == "I like to lead.":
            tempStudent.preferLeader = True
        else:
            tempStudent.preferLeader = False

        #country - Country of Origin
        tempArr = (row[studentData.column.str.contains('1085153')].item()).split(",")
        freeResponse = row[studentData.column.str.contains('1091769')].item()
        if tempArr[0] == "Not Included":
            tempStudent.countryOfOrigin = freeResponse
        else:
            tempStudent.countryOfOrigin = tempArr[0]
        
        
        #preferCountry - True if they would like to have a groupmate from the same country
        if tempArr[1] == "No":
            tempStudent.preferCountry = False
        else: 
            tempStudent.preferCountry = True
        tempArr.clear()
        freeResponse = ''

        #languages - Preferred language
        freeResponse = row[studentData.column.str.contains('1085154')].item()
        tempResponse = row[studentData.column.str.contains('1091774')].item()
        if freeResponse == "Not Included":
            tempStudent.language = tempResponse
        else:
            tempStudent.language = freeResponse
        
        freeResponse = ''
        tempResponse = ''

        #Preferred stuff to do - the drop downs and free response
        freeResponse = (row[studentData.column.str.contains('1085156')].item()).split(",")
        tempStudent.option1 = freeResponse[0]
        tempStudent.option2 = freeResponse[1]
        tempStudent.freeResponse = row[studentData.column.str.contain('1085157')].item()

        freeResponse = ''
        tempStudent = ''
        
        #Priority of what they want
        tempStudent.priorityList = (row[studentData.column.str.contains('1091940')].item()).split(",")



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