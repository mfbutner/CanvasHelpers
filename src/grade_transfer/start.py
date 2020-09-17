# Good job Janet for start working!!

# GUI part 1: "Tell me about this csv": Given a preview of the first 10 rows of the 3rd party csv (ex: mimir), user drag
#             and drop which row is "first_name", "last_name", "NAME" (MAY separate by comma OR whitespace, worry about
#             it later), "email", "SID", "grades_1", "grades_2", "ignore" etc.
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

# 

# Part 1: Don't need to ask for canvas list, I was already given Canvas course object. Can use canvas course object to
#         do the additional query (student list, assignments, etc)

# Part 2: Ask for the 3rd party csv address (GUI!!!!! THIS IS GUI!!!!! Make it look like when word doc asks for document
# location.)

# Part 3: "Tell me about this csv" (GUI part 1)

# Part 4: Match by Email (1st degree match)

# Part 5: Match by SID, IF SID is available (Continue 1st degree match)

# Part 5: Match by unique full name after 1st degree match (2nd degree match) (######## Put the result in the below box)

# Part 6: Match by unique last name after 1nd degree match (Continue 2rd degree match) (######## Put the result in the
#         below box)

# Part 7: "How to match the rest" (GUI part 2)

# Part 8: Upload the grades to Canvas

