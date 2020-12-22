import canvasapi
import csv
from typing import Iterable, Tuple


def download_users_to_csv(path_to_csv: str,
                          course: canvasapi.course.Course,
                          roles: Tuple[str] = ('student',),
                          headers: Iterable[str] = ('Last Name', 'First Name', 'Login Id', 'Email', 'SID', 'Canvas Id'),
                          user_fields: Iterable[str] = ('last_name', 'first_name', 'login_id', 'email', 'sis_user_id', 'id')):
    user_fields = list(user_fields)
    with open(path_to_csv, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        users = course.get_users(enrollment_type=roles, sort='username')
        writer.writerow(headers)
        for user in users:
            user_info = []
            for field in user_fields:
                last_name, first_name = user.sortable_name.split(',')
                if field == 'last_name':
                    user_info.append(last_name)
                elif field == 'first_name':
                    user_info.append(first_name)
                elif hasattr(user, field):
                    user_info.append(getattr(user, field))
                else:
                    user_info.append('')
            writer.writerow(user_info)
