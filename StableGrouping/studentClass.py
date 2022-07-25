#!/usr/bin/env python3
# this is a class containing student information
class Student:

    def __init__(self):
        # Student identification information
        self.name = "default_name"
        self.id_num = 0
        self.schoolEmail = "default_email"
        self.firstName = "default_firstName"
        self.lastName = "default_lastName"

        # Student preferred pronouns
        self.pronouns = "default/defaults"
        # If student prefers the same pronouns
        # 0 - Not same pronouns 1 - No preference 2 - Prefer the same pronouns
        self.prefer_same = 1

        # Student available meeting times in PST
        # [Day][time] in 4 hour in hr intervals from 12am to 12am starting Sunday
        self.meeting_times = [[False, False, False, False, False, False],
                              [False, False, False, False, False, False],
                              [False, False, False, False, False, False],
                              [False, False, False, False, False, False],
                              [False, False, False, False, False, False],
                              [False, False, False, False, False, False],
                              [False, False, False, False, False, False]]

        # Does the student prefer to meet asynchronously
        # 0 - No preference 1 - Synchronous 2 - Asynchronous
        self.prefer_async = 0

        # contact preference and information
        self.contact_preference = [False, False, False, True]
        self.contact_information = ["defaultDiscordName#2424", "(000) 000-0000", "defaultEmail@gmail.com"]

        # If student prefers being the leader
        self.prefer_leader = False

        # Is the student international and would they like to be with another international student
        # 0 - not international 1 - no preference 2 - is international and would like to match
        self.international = 0

        # Language preference
        self.language = "English"

        # What the student prefers to do.
        self.activity_choice = "default"
        self.free_response = "default"

        # The what the student prioritizes in a study group most to least.
        self.priority_list = ["default", "default", "default", "default", "default"]

        # How confident the student feels (0 - 2) default is 1
        self.confidence = 1

        # partner the student wants
        self.partner = "default"

        # the email of the partner that the student wants
        self.partner_email = "default"

    def __str__(self):
        student_details = (f"Student: {self.name} ({self.lastName}, {self.firstName})\n"
                           f"ID: {self.id_num} | Email: {self.schoolEmail}\n"
                           f"Pronouns: {self.pronouns} - Prefer Same Pronouns: {self.prefer_same}\n"
                           f"  Meeting Times (Prefer Async: {self.prefer_async})")

        for week in self.meeting_times:
            student_details += "\n "
            for day in week:
                student_details += f" {str(day)} "
        student_details += "\n"

        student_details += "Contact Preferences: "
        for contact_preference in self.contact_preference:
            student_details += f" {str(contact_preference)}, "
        student_details += "\n"

        student_details += "Contact Information: "
        for contact_information in self.contact_preference:
            student_details += f" {contact_information}, "
        student_details += "\n"

        student_details += (f"Prefer Leader: {self.prefer_leader} | International: {self.international} | "
                            f"Language: {self.language} | Activity: {self.activity_choice} - {self.free_response}\n"
                            f"Confidence: {self.confidence}\n"
                            f"Priorities: ")
        for value in self.priority_list:
            student_details += f" {value}, "

        return student_details
