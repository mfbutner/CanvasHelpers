#!/usr/bin/env python3
# this is a class containing student information
class Student:
    
    def __init__(self, idNumInput = 0, nameInput = "default_name", emailInput = "default_email", firstNameInput = "default_firstName", lastNameInput = "default_lastName"):
        # Student identification information
        self.name = nameInput
        self.idNum = idNumInput
        self.schoolEmail = emailInput
        self.firstName = firstNameInput
        self.lastName = lastNameInput

        # Student preferred pronouns
        self.pronouns = "default/defaults"
        # If student prefers the same pronouns
        # 0 - Not same pronouns 1 - No preference 2 - Prefer the same pronouns
        self.preferSame = 1

        # Student available meeting times in PST
        # [Day][time] in 4 hour in hr intervals from 12am to 12am starting Sunday
        self.meetingTimes = [[False, False, False, False, False, False],[False, False, False, False, False, False],[False, False, False, False, False, False],[False, False, False, False, False, False],[False, False, False, False, False, False],[False, False, False, False, False, False], [False, False, False, False, False, False]]

        # Does the student prefer to meet asynchronously
        # 0 - No preference 1 - Synchronous 2 - Asynchronous
        self.preferAsy = 0

        # contact preference and information
        self.contactPreference = [False, False, False, True]
        self.contactInformation = ["defaultDiscordName#2424", "(000) 000-0000", "deafultEmail@gmail.com"]

        # If student prefers being the leader
        self.preferLeader = False

        # Is the student international and would they like to be with anothe international student
        # 0 - not international 1 - no preference 2 - is international and would like to match
        self.international = 0

        # Language preference
        self.language = "English"

        # What the student prefers to do.
        self.option1 = "default"
        self.freeResponse = "default"

        # The what the student prioritizes in a study group most to least.
        self.priorityList = ["default", "default", "default", "default", "default"]

        # How confident the student feels (0 - 2) default is 1
        self.confidence = 1
    
    def __str__(self): 
        fullString = ""
        fullString = "Name: " + self.name + " First Name: " + self.firstName + " Last Name: " + self.lastName + " idNum: " + str(self.idNum) + " schoolEmail: " + self.schoolEmail
        fullString += " Pronouns: " + self.pronouns + " preferSame: " + str(self.preferSame) + "\n"
        fullString += " meetingTimes\n"
        for value in self.meetingTimes:
            for time in value:
                fullString += " " + str(time) + " "
            fullString += "\n"
        fullString += " preferAsy: " + str(self.preferAsy)
        fullString += "\ncontactPreference: "
        for value in self.contactPreference:
            fullString += " " + str(value) + ", "
        fullString += "\nContactInformation:"
        for value in self.contactInformation:
            fullString += " " + value + ", "
        fullString += "\npreferLeader: " + str(self.preferLeader) + " international: " + str(self.international) +" language: " + self.language + " option1: " + self.option1 + " freeresponse: " + self.freeResponse
        fullString += "\npriorityList: "
        for value in self.priorityList:
            fullString += " " + value + ", "
        fullString += "\nconfidence: " + str(self.confidence)
        return fullString