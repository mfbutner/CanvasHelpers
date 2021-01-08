#!/usr/bin/env python3
from canvasapi import Canvas
import pprint
import pandas as pd
import xlrd
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
df = pd.read_csv(url)

#Alternatively use the download
#statFile  = pd.read_csv(r'\Users\rebek\Documents\Fall Quarter\Group.csv')   #<---- NEED TO CHANGE FOR EACH
#statColumn = pd.DataFrame(statFile, columns = ["name", "sis_id", """1085146: 
#What are your preferred pronouns?

#This information will NOT be shared with other students.Â Â """])

#print(statColumn)
#At this point do not actually need the class

loc = r'\Users\rebek\Documents\Fall Quarter\Group.xls' # <--- NEED To change to real thing and make into a xls
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)

#Fill the dictionary
dictSt = {}
for i in range(1, int(sheet.nrows)):
    print(sheet.cell_value(i, 0))

    #name and id
    dictSt[sheet.cell_value(i, 2)] = Student(sheet.cell_value(i, 1), sheet.cell_value(i, 0))

    #pronouns
    dictSt[sheet.cell_value(i, 2)].pronouns = sheet.cell_value(i, 9)

    #prefer same
    if sheet.cell_value(i, 9) == "If possible, I would prefer another person with the same pronouns as me.":
        dictSt[sheet.cell_value(i, 2)].preferSame = True
    else:
        dictSt[sheet.cell_value(i, 2)].preferSame = False

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
    dictSt[sheet.cell_value(i, 2)].pr = sheet.cell_value(i, 9)
    dictSt[sheet.cell_value(i, 2)].pronouns = sheet.cell_value(i, 9)
    dictSt[sheet.cell_value(i, 2)].pronouns = sheet.cell_value(i, 9)
    dictSt[sheet.cell_value(i, 2)].pronouns = sheet.cell_value(i, 9)
    dictSt[sheet.cell_value(i, 2)].pronouns = sheet.cell_value(i, 9)

# update student dictionary to include people who did not take
# the class and add default emails to all students
for user in canvasClass.get_users(enrollment_type=['student']):
    if user.id not in dictSt:
        dictSt[user.id] = Student(user.id, user.name, user.email)
    else:
        dictSt[user.id].schoolEmail = user.email

