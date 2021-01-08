#!/usr/bin/env python3
from canvasapi import Canvas
import pprint
import csv
import pandas as pd

API_URL = "https://canvas.ucdavis.edu/"
API_KEY = "3438~F8UL89qNJVVOcpDpxmEQdEkGixcJm4vN1rZpwQebN0zJtXjUd0girRxeAXnRsCvc"

canvasN = Canvas(API_URL, API_KEY)

course = canvasN.get_course(1599)

assignment = course.get_quiz(108761)
var = assignment.get_statistics()
pp = pprint.PrettyPrinter(indent=4)
 
# printing all students in a class
for user in course.get_users(enrollment_type=['student']):
    print(user.email + " " + str(user.id) + " " +user.name)
print()
# request a student analysis type report of a quiz and print all available keys 
studentReport = assignment.create_report("student_analysis")
print(studentReport.__dict__.keys())
#pp.pprint(var[0].question_statistics[1]["answers"])
print()
# gets the csv of the student report and import it into pandas
url = studentReport.file["url"]
print(url)
df = pd.read_csv(url)
print(df[["1085147: \nIf you answered \"Not Included\" above, feel free to specify:\nThis information will NOT be shared with other students.\n"]])

#print(var[0].question_statistics[2]["answers"][0]["user_ids"])
    

    








