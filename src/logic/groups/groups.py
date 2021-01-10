import canvasapi
import csv
from typing import Iterable, Dict, List


def download_groups_to_csv(group_category: canvasapi.group.GroupCategory, csv_path: str,
                           group_category_fields_to_include: Iterable['str'] = ('name',),
                           headers: Iterable[str] = ('Group Name', 'Email', 'Student Id', 'Last Name', 'First Name'),
                           group_fields_to_include: Iterable[str] = ('name',),
                           user_fields_to_include: Iterable[str] = (
                                   'integration_id', 'sis_user_id', 'last_name', 'first_name')) -> None:
    """

    :param group_category: The group category to download information from
    :param csv_path: The location to write the csv file to
    :param group_category_fields_to_include: The fields of the group category to include.
    See https://canvas.instructure.com/doc/api/group_categories.html for field names
    :param headers: The headers to place at the top of the csv
    :param group_fields_to_include: The names of the fields in the group to include.
    See https://canvas.instructure.com/doc/api/groups.html for field names
    :param user_fields_to_include:The names of the fields in the user to include.
    See https://canvas.instructure.com/doc/api/users.html for field names. Also supports last_name and first_name
    :return:
    """
    with open(csv_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        group_category_fields_to_include = tuple(group_category_fields_to_include)
        headers = tuple(headers)
        group_fields_to_include = tuple(group_fields_to_include)
        user_fields_to_include = tuple(user_fields_to_include)

        writer.writerow([getattr(group_category, field) if hasattr(group_category, field) else '' for field in
                         group_category_fields_to_include])
        writer.writerow([])  # write an empty line
        writer.writerow(headers)
        for group in group_category.get_groups():
            group_info = [getattr(group, field) if hasattr(group, field) else '' for field in group_fields_to_include]
            for user in group.get_users():
                user_info = []
                for field in user_fields_to_include:
                    last_name, first_name = user.sortable_name.split(',')
                    if field == 'last_name':
                        user_info.append(last_name)
                    elif field == 'first_name':
                        user_info.append(first_name)
                    elif hasattr(user, field):
                        user_info.append(getattr(user, field))
                    else:
                        user_info.append('')
                writer.writerow(group_info + user_info)


def create_groups_from_csv(course: canvasapi.course.Course, csv_path: str,
                           behavior: str = 'update',
                           group_missing_members: bool = True):
    """
    csv should be structured as
    Group Category Name, Group Name, Email. Headers must be There
    :param course:
    :param csv_path:
    :param behavior:
    :param group_missing_members: distribute students who aren't explicitly in a group evenly among existing
    groups
    :return:
    """
    with open(csv_path, newline='') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # skip headers
        new_group_categories = dict()
        for row in reader:
            if row:
                row = [field.strip() for field in row]
                if row[0] not in new_group_categories:
                    new_group_categories[row[0]] = dict()
                if row[1] not in new_group_categories[row[0]]:
                    new_group_categories[row[0]][row[1]] = []
                new_group_categories[row[0]][row[1]].append(row[2])
    behavior = behavior.lower().strip()
    if behavior == 'overwrite':
        overwrite_group_categories(course, new_group_categories, 'email', group_missing_members)


def overwrite_group_categories(course: canvasapi.course.Course,
                               new_group_categories: Dict[str, Dict[str, List[str]]],
                               student_identifier: str,
                               group_missing_members: bool):
    current_group_categories = course.get_group_categories()

    # remove any existing matching group categories
    for group_category in current_group_categories:
        if group_category.name in new_group_categories:
            group_category.delete()

    # mapping of student identifier to student
    students = {getattr(student, student_identifier).lower(): student
                for student in course.get_users(enrollment_type=['student'])
                if hasattr(student, student_identifier)}
    for category_name, group in new_group_categories.items():
        group_category = course.create_group_category(name=category_name, self_signup=None)
        for group_name, member_identifiers in group.items():
            group = group_category.create_group(name=group_name)
            members = []
            for ident in member_identifiers:
                ident = ident.lower()
                if ident in students:
                    members.append(students[ident].id)
                else:
                    print(f'Could not locate {ident}')
            group.edit(members=members)
        if group_missing_members:
            group_category.assign_members()


def update_group_names_to_reflect_membership(group_category: canvasapi.group.GroupCategory,
                                             prefix: str = '', suffix: str = '', sep: str = '_') -> None:
    for group in group_category.get_groups():
        member_last_names = [member.sortable_name.split(',')[0] for member in group.get_users()]
        group_name = [prefix] + member_last_names + [suffix]
        group_name = sep.join(group_name)
        group.edit(name=group_name)


def transform_study_group_matches(qtbuddy_path, result_path, category_name):
    with open(qtbuddy_path, newline='') as in_file, open(result_path, mode='w', newline='') as out_file:
        reader = csv.reader(in_file)
        writer = csv.writer(out_file)
        email_counter = dict()
        next(reader)
        emails = []
        last_names = []
        writer.writerow(['Group Category Name, Group Name, Email'])
        for row in reader:
            row = [value for value in row if value]
            if row:
                if row[0].startswith("-0") or row[0].startswith("0"):
                    if emails and last_names:
                        group_name = '_'.join(last_names)
                        for email in emails:
                            writer.writerow([category_name, group_name, email])
                            if email in email_counter:
                                email_counter[email] += 1
                            else:
                                email_counter[email] = 1
                        emails.clear()
                        last_names.clear()
                else:
                    last_names.append(row[-2].strip().split()[-1])
                    emails.append(row[-1])
        if emails and last_names:
            group_name = '_'.join(last_names)
            for email in emails:
                writer.writerow([category_name, group_name, email])
                if email in email_counter:
                    email_counter[email] += 1
                else:
                    email_counter[email] = 1

        for email, count in email_counter.items():
            if count > 1:
                print(email, count)
