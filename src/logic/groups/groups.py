import canvasapi
import csv
from typing import Iterable


def download_groups_to_csv(group_category: canvasapi.group.GroupCategory, csv_path: str,
                           group_category_fields_to_include: Iterable['str'] = ('name',),
                           headers: Iterable[str] = ('Group Name', 'Email', 'Student Id', 'Last Name', 'First Name'),
                           group_fields_to_include: Iterable[str] = ('name',),
                           user_fields_to_include: Iterable[str] = (
                                   'login_id', 'sis_user_id', 'last_name', 'first_name')) -> None:
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
                writer.writerow(group_info + user_info)
