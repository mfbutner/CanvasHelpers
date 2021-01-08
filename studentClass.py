#!/usr/bin/env python3
# this is a class containing student information
class Student:
    #Personal data
    idNum = 0 #check
    name = "default_name" #check
    schoolEmail = "default@gmail.com"
    
    #Pronouns
    pronouns = "default/defaults" #check
    otherPronouns = "NA" #check
    preferSame = 1 #check

    #Meet the times
    meetingTimes = [[1, 1, 1, 1, 1, 1],[1, 1, 1, 1, 1, 1],[1, 1, 1, 1, 1, 1],[1, 1, 1, 1, 1, 1],[1, 1, 1, 1, 1, 1],[1, 1, 1, 1, 1, 1]]
    preferAsy = 0

    #Contact Infonrmation
    contactPreference = [0, 0, 0, 1]  #Discord, Phone Number, Email, Canvas Groups
    contactInformation = ["defaultDiscordName#2424", "(000) 000-0000", "deafultEmail@gmail.com"]

    #Preferred Leader or Follower
    preferLeader = 0

    #Country of Origin
    countryOfOrigin = "United States of America"
    preferCountry = 0
         
    #Language Preference
    language = "English"
    preferLanguage = 0
    
    #Preffered Stuff to Do
    option1 = "default"
    option2 = "default"
    freeResponse = "default"
    
    def __init__(self, idNumInput = 0, nameInput = "default_name", emailInput = "default_email"):
        self.name = nameInput
        self.idNum = idNumInput
        self.schoolEmail = emailInput
