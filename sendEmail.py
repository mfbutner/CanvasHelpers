"""This file is for sending the emails (python3)
    last line is: sendMessage(group_list, class_name, study_group_number)
    group_list should be a list of list of student objects
    class_name is the name of the class (ecs 154a or ecs 50)
    study_group_number is the number of that week's study group (1-5)
    """

# import system variables
# in order to send the messages, need to log into an email
# i put the password and email in environment variables
import os
sender_email = os.environ.get('sender_email')
sender_email_password = os.environ.get('sender_email_password')

# import numpy
import numpy as np

# import smtplib for the actual sending function
import smtplib

# import email module from email library
from email.message import EmailMessage

def getBody(student_list):
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
        sync_text = ("Prefers to meet synchronously on " if sync==0 else "Has no preference meeting synchronously or asynchronously on " if sync==1 else "Prefers to meet asynchronously on ")
        # put in everyone's preferred meeting times (specified for each person)
        meeting_time_text = meetingTimesText(student)
        # put in preferred activities (specified for each person)
        preferred_activity_text = f"{student.option1} and {student.option2}"

        # put it all into the body
        body += f"{student.name}: \n"
        if contact_method_id != "":
            body += f"Contact information: {contact_method_id}\n"
        body += f"{sync_text}\n"
        body += f"{meeting_time_text}"
        body += f"Prefers to {preferred_activity_text.lower()}\n"
        body += "\n"
    return body

def preferredContactMethod(student_list):
    """
    checks to see if everyone has the same preferred contact method
    #return the preferred contact method (canvas group if no matches) 
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

def generalInformationText(student_list, contact_method):
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

    general_info_text += f"This week, your group members are {names_text}.\n"
    general_info_text += f"You all prefer to meet via {contact_method}.\n"
    general_info_text += f"Some things you and your group memebers would like to do together are {free_response_text}.\n"
    return general_info_text

def meetingTimesText(student):
    """
    return the text for the meeting time of the student
    """
    meeting_time_text = ""
    day_names = ["Mondays", "Tuesdays", "Wednesdays", "Thursdays,", "Fridays", "Saturdays", "Sundays"]
    time_names = ["After midnight (12-4 AM)", "Early Mornings (4-8 AM)",
    "Mornings (8-12 PM)","Afternoons (12-4 PM)","Evenings (4-8 PM)","Nighttime (8 PM-12 AM)"]
    
    for day in range(len(student.meetingTimes)):

        day_text = f"{day_names[day]}: "
        time_text = ""

        for time in range(len(student.meetingTimes[day])):
            if student.meetingTimes[day][time] == 1:
                time_text += f" {time_names[time]},"

        if time_text != "":
            time_text = time_text[:-1]
            meeting_time_text += "   " + day_text + time_text + "\n"

    return meeting_time_text


def getEmails(student_list):
    """
    Gets all the emails from the student objects
    """
    email_arr = []
    for i in range(len(student_list)):
        email_arr.append(student_list[i].schoolEmail)
    return email_arr

def makeMessage(student_list, class_name, study_group_number):
    """
    Make the the email message using the EmailMessage() class
    return the msg
    """
    email_arr = getEmails(student_list)
    body = getBody(student_list)

    msg = EmailMessage()
    msg['Subject'] = class_name + " " + study_group_number
    msg['From'] = sender_email
    msg['To'] = ", ".join(email_arr)
    msg.set_content(body)
    return msg
    

def sendGroupMessage(student_list, class_name, study_group_number):
    """
    This function sends the email to everyone in the group
    """

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(sender_email, sender_email_password)
        
        msg = makeMessage(student_list, class_name, study_group_number)
                
        smtp.send_message(msg)
    
    return

def sendMessage(group_list, class_name, study_group_number):
    """
    for every group in the group_list, send a message for each student per group
    """
    for group in range(len(group_list)):
        sendGroupMessage(group_list[group], class_name, study_group_number)



group_list = # place a list of list of student objects here
class_name = "ECS" # change to ecs 50 or ecs 154
study_group_number = "1" # change the study group number here

sendMessage(group_list, class_name, study_group_number)

