import canvasapi
from collections import defaultdict
import random


def find_partner_eval_ag(
    course: canvasapi.course.Course,
) -> canvasapi.assignment.AssignmentGroup:
    """
    looks for an AssignmentGroup named "Partner Evaluations"
    ends program if no AssignmentGroup is found
    :returns: "Partner Evaluations" assignment group
    """
    partner_eval_ag = None
    for ag in course.get_assignment_groups():
        if ag.name == "Partner Evalulations":
            partner_eval_ag = ag
            break

    if partner_eval_ag is None:
        print('"Partner Evaluations" category does not exist!')
        print("Cannot grade, so ending program now")
        exit(1)

    return course.get_assignment_group(partner_eval_ag.id, include=["assignments"])


def make_student_id_map(course: canvasapi.course.Course) -> dict[str, int]:
    """
    Creates a mapping of unique student sortable names to Canvas ID's
    we initially create a dict where keys are student names and value is list [SID, canvas ID] so that we can have a student's SID avaliable for duplicates
    If student sortable names are duplicate, then last 4 or 5 digits are appended to student sortable name
    :returns: dict where key is unique sortable name and value is canvas ID
    """
    raw_students = defaultdict(list)
    dup_list = set()
    for raw_student in course.get_users(sort="username", enrollment_type=["student"]):
        if (
            raw_student.sis_user_id is None
        ):  # FIXME: delete for real class; not all sandbox student have SID
            raw_student.sis_user_id = random.randint(0, 100)

        if raw_student.sortable_name in dup_list:
            add_another_duplicate_student(raw_student, raw_students)
        elif raw_student.sortable_name in raw_students.keys():
            add_first_duplicate_student(raw_student, dup_list, raw_students)
        else:
            raw_students[raw_student.sortable_name] = [
                raw_student.sis_user_id,
                raw_student.id,
            ]

    student_id_map = {student: raw_students[student][1] for student in raw_students}
    return student_id_map


def add_another_duplicate_student(
    dupe_student: canvasapi.user.User, raw_students: dict[str, list]
) -> None:
    """
    Adds in the duplicate student with their last 4 or 5 SID digits appened to their name
    Modifies students in raw_students if necessary
    :param dupe_student: the duplicate student to be added to raw_students
    :param raw_students: the dict of all students
    :returns: None, instead, raw_students is directly modified
    """
    duplicate_name = dupe_student.sortable_name
    dupe_SID = str(dupe_student.sis_user_id)
    if duplicate_name + " (XXXXX" + dupe_SID[-4:] + ")" in raw_students:
        in_dict_SID = raw_students[duplicate_name + " (XXXXX" + dupe_SID[-4:] + ")"][0]
        raw_students.pop(raw_students[duplicate_name + " (XXXXX" + dupe_SID[-4:] + ")"])
        raw_students[duplicate_name + " (XXXXX" + in_dict_SID[-5:] + ")"] = in_dict_SID
        raw_students[duplicate_name + " (XXXXX" + dupe_SID[-5:] + ")"] = [
            dupe_SID,
            dupe_student.id,
        ]
    else:
        raw_students[duplicate_name + " (XXXXX" + dupe_SID[-4:] + ")"] = [
            dupe_SID,
            dupe_student.id,
        ]


def add_first_duplicate_student(
    dupe_student: canvasapi.user.User, dupe_list: set, raw_students: dict[str, list]
) -> None:
    """
    Adds in the duplicate student with their last 4 or 5 SID digits appended to their name
    Also removes the original student in the raw_students dict and
    adds the original student back with their last 4 or 5 SID digits appended to their name
    :param dupe_student: the duplicate student to be added to raw_students
    :param dup_list: the list of sortable_names that have duplicate students
    :param raw_students: the dict of all students
    :returns: None, instead, dup_list and raw_students are directly modified
    """
    duplicate_name = dupe_student.sortable_name
    dupe_list.add(duplicate_name)

    in_dict_SID = str(raw_students[dupe_student.sortable_name][0])
    dupe_SID = str(dupe_student.sis_user_id)
    for index in range(4, 6):
        if in_dict_SID[-index:] == dupe_SID[-index:]:
            continue
        # add duplicate student in with appened SID
        raw_students[duplicate_name + " (XXXXX" + dupe_SID[-index:] + ")"] = [
            dupe_SID,
            dupe_student.id,
        ]
        # add original student back in with appened SID
        raw_students[
            duplicate_name + " (XXXXX" + in_dict_SID[-index:] + ")"
        ] = raw_students[dupe_student.sortable_name]
        raw_students.pop(dupe_student.sortable_name)
        break