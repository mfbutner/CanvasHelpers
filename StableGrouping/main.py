from canvasapi import Canvas
import pandas as pd
from makeGroups import makeGroups
from checkValidGroup import invalidGroupDict
from analyzeCode import gradeGroups
from sendCanvasConvo import sendConvo
from canvasapi.canvas_object import CanvasObject
from studentClass import Student
from parseStudent import parse_students, parse, parseEmails, parsePartnerQuiz, parse_submissions
import json
from dotenv import dotenv_values

# Load .env file with environment variables from project root
env = dotenv_values("../.env")
API_URL = env["API_URL"]
API_KEY = env["API_KEY"]

# Load config file for this session
config_file = open("../config.json")
config = json.load(config_file)
config_file.close()

# Macros that will have to change to the appropriate class and survey number

# ECS 36A
# CLASS_ID = 574775 # ECS 36A
# QUIZ_ID = 123073 # ECS 36A main quiz
# className = "ECS 36A"

# ECS 36B
# CLASS_ID = 569280 #36B
# QUIZ_ID = 123095 # ECS 36B main quiz
# className = "ECS 36B"
# QUIZ_ID2 = 1 # who do you want to be with quiz

# studyGroupNumber = "Fifth Study Group"

# Use API Key and URL to authenticate upcoming Canvas API Calls
canvas = Canvas(API_URL, API_KEY)

# Obtain selected course from the Canvas API
course = canvas.get_course(config.course.id)

# Get a list of all students still enrolled in the course
students = course.get_users(enrollment_type="student")
# Parse students into Student class instances
all_students = parse_students(students)

# Get selected Canvas quiz to match partners with
quiz = course.get_quiz(config.quiz_id)

# Parse the student data of those that took the survey
students_submitted = parse_submissions(students, quiz, config)

dictStudentTakeSurvey = parse(studentData, config.course.id, course)

#Finds out who did not take survey (also updates the entire class with their school emails)
dictStudentDidNotTakeSurvey = parseEmails(dictStudentTakeSurvey, course)

#Find the appropriate quiz
#quiz2 = canvasClass.get_quiz(QUIZ_ID2)
#partnerQuizData = retrieveCSVfromCanvas(quiz2)
#parsePartnerQuiz(partnerQuizData ,canvasClass, dictStudentTakeSurvey, dictStudentDidNotTakeSurvey)

#Find the people who were matchedBefore, place it into a dict
matchedBefore = invalidGroupDict(canvas, config.course.id)

#Create the groups:
groups = makeGroups(dictStudentTakeSurvey, dictStudentDidNotTakeSurvey, matchedBefore)


#Now that groups are matched, send emails and form groups
sendConvo(canvas, config.course.id, groups, config.group_number)

#Anaylze the groups: how many students with a preference got it?
gradeGroups(groups, matchedBefore)
