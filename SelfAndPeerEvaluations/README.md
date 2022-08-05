# Scripts
## partner_eval_quiz_creator
To be used at the start of the quarter.

Creates evaluation quiz assignments.

Create a `PartnerEvalQuizCreator` object by at least providing the `canvasapi.course.Course`, JSON file of quiz questions, and an assignment name.

Call `upload_to_canvas()` to upload a quiz assignment under the "Partner Evaluations" assignment group.

## partner_eval_quiz_validator
To be used regularly as the quarter progresses. Ideally, this is ran once right after a evaluation assignment is due and once more two days later (incorrect submissions are given 2 days to ammend their issues).

Validates individual quiz assignemnts by checking if students submitted completely and correctly.

Create a `PartnerEvalQuizValidator` object by at least providing the `canvasapi.course.Course` and JSON file of quiz questions.

Call `validate_quiz(True | False)` to validate a quiz. This function will ask you which quiz you want to validate. Then, it will store the quiz results into a JSON file in `./quiz_results/quiz_reports/`. A list of solo submisisons will be logged to a .txt file in `./quiz_results/solo_submissions/`. 

If `validate_quiz` is passed with a `True` flag, students will be assigned a "did you submit correctly" assignment for the quiz you asked to validate. Correct submisions will be given a 1/1 (100%). Incorrect submisison will be given a 0/1 (0%) and comments indicating which questions students need to go back and answer.
## partner_eval_quiz_final_grader
To be used at the end of the quarter.

Calculates overall evaluation grades for students based on the reports in `./quiz_results/quiz_reports/`. *Please make sure all the reports you want to use for grading are in this directory.*

Create a `PartnerEvalQuizFinalGrader` object by at least providing the `canvasapi.course.Course`.

Call `upload_final_grades_to_canvas("optional_assignment_name_here")` to upload final grades to Canvas. This function will create an assignment that gives students their overall evaluation grade and attach a CSV file of their grade breakdown. All student CSV files are stored in `./quiz_results/individual_student_reports`.
