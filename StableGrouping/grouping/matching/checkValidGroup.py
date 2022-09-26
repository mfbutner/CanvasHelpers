"""
    This file has 2 functions: invalidGroupDict and is_valid_group.
    invalidGroupDict returns a dictionary. This function only needs to be run once.
    is_valid_group takes in that dictionary (and a list of Student objects) and returns how many times students have
                   overlapped with each other.
"""


def get_invalid_groups(course, all_students):
    """
        returns a dictionary where the keys are STRING student id numbers, and the values are INT group numbers
    """

    # get a list of group categories
    group_categories = course.get_group_categories()

    student_id_group_id_map = {str(student.id_num): [] for student in all_students.values()}

    for category in group_categories:
        group_list = category.get_groups()
        for group in group_list:
            users_list = group.get_users()
            for user in users_list:
                student_id_group_id_map[str(user.id)].append(group.id)

    return student_id_group_id_map


def is_valid_group(invalid_group_dict: dict, student_list: list):
    """
        takes in a dictionary where the keys are STRING student id numbers, and the values are INT group numbers
        takes in a list of student objects
        returns an int (the number of times students have ever been in a same group before)
    """
    count = 0
    for student in student_list:
        student_id = str(student.id_num)
        prev_members = invalid_group_dict[student_id]
        for other_student in student_list:
            other_student_id = str(other_student.id_num)
            if student_id != other_student_id:
                other_prev_members = invalid_group_dict[other_student_id]
                same_group = set(prev_members) & set(other_prev_members)
                if same_group:
                    count += 1

    return count
