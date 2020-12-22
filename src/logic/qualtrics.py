import canvasapi
import csv
from typing import List, Tuple, NamedTuple, Iterable


def upload_survey_completion(canvas_assignment: canvasapi.assignment.Assignment,
                             canvas_students: Iterable[canvasapi.user.User],
                             csv_path: str) -> None:
    with open(csv_path, newline='', errors='replace') as csv_file:
        grades = {student.id: {'posted_grade': 0} for student in canvas_students}
        email_to_student_id = {student.email: student.id for student in canvas_students}

        reader = csv.reader(csv_file)
        headers = next(reader)
        email_field = headers.index('RecipientEmail')
        percent_complete_field = headers.index('Progress')
        num_junk_rows = 2
        for i in range(num_junk_rows):
            next(reader)
        for completed_student in reader:
            completed_email = completed_student[email_field]
            if completed_email in email_to_student_id:
                percent_complete = float(completed_student[percent_complete_field]) / 100
                grades[email_to_student_id[completed_email]]['posted_grade'] = canvas_assignment.points_possible * percent_complete
            else:
                print(f'Unexpected email found: {completed_email}')

        canvas_assignment.submissions_bulk_update(grade_data=grades)


class QualtricsStudent(NamedTuple):
    email: str
    last_name: str
    first_name: str


def get_missing_qualtrics_users(users: List[canvasapi.user.User], qualtrics_csv_path: str) -> \
        Tuple[List[canvasapi.user.User], List[QualtricsStudent]]:
    canvas_students = {user.email: user for user in users}
    with open(qualtrics_csv_path, newline='') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)
        qualtrics_students = {row[3]: QualtricsStudent(row[3], row[2], row[1]) for row in reader}

        qualtrics_students_missing_from_canvas = [student for email, student in qualtrics_students.items() if
                                                  email not in canvas_students]
        canvas_students_missing_from_qualtrics = [student for email, student in canvas_students.items() if
                                                  email not in qualtrics_students]

        return canvas_students_missing_from_qualtrics, qualtrics_students_missing_from_canvas
