"""
    This file has all the functions to create the body of the message for each group email
    main function is get_body which takes in a list of student objects and returns a string
    that string is the message body
"""
import numpy as np
# import tabulate for making the meeting times table
from tabulate import tabulate


def get_body(student_list: list):
    """
    creates the body of the email based on information from the students
    """
    # general information for the study group (names, contact method, free response activities)
    contact_method = preferred_contact_method(student_list)
    general_info_text = general_information_text(student_list, contact_method)
    body = f"{general_info_text}\n"
    # specified information for each student
    for student in student_list:
        # contact info if NOT canvas group
        if contact_method == "discord":
            contact_method_id = student.contact_information[0]
        elif contact_method == "phone number":
            contact_method_id = student.contact_information[1]
        elif contact_method == "email":
            contact_method_id = student.contact_information[2]
        else:
            contact_method_id = ""
        # sync or async
        sync = student.prefer_async

        if sync == 0:
            sync_text = "Prefers to meet synchronously "
        elif sync == 1:
            sync_text = "Has no preference meeting synchronously or asynchronously"
        else:
            sync_text = "Prefers to meet asynchronously"
        # put in everyone's preferred meeting times (specified for each person)

        # put in preferred activities (specified for each person)
        preferred_activity_text = ""
        if student.activity_choice:
            preferred_activity_text = f"{student.activity_choice}"

        # put it all into the body
        body += f"{student.name}: \n"
        if contact_method_id != "":
            body += f"Contact information: {contact_method_id}\n"
        else:
            body += f"Contact information: {student.schoolEmail}\n"
        body += f"{sync_text}\n"
        # body += f"{meeting_time_text}"
        if preferred_activity_text != "":
            body += f"Prefers to {preferred_activity_text.lower()}\n"
        body += "\n"
    return body


def preferred_lang(student_list: list):
    """
        function to check if everyone has the same lang pref
        If consensus, use that language
        no consensus, use English default
        return the string of the language to use
        Args:
            student_list (list): list of student objects
    """
    consensus_lang = student_list[0].language
    for student in student_list:
        if student.language != consensus_lang:
            consensus_lang = "English"
    return consensus_lang


def preferred_contact_method(student_list: list):
    """
        checks to see if everyone has the same preferred contact method
        return the preferred contact method (canvas group if no matches)
    """
    contact_arr = [0, 0, 0, 0]
    num_students = len(student_list)
    for student in student_list:
        contact_arr += np.array(student.contact_preference)

    if contact_arr[0] == num_students:
        return "discord"
    elif contact_arr[1] == num_students:
        return "phone number"
    elif contact_arr[2] == num_students:
        return "email"
    return "canvas groups"


def general_information_text(student_list: list, contact_method: str):
    """
        the general information text for each study group. this includes the names of the members,
        preferred contact method (canvas group if no matches), and the free response.
    """
    general_info_text = ""
    names_text = ""
    free_response_text = ""

    for student in range(len(student_list)):
        if student_list[student].free_response != "":
            free_response_text += f"{student_list[student].free_response}, "
        if student == len(student_list) - 1:
            free_response_text = free_response_text[:-2]
            names_text += f"and {student_list[student].name}"
        else:
            names_text += f"{student_list[student].name}, "

    meeting_times_list_time = meeting_times_list(student_list)
    meeting_table(meeting_times_list_time)

    lang = preferred_lang(student_list)

    general_info_text += f"This week, your group members are {names_text}.\n"
    if contact_method == "canvas groups":
        general_info_text += f"Please check your canvas groups to contact them.\n"
    else:
        general_info_text += f"You all prefer to meet via {contact_method}.\n"
    general_info_text += f"Some things you and your group members would like to do together are {free_response_text}.\n"
    general_info_text += f"Primary Language for Communication: {lang}\n"
    return general_info_text


def meeting_times_list(student_list: list):
    """
    return a list of lists of when people are free
    each row of the list will be the list of TIMES people are free that DAY
    there are 6 times total, so 6 rows
    """
    meeting_time_list = [[], [], [], [], [], []]

    time_names = ["Midnight - 4AM", "4AM - 8AM", "8AM - Noon", "Noon -  4PM", "4PM - 8PM", "8PM - Midnight"]

    for time in range(0, 6):
        student_times = ["", "", "", "", "", "", ""]
        for day in range(0, 7):
            for student_num in range(0, len(student_list)):
                student = student_list[student_num]
                if student.meeting_times[day][time] == 1:
                    student_times[day] += student.name
                    if student_num != len(student_list) - 1:
                        student_times[day] += "\n"

        student_times.insert(0, time_names[time])
        meeting_time_list[time] = student_times
    return meeting_time_list


def meeting_table(times: list):
    """update the table.txt to the information from list using tabulate library
    Args:
        times (list): 2D list of TIMES of names of students who are available
                      note: times[0] is all the availability of students from Midnight to 4am
    """
    col_names = ["Times", "Sun", "Mon", "Tues", "Wed", "Thur", "Fri", "Sat"]
    table = tabulate([times[0], times[1], times[2], times[3], times[4], times[5]], col_names, tablefmt="grid")
    with open('table.txt', 'w') as w:
        w.write(str(table))
    return


def get_emails(student_list: list):
    """
    Gets all the emails from the student objects
    """
    email_arr = []
    for i in range(len(student_list)):
        email_arr.append(student_list[i].schoolEmail)
    return email_arr
