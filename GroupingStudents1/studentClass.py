#!/usr/bin/env python3
# this is a class containing student information
class Student:
    #Personal data
    idNum = 0
    name = "default_name"
    firstName = "default_firstName"
    lastName = "default_lastName" 
    schoolEmail = "default@gmail.com"
    
    #Pronouns
    pronouns = "default/defaults" #string representing the pronoun
    preferSame = 1 #does the person prefer someone of their same gender.

    #Meet the times (starting [sunday] [midnight])
    meetingTimes = [[False, False, False, False, False, False],[False, False, False, False, False, False],[False, False, False, False, False, False],[False, False, False, False, False, False],[False, False, False, False, False, False],[False, False, False, False, False, False], [False, False, False, False, False, False]]
    preferAsy = 0 # 3 values, 0 = sync, 1= no preference, 2=async

    #Contact Infonrmation
    contactPreference = [False, False, False, True]  #Discord, Phone Number, Email, Canvas Groups 0 = no, 1= no preference, 2= yes
    contactInformation = ["defaultDiscordName#2424", "(000) 000-0000", "deafultEmail@gmail.com"]

    #Preferred Leader or Follower
    preferLeader = False

    #Country of Origin if US then false?
    countryOfOrigin = "United States of America"
    preferCountry = False

    # international student preference
    international = 0  
         
    #Language Preference
    language = "English"
    
    #Preffered Stuff to Do
    option1 = "default"
    option2 = "default"
    freeResponse = "default"

    #Priority
    priorityList = ["default", "default", "default", "default", "default"]

    #confidence
    confidence = "default"
    
    def __init__(self, idNumInput = 0, nameInput = "default_name", emailInput = "default_email", firstNameInput = "default_firstName", lastNameInput = "default_lastName"):
        self.name = nameInput
        self.idNum = idNumInput
        self.schoolEmail = emailInput
        self.pronouns = "default/defaults"
        self.preferSame = 1
        self.meetingTimes = [[False, False, False, False, False, False],[False, False, False, False, False, False],[False, False, False, False, False, False],[False, False, False, False, False, False],[False, False, False, False, False, False],[False, False, False, False, False, False], [False, False, False, False, False, False]]
        self.preferAsy = 0
        self.contactPreference = [False, False, False, True]
        self.contactInformation = ["defaultDiscordName#2424", "(000) 000-0000", "deafultEmail@gmail.com"]
        self.preferLeader = False
        self.international = 0
        self.language = "English"
        self.option1 = "default"
        self.option2 = "default"
        self.freeResponse = "default"
        self.priorityList = ["default", "default", "default", "default", "default"]
        self.confidence = "default"
        self.firstName = firstNameInput
        self.lastName = lastNameInput
    
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
        fullString += "\npreferLeader: " + str(self.preferLeader) + " international: " + str(self.international) +" language: " + self.language + " option1: " + self.option1 + " option2: " + self.option2 + " freeresponse: " + self.freeResponse
        fullString += "\npriorityList: "
        for value in self.priorityList:
            fullString += " " + value + ", "
        fullString += "\nconfidence: " + str(self.confidence)
        return fullString