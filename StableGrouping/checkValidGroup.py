""" This file has 2 functions: invalidGroupDict and isValidGroup.
invalidGroupDict returns a dictionary. This function only needs to be run once.
isValidGroup takes in that dictionary (and a list of student objects) and returns the count of how many times students have overlapped with each other
"""


def get_invalid_groups(course, all_students):
    """
    return a dictionary where the keys are STRING student id numbers, and the values are INT group numbers
    """

    # get a list of group categories
    group_categories = course.get_group_categories()

    studentid_groupid = {str(student.idNum): [] for student in all_students.values()}

    for category in group_categories:
        group_list = category.get_groups()
        for group in group_list:
            users_list = group.get_users()
            for user in users_list:
                studentid_groupid[str(user.id)].append(group.id)

    return studentid_groupid


def isValidGroup(invalid_group_dict: dict, student_list: list):
    """
    takes in a dictionary where the keys are STRING student id numbers, and the values are INT group numbers
    takes in a list of student objects
    returns an int (the number of times students have ever been in a same group before)
    """
    count = 0
    for student in student_list:
        student_id = str(student.idNum)
        prevMembers = invalid_group_dict[student_id]
        for other_student in student_list:
            other_student_id = str(other_student.idNum)
            if student_id != other_student_id:
                other_prevMembers = invalid_group_dict[other_student_id]
                sameGroup = set(prevMembers) & set(other_prevMembers)
                if sameGroup:
                    count += 1

    return count
