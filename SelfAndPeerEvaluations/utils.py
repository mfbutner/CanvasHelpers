import argparse
import canvasapi
from collections import defaultdict
from typing import DefaultDict, Iterable, Union

JsonValue = Union[str, int, float, bool, list["JsonValue"], "JsonDict"]
JsonDict = dict[str, JsonValue]


def create_base_arguement_parser(
    prog: str, description: str, prefix: str
) -> argparse.ArgumentParser:
    """
    Creates a basic arguement parser with common arguements among all scripts
    :param prog: name of the program
    :param description: description of the program
    :param prefix: character to prefix file
    :returns: a basic arguement parser
    """
    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        fromfile_prefix_chars=prefix,
    )
    parser.add_argument(
        "--canvas_url",
        dest="canvas_url",
        required=True,
        type=str,
        default="https://canvas.ucdavis.edu/",
        help="Your Canvas URL. By default, https://canvas.ucdavis.edu",
    )
    parser.add_argument(
        "--key", dest="canvas_key", type=str, required=True, help="Your Canvas API key."
    )
    parser.add_argument(
        "--course_id",
        dest="course_id",
        type=int,
        required=True,
        help="The id of the course.\nThis ID is located at the end of /coures in the Canvas URL.",
    )
    parser.add_argument(
        "--questions_path",
        dest="questions_path",
        type=str,
        required=True,
        help="The path to the JSON file of questions the evaluation quiz is based off of",
    )
    return parser


def find_ag(
    course: canvasapi.course.Course, ag_name: str
) -> canvasapi.assignment.AssignmentGroup:
    """
    looks for an AssignmentGroup named ag_name
    if no AssignmentGroup is found, prompts user to select an AssignmentGroup
    :returns: assignment_group that includes assignment info
    """
    target_ag = None
    ag_list = []
    for ag in course.get_assignment_groups():
        ag_list.append(ag)
        if ag.name == ag_name:
            target_ag = ag
            break

    if target_ag is None:
        print(f"Cannot find {ag_name} assignment group")
        target_ag_index = select_ags_from_list(ag_list)
        target_ag = ag_list[target_ag_index]

    return course.get_assignment_group(target_ag.id, include=["assignments"])


def select_ags_from_list(ag_list: list[canvasapi.assignment.AssignmentGroup]) -> int:
    """
    lists out all the assignment groups in ag_list and prompts user to selects one
    :returns: index where selected assignment group is located in ag_list
    """
    print(f"Here are the assignment groups I found")
    for index, ag in enumerate(ag_list):
        print(str(index) + ".", ag.name)
    while True:
        index = input(
            f"Please select the assignment group (0 - {len(ag_list) - 1}). Or enter 'q' to quit the program: "
        )
        if input == "q":
            exit()
        try:
            index = int(index)
            if 0 <= index < len(ag_list):
                return index
        except:
            continue


def make_unique_student_id_map(
    students: Iterable[canvasapi.user.User], min_characters_of_email_to_use: int = 0
) -> dict[str, canvasapi.user.User]:
    """
    Creates a mapping from a unique, displayable id to a student. The id is the first_name, last_name (partial email).
    (partial email) only appears if there is more than one student with the same name or min_characters_of_email_to_use
    is set higher than 0. Partial Email is formed by taking characters from the front and back of the students' emails
    (excluding the email domain) until the email becomes unique among the students that have the same name.

    :param students: The students to create a unique mapping for
    :param min_characters_of_email_to_use: The minimum number of characters from the student's email that must be taken.
    This number is taken from the front AND back of the email so the actual number of characters from a student's
    email would be double the number specified. For example, if an email was abcdefg@example.com and
    min_characters_of_email_to_use was 2 then the email appended to the students name would be ab****fg@example.com
    :return: a dictionary mapping unique student ids to students
    """
    student_name_to_student_map: DefaultDict[str, list["Student"]] = defaultdict(list)

    # group students together that have the same name
    for student in students:
        student_name_to_student_map[student.sortable_name].append(student)

    unique_id_to_student_map = {}
    for students_with_same_name in student_name_to_student_map.values():
        for unique_id, student in _create_unique_identifier_for_students(
            students_with_same_name, min_characters_of_email_to_use
        ):
            unique_id_to_student_map[unique_id] = student
    return unique_id_to_student_map


def _create_unique_identifier_for_students(
    students_with_same_identifier: Iterable[canvasapi.user.User],
    min_characters_of_email_to_use: int = 0,
) -> Iterable[tuple[str, canvasapi.user.User]]:
    """
    Creates a unique identifier for each student in students_with_same_identifier. The identifier is
    last_name, first_name (partial_email).
    (partial email) only appears if there is more than one student with the same name or min_characters_of_email_to_use
    is set higher than 0. Partial Email is formed by taking characters from the front and back of the students' emails
    (excluding the email domain) until the email becomes unique among the students that have the same name.

    :param students_with_same_identifier: An iterable of one or more students that all share the same name
    :param min_characters_of_email_to_use: The minimum number of characters from the student's email that must be taken.
    This number is taken from the front AND back of the email so the actual number of characters from a student's
    email would be double the number specified. For example, if an email was abcdefg@example.com and
    min_characters_of_email_to_use was 2 then the email appended to the students name would be ab****fg@example.com
    :return: An iterable of tuples of the form (unique_id, User) for each User in students_with_same_identifier
    :raise ValueError if min_characters_of_email_to_use < 0
    """

    if min_characters_of_email_to_use < 0:
        raise ValueError(
            f"min_characters_of_email_to_use must be >= 0 but is {min_characters_of_email_to_use}"
        )

    # break students email into account and domain
    students_with_same_identifier = [
        (student, student.email.rsplit("@", 1))
        for student in students_with_same_identifier
    ]
    while (
        True
    ):  # while we haven't found a unique mapping for all students sharing the same name
        mappings = {}
        for student, (email_account, email_domain) in students_with_same_identifier:
            if min_characters_of_email_to_use * 2 > len(
                student.email
            ):  # maybe + 1 to deal with odd length emails
                duplicates = [
                    dup_student
                    for dup_student, (_, _) in students_with_same_identifier
                    if dup_student.email == student.email
                ]
                raise ValueError(
                    f"Impossible to form unique ids as {len(duplicates)} students "
                    f"share {student.sortable_name}({student.email})."
                )
            new_id = (
                f"{student.sortable_name} "
                f"({email_account[:min_characters_of_email_to_use]}"
                f"****"
                f"{email_account[-min_characters_of_email_to_use:]}"
                f"@{email_domain})"
                if min_characters_of_email_to_use > 0
                else student.sortable_name
            )
            if (
                new_id in mappings
            ):  # still matching despite adding a portion of their email to their name
                min_characters_of_email_to_use += 1  # use more of their email
                break
            else:
                mappings[new_id] = student
        else:
            return mappings.items()
