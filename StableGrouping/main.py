from canvasapi import Canvas
from makeGroups import makeGroups
from checkValidGroup import invalidGroupDict
from analyzeCode import gradeGroups
from sendCanvasConvo import sendConvo
from parseStudent import parse_students, parse_submissions, filter_students_submitted, parsePartnerQuiz
from dotenv import dotenv_values
import json

# Load .env file with environment variables from project root (Same folder as config.json, .gitignore, and more)
env = dotenv_values("../.env")
API_URL = env["API_URL"]
API_KEY = env["API_KEY"]

# Load config file for this session
config_file = open("../config.json")
config = json.load(config_file)
config_file.close()

# Use API Key and URL to authenticate upcoming Canvas API Calls
canvas = Canvas(API_URL, API_KEY)

# Obtain selected course from the Canvas API
course = canvas.get_course(config["course"]["id"])

# Get a list of all students still enrolled in the course
students = course.get_users(enrollment_type="student")
# Parse students into Student class instances. Sets basic info: idNum, name, name (first and last), and email
all_students = parse_students(students)

# Get selected Canvas quiz to match partners with
quiz = course.get_quiz(config["quiz_id"])

# Separate the all_students dictionary into two dictionaries: One for those who submitted and one for those who haven't
students_submitted = filter_students_submitted(all_students, quiz.get_submissions())
students_not_submitted = {s_id: student for (s_id, student) in all_students.items() if s_id not in students_submitted}

# Modifies Student instances in students_submitted by updating their properties with their quiz responses
parse_submissions(students_submitted, course, quiz, config)

print("Work In Progress (Quitting early)")
quit(1)

# Find the people who were matchedBefore, place it into a dict
matchedBefore = invalidGroupDict(canvas, config["course"]["id"])

# Create the groups:
groups = makeGroups(students_submitted, students_not_submitted, matchedBefore)

# Now that groups are matched, send emails and form groups
sendConvo(canvas, config["course"]["id"], groups, config["group_number"])

# Analyze the groups: how many students with a preference got it?
gradeGroups(groups, matchedBefore)
