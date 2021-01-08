#!/usr/bin/env python3
from canvasapi import Canvas
import pprint
import pandas as pd
from studentClass import Student

#Get the right class 
API_URL = "https://canvas.ucdavis.edu/"
API_KEY = "3438~F8UL89qNJVVOcpDpxmEQdEkGixcJm4vN1rZpwQebN0zJtXjUd0girRxeAXnRsCvc"
CLASS_ID = 1599
QUIZ_ID = 108761
canvas = Canvas(API_URL, API_KEY)
canvasClass = canvas.get_course(CLASS_ID)   #<---- NEED TO CHANGE TO BUTNERS REAL CLASS

# Get the right quiz and creating a Pandas dataFrame from the generated csv
quiz = canvasClass.get_quiz(QUIZ_ID)
studentReport = quiz.create_report("student_analysis")
url = studentReport.file["url"]
studentData = pd.read_csv(url)

#Alternatively use the download
#statFile  = pd.read_csv(r'\Users\rebek\Documents\Fall Quarter\Group.csv')   #<---- NEED TO CHANGE FOR EACH
#statColumn = pd.DataFrame(statFile, columns = ["name", "sis_id", """1085146: 
#What are your preferred pronouns?

#This information will NOT be shared with other students.Â Â """])

#print(statColumn)
#At this point do not actually need the class


#Fill the dictionary
dictSt = {}
for index, row in studentData.iterrrows():

    #name and id
    dictSt['id'] = Student(row['name'], row['id'])

    #pronouns
    dictSt['id'].pronouns = row[studentData.columns.str.contains('1085146')].item()

    #prefer same
    if row[studentData.columns.str.contains('1085148')].item() == "If possible, I would prefer another person with the same pronouns as me.":
        dictSt['id'].preferSame = True
    else:
        dictSt['id'].preferSame = False

    #meeting times

    #asynch, synch, no pref

    #contact pref

    #contact info

    #prefer leader

    #country

    #preferCountry

    #languages

    #preferlanguage

    #

# update student dictionary to include people who did not take
# the class and add default emails to all students
for user in canvasClass.get_users(enrollment_type=['student']):
    if user.id not in dictSt:
        dictSt[user.id] = Student(user.id, user.name, user.email)
    else:
        dictSt[user.id].schoolEmail = user.email

