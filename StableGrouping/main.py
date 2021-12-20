
from canvasapi import Canvas
import sys
import pandas as pd
from makeGroups import makeGroups
from checkValidGroup import invalidGroupDict
from analyzeCode import gradeGroups
from sendCanvasConvo import sendConvo
from canvasapi import Canvas
from canvasapi.canvas_object import CanvasObject
from studentClass import Student
from parseStudent import parse, parseEmails, parsePartnerQuiz

def retrieveCSVfromCanvas(quiz:CanvasObject) :
       studentReport = quiz.create_report("student_analysis")
       reportProgress = None
       # URL of canvas progress object from studentReport
       reportProgressURL = studentReport.progress_url
       # parse so only the process id remains
       reportProgressID = reportProgressURL.removeprefix('https://canvas.ucdavis.edu/api/v1/progress/')

       # wait for student report to finish generating while the process has not completed or failed 
       while reportProgress != 'completed' and reportProgress != 'failed':
              reportProgressObj = canvas.get_progress(reportProgressID)
              reportProgress = reportProgressObj.workflow_state
              print(reportProgress)
       studentReportN = quiz.create_report("student_analysis")
       url = studentReportN.file["url"]
       studentData = pd.read_csv(url)

       return studentData

#Get the right class 
API_URL = "https://canvas.ucdavis.edu/"
API_KEY = sys.argv[1] #first command line parameter is your API KEY

#Macros that will have to change to the appropriate class and survey number

# ECS 36A
# CLASS_ID = 574775 # ECS 36A
# QUIZ_ID = 123073 # ECS 36A main quiz
# className = "ECS 36A"

# ECS 36B
CLASS_ID = 569280 #36B
QUIZ_ID = 123095 # ECS 36B main quiz
className = "ECS 36B"
# QUIZ_ID2 = 1 # who do you want to be with quiz

studyGroupNumber = "Fifth Study Group"


#Get the class data from canvas
canvas = Canvas(API_URL, API_KEY)
canvasClass = canvas.get_course(CLASS_ID)  

# Get the right quiz
quiz = canvasClass.get_quiz(QUIZ_ID)
studentReport = quiz.create_report("student_analysis")
reportProgress = None

# URL of canvas progress object from studentReport
reportProgressURL = studentReport.progress_url

# parse so only the process id remains
reportProgressID = reportProgressURL.removeprefix('https://canvas.ucdavis.edu/api/v1/progress/')

# wait for student report to finish generating while the process has not completed or failed 
while reportProgress != 'completed' and reportProgress != 'failed':
       reportProgressObj = canvas.get_progress(reportProgressID)
       reportProgress = reportProgressObj.workflow_state

studentReportN = quiz.create_report("student_analysis")
url = studentReportN.file["url"]
studentData = pd.read_csv(url)

#Parse the student data of those that took the survey
dictStudentTakeSurvey = parse(studentData, CLASS_ID, canvasClass)

#Finds out who did not take survey (also updates the entire class with their school emails)
dictStudentDidNotTakeSurvey = parseEmails(dictStudentTakeSurvey, canvasClass)

#Find the appropriate quiz
#quiz2 = canvasClass.get_quiz(QUIZ_ID2)
#partnerQuizData = retrieveCSVfromCanvas(quiz2)
#parsePartnerQuiz(partnerQuizData ,canvasClass, dictStudentTakeSurvey, dictStudentDidNotTakeSurvey)

#Find the people who were matchedBefore, place it into a dict 
matchedBefore = invalidGroupDict(canvas, CLASS_ID)

#Create the groups:
groups = makeGroups(dictStudentTakeSurvey, dictStudentDidNotTakeSurvey, matchedBefore)


#Now that groups are matched, send emails and form groups
sendConvo(canvas, CLASS_ID, groups, studyGroupNumber)

#Anaylze the groups: how many students with a preference got it?
gradeGroups(groups, matchedBefore)
