"""
    This file is for sending the canvas conversation for each group (python3)
    last line is: send_convo(canvas, course_number, group_list, study_group_number)
    canvas is a canvas objects
    group_list should be a 2D list of student objects
    course_number is the number of the course
    study_group_number is the number of that week's study group (1-5)
"""
# Uses get_body to create the body of the message
from ..finalizing.createMessageBody import get_body


def get_student_ids(student_list: list):
    """
        takes in a list of student objects
        returns a list of strings where each string is a student's ID
    """
    student_ids = []
    for student in student_list:
        student_ids.append(str(student.id_num))
    return student_ids


def get_student_last_names(student_list: list):
    """
        Takes in the list of student objects
        gets the last names of everyone
        return a string of everyone's last names with underscores separating
    """
    student_names = " _"
    for student in student_list:
        student_names += student.lastName + "_"
    return student_names


def upload_table(canvas):
    """
        upload the table.txt to the "conversation attachments" folder
        return the id of the table to be attached
    """
    curr_user = canvas.get_current_user()

    folders = curr_user.get_folders()
    folder_id = 0
    for i in folders:
        if i.name == "conversation attachments":
            folder_id = i.id
    folder = curr_user.get_folder(folder_id)

    did_upload = folder.upload('table.txt')

    return did_upload[1]['id']


def send_convo(canvas, course_number, group_list, study_group_number):
    """
        for every group in the group_list, send a conversation for each student per group
    """
    course = canvas.get_course(course_number)

    category_name = "Study Groups " + study_group_number
    # make the study group category
    curr_group_category = course.create_group_category(name=category_name, self_signup=None)

    for group in range(len(group_list)):
        members = get_student_ids(group_list[group])
        last_names = get_student_last_names(group_list[group])
        group_name = "Study Group " + study_group_number + ":" + last_names
        # make the group
        curr_group = curr_group_category.create_group(name=group_name)
        # edit the group
        curr_group.edit(members=members)

        body = get_body(group_list[group])
        # make the conversation

        table_id = [upload_table(canvas)]
        canvas.create_conversation(recipients=members, body=body, subject=group_name, attachment_ids=table_id,
                                   force_new=True)
    return
