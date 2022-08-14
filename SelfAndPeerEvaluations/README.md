# Scripts
## quiz_creator
To be used at the start of the quarter.

Creates evaluation quiz assignments.

Typical usage: `python3 quiz_creator.py @creator_args.txt --questions_file_path ./questions.json`

## quiz_validator
To be used regularly as the quarter progresses. Ideally, this is ran once right after a evaluation assignment is due and once more after the resubmission deadline (students with quiz submission issues are given extra days to resubmit).

Validates individual quiz assignemnts by checking if students submitted completely and correctly.

Typical usage: `python3 quiz_validator.py @validator_args.txt --questions_file_path ./questions.json`

## final_grader
To be used at the end of the quarter.

Calculates overall evaluation grades for students based on the quiz reports generated from `quiz_validator.py`. Also attached a CSV file of student's grade breakdown to the overall final grade assignment.

Typical usage: `python3 final_grader.py @final_grader_args.txt`
