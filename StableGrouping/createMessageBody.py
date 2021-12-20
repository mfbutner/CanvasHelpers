"""This file has all the functions to create the body of the message for each group email
    main function is getBody which takes in a list of student objects and returns back a string
    that string is the message body
    """

# import numpy
import numpy as np

# import tablulate for making the meeting times table
from tabulate import tabulate


def getBody(student_list: list):
    """
    creates the body of the email based on information from the students
    """
    body = ""
    # general information for the study group (names, contact method, free response activities)
    contact_method = preferredContactMethod(student_list)
    general_info_text = generalInformationText(student_list, contact_method)
    body = f"{general_info_text}\n"
    #specified information for each student
    for student in student_list:
        #contact info if NOT canvas group
        if contact_method == "discord":
            contact_method_id = student.contactInformation[0]
        elif contact_method == "phone number":
            contact_method_id = student.contactInformation[1]
        elif contact_method == "email":
            contact_method_id = student.contactInformation[2]
        else:
            contact_method_id = ""
        # sync or async
        sync = student.preferAsy
        sync_text = ("Prefers to meet synchronously " if sync==0 else "Has no preference meeting synchronously or asynchronously" if sync==1 else "Prefers to meet asynchronously")
        # put in everyone's preferred meeting times (specified for each person)
        
        # put in preferred activities (specified for each person)
        preferred_activity_text = ""
        if "default" not in student.option1:
            preferred_activity_text = f"{student.option1}"
        if "default" not in student.option2:
            preferred_activity_text += f"{student.option2}"

        # put it all into the body
        body += f"{student.name}: \n"
        if contact_method_id != "":
            body += f"Contact information: {contact_method_id}\n"
        else:
            body += f"Contact information: {student.schoolEmail}\n"
        body += f"{sync_text}\n"
        #body += f"{meeting_time_text}"
        if preferred_activity_text != "":
            body += f"Prefers to {preferred_activity_text.lower()}\n"
        body += "\n"
    return body

def preferredLang(student_list: list):
    """function to check if everyone has the same lang pref
    If consensus, use that language
    no consensus, use English default
    return back the string of the language to use
    Args:
        student_list (list): list of student objects
    """
    consensus_lang = student_list[0].language
    for student in student_list:
        if student.language != consensus_lang:
            consensus_lang = "English"
    return consensus_lang

def preferredContactMethod(student_list: list):
    """
    checks to see if everyone has the same preferred contact method
    return the preferred contact method (canvas group if no matches) 
    """
    contact_arr = [0, 0, 0, 0]
    num_students = len(student_list)
    for student in student_list:
        contact_arr += np.array(student.contactPreference)

    if contact_arr[0] == num_students:
        return "discord"
    elif contact_arr[1] == num_students:
        return "phone number"
    elif contact_arr[2] == num_students:
        return "email"
    return "canvas groups"

def generalInformationText(student_list: list, contact_method: str):
    """
    the general information text for each study group
    this includes the names of the members, preferred contact method (says canvas group if no matches), and the free response.
    """
    general_info_text = ""
    names_text = ""
    free_response_text = ""

    for student in range(len(student_list)):
        if student_list[student].freeResponse != "":        
            free_response_text += f"{student_list[student].freeResponse}, "
        if student == len(student_list)-1:
            free_response_text = free_response_text[:-2]
            names_text += f"and {student_list[student].name}"
        else:
            names_text += f"{student_list[student].name}, "

    meeting_times_list = meetingTimesList(student_list)
    meetingTable(meeting_times_list)

    lang = preferredLang(student_list)

    general_info_text += f"This week, your group members are {names_text}.\n"
    if contact_method == "canvas groups":
        general_info_text += f"Please check your canvas groups to contact them.\n"
    else:
        general_info_text += f"You all prefer to meet via {contact_method}.\n"
    general_info_text += f"Some things you and your group memebers would like to do together are {free_response_text}.\n"
    general_info_text +=f"Primary Language for Communication: {lang}\n"
    return general_info_text

def meetingTimesList(student_list: list):
    """
    return a list of lists of when people are free
    each row of the list will be the list of TIMES people are free that DAY
    there are 6 times total, so 6 rows
    """
    meeting_time_list = [[], [], [], [], [], []]

    time_names = ["Midnight - 4AM", "4AM - 8AM", "8AM - Noon", "Noon -  4PM", "4PM - 8PM", "8PM - Midnight"]

    for time in range(0,6):
        student_times = ["", "", "", "", "", "", ""]
        for day in range(0,7):
            for student_num in range(0, len(student_list)):
                student = student_list[student_num]
                if student.meetingTimes[day][time] == 1:
                    student_times[day] += student.name
                    if student_num != len(student_list) - 1:
                        student_times[day] += "\n"
                    
        student_times.insert(0, time_names[time])
        meeting_time_list[time] = student_times
    return meeting_time_list


def meetingTable(times: list):
    """update the table.txt to the information from list using tablulate library
    Args:
        times (list): list of list of TIMES of names of students who are available
        note: times[0] is all the availibilites of students from Midnight to 4am
    """
    col_names = ["Times", "Sun", "Mon", "Tues", "Wed", "Thur", "Fri", "Sat"]
    table = tabulate([times[0], times[1], times[2], times[3], times[4], times[5]], col_names, tablefmt="grid")
    with open('table.txt', 'w') as w:
        w.write(str(table))
    return
   

def getEmails(student_list: list):
    """
    Gets all the emails from the student objects
    """
    email_arr = []
    for i in range(len(student_list)):
        email_arr.append(student_list[i].schoolEmail)
    return email_arr