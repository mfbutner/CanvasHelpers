# Good job Janet for start working!!

# GUI part 1: "Tell me about this csv": Given a preview of the first 10 rows of the 3rd party csv (ex: mimir), user drag
#             and drop which row is STUDENTS: "first_name", "last_name", "NAME" (MAY separate by comma OR whitespace,
#             worry about it later), "email", "SID", HOMEWORK: homework1, QUIZ: quiz1, quiz2, EXAM: midterm1, final etc.
#             NOTE: User MUST match AT LEAST one of the columns to move on: "first_name" AND "last_name", "name", "SID",
#             "email"
#
# GUI part 2: "How to match the rest": After 1st and 2nd degree matches, show user the leftover from both
#             lists (Canvas student list: first_name, last_name, school_email, SID; 3rd party csv: name, Or, first_name,
#             last_name, email, SID (whichever is available). Let canvas list be on the left, 3rd party csv rows be on
#             the right, and let user drag and drop the matching rows from both sides to the box below them. After user
#             finish matching, whatever left in both sides should be disregarded.
#             NOTE: There will be some pre-matched results from 2nd degree match (unique leftover full name and unique
#             leftover last name) in the below box. Ask user to VERIFY the pre-matched results.


# Part 1: Don't need to ask for canvas list, I was already given Canvas course object. Can use canvas course object to
#         do the additional query (student list, assignments, etc)

# Part 2: Ask for the 3rd party csv address (GUI!!!!! THIS IS GUI!!!!! Make it look like when word doc asks for document
#         location.)

# Part 3: "Tell me about this csv" (GUI part 1)

# Part 4: Match by Email (1st degree match)

# Part 5: Match by SID, IF SID is available (Continue 1st degree match)

# Part 6: Match by unique full name after 1st degree match (2nd degree match) (######## Put the result in the below box)

# Part 7: Match by unique last name after 1nd degree match (Continue 2rd degree match) (######## Put the result in the
#         below box)

# Part 8: "How to match the rest" (GUI part 2)

# Part 9: Upload the grades to Canvas


# NOTE: 1. First Gui part 1, then this logic program (start.py), so CanvasGradeTransfer instance only exits AFTER Gui
#          part1 hits "play", therefore you will have everything (course_name, email_index, name_index,
#          assignment1_index, etc.) and you can use this list to create the logic instance.

#       2. Gui part1 returns a list of mix of strings ("First_name", "Last_name", "email", "SID") and NA (placeholders,
#          columns that we are not using), and instances of Canvas assignments. Only Canvas assignments are instances of
#          class because name column (for example) in csv doesn't represent a unique entity (names for multiple
#          students, grades are all for the same assignment)

#       3. Gui gets a course, and it downloads the available assignments in that course, so the drag and drop can tell
#          me which column is canvas.course.assignment1.

#       4. Want to avoid asking Canvas stuff. If already asked before, better to pass the info through instead of asking
#          Canvas again.
#
#       5. Gui part1 takes the Canvas course as argument and in Gui part1 we ask CanvasAPI for assignment_group. For
#          each assignment group (quiz, exam, projects, ...), ask for specific assignment names.
#
#       6. Gui part1 will NOT be in this file, it will be on its own file under "GUI" directory.
#
#       7. CanvasGradeTransfer should NEVER receive an instance of Gui_part1 class. Should write start.py as if
#          gui_part1 doesn't exit (don't know it exists as in logic wise, like that index_list can be passed from
#          anywhere).


# "command + option + L" to make the code looks nice


import canvasapi
from typing import List, Union


class CanvasGradeTransfer:

    # csv_path because we still need to read the csv after knowing what the header situation is.
    def __init__(self, course: canvasapi.course.Course,
                 index_list: List[Union[str, None, canvasapi.assignment.Assignment]],
                 csv_path: str):

        self.course = course
        self.assignments_list = self.create_assignments_list()
        self.third_party_csv = self.get_csv()
