# Scripts
## quiz_creator
To be used at the start of the quarter.

Creates evaluation quiz assignments.

Typical usage: `python3 quiz_creator.py @creator_args.txt --questions_file_path ./questions.json`

```
options:
  --canvas_url CANVAS_URL
                        Your Canvas URL. By default, https://canvas.ucdavis.edu
  --key CANVAS_KEY      Your Canvas API key.
  --course_id COURSE_ID
                        The id of the course. This ID is located at the end of /coures in the Canvas URL.
  --questions_path QUESTIONS_PATH
                        The path to the JSON file of questions the evaluation quiz is based off of
  --assignment_group_name ASSIGNMENT_GROUP_NAME
                        The name of the assignment group for the Self and Peer Evaluation quiz assignment to be created under. If the assignment group is not found, you will be asked if
                        you want to create it.
  --assignment_name ASSIGNMENT_NAME
                        The name of the assignment you want to create.
  --due_date DUE_DATE   The date and time that the assignment is due in ISO Format: YYYY-MM-DDTHH:MM (e.g. 2022-03-03T23:59 -> March 3rd, 2022 at 11:59 PM)
  --unlock_date UNLOCK_DATE
                        The date the assignment should unlock. If not specified the assignment is made immediately available to students
  --late_days LATE_DAYS
                        The number of days an assignment can be turned in late. By default there are no late days.
```

## quiz_validator
To be used regularly as the quarter progresses. Ideally, this is ran once right after a evaluation assignment is due and once more after the resubmission deadline (students with quiz submission issues are given extra days to resubmit, so we want to run it twice).

Validates individual quiz assignemnts by checking if students submitted completely and correctly. Solo submission users and their justifactions are logged to a `.txt` file. A validation assignment is created / updated to notify students about their submission and whatever issues they might have had.

Note that each student in the quiz report JSON file will have a `valid_solo_submission` flag. By default all solo submission have `valid_solo_submission` set to `True`. If a student ended up not having a valid solo submisison, please set their `valid_solo_submission` value to `False`. The final grader script will handle this case by having their "partner" give them the lowest scores possible.

Typical usage: `python3 quiz_validator.py @validator_args.txt --questions_file_path ./questions.json`

```
options:
  --canvas_url CANVAS_URL
                        Your Canvas URL. By default, https://canvas.ucdavis.edu
  --key CANVAS_KEY      Your Canvas API key.
  --course_id COURSE_ID
                        The id of the course. This ID is located at the end of /coures in
                        the Canvas URL.
  --questions_path QUESTIONS_PATH
                        The path to the JSON file of questions the evaluation quiz is based
                        off of
  --assignment_group_name ASSIGNMENT_GROUP_NAME
                        The name of the assignment group where the Self and Peer Evaluation
                        quiz assignments are located.If the assignment group is not found,
                        you will be asked to select it from a list of assignment groups.
  --reopen_assignment   Whether or not to reopen the assignment for students to resubmit
                        and ammend their issues. If this flag is passed, the assignment
                        will be reopened for students to resubmit the assignment.
  --extra_days EXTRA_DAYS
                        The number of extra days students will get to resubmit the quiz
                        that had issues with. By default, it is 2 extra days.
  --quiz_report_path QUIZ_REPORT_PATH
                        The path to the directory where you want to store the quiz report.
                        It's ok if the directory path has a trailing `/`. NOTE: The report
                        WILL override any exist report with the same name.
  --solo_sub_path SOLO_SUB_PATH
                        The path to the directory where you want to store the solo
                        submissions log. It's ok if the directory path has a trailing `/`.
                        NOTE: The log WILL override any exist log with the same name.
  --quiz_errors_path QUIZ_ERRORS_PATH
                        The path to the directory where you want to store the quiz errors
                        log. It's ok if the directory path has a trailing `/`. NOTE: The
                        log WILL override any exist log with the same name.
```

## final_grader
To be used at the end of the quarter.

Calculates overall evaluation grades for students based on the quiz reports generated from `quiz_validator.py`. Also attached a CSV file of student's grade breakdown to the overall final grade assignment.

A template CSV file is loaded from `templates/report.csv` using jinja.

Typical usage: `python3 final_grader.py @final_grader_args.txt`

```
options:
  --canvas_url CANVAS_URL
                        Your Canvas URL. By default, https://canvas.ucdavis.edu
  --key CANVAS_KEY      Your Canvas API key.
  --course_id COURSE_ID
                        The id of the course. This ID is located at the end of /coures in
                        the Canvas URL.
  --questions_path QUESTIONS_PATH
                        The path to the JSON file of questions the evaluation quiz is based
                        off of
  --assignment_group_name ASSIGNMENT_GROUP_NAME
                        The name of the assignment group for the final, overall evaluation
                        assignment to be created under.If the assignment group is not
                        found, you will be asked to select it from a list of assignment
                        groups.
  --assignment_name ASSIGNMENT_NAME
                        The name of the final, overall evaluation assignment.
  --quiz_reports_path QUIZ_REPORTS_PATH
                        The path to the directory where the quiz reports are located. It's
                        ok if the directory path has a trailing `/`.
  --csv_reports_path CSV_REPORTS_PATH
                        The path to the directory to store each students' CSV report. It's
                        ok if the directory path has a trailing `/`.
```
