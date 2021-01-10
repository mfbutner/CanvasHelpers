#!/usr/bin/env python3
from studentClass import Student
# seed the pseudorandom number generator
from random import seed
from random import random
# seed random number generator
seed(1)

def createStudents():
    listOfStudents = list()
    for i in range(0, (45*5)):
        temp = Student()

        x = random()
        if x< 0.01 :
            temp.pronouns = "They/them"
        elif x< 0.3:
            temp.pronouns = "She/Hers"
        elif x < 0.95:
            temp.pronouns = "He/him/his"
        else:
            temp.pronouns = "Prefer not to say"

        x = random()
        if x > 0.5:
            preferSame = True

        for i in range(7):
            for j in range(6):
                x = random()
                if x < 0.75:
                    temp.meetingTimes[i][j] = 0

        x = random()
        if x > 0.5:
            temp.preferAsy = True

        x = random()
        if x > 0.9:
            temp.preferLeader = True

        x = random()
        if x > 0.6 and x <0.80:
            temp.countryOfOrigin = "China"
        elif x > 0.8:
            temp.countryOfOrigin = "India"
        elif x > 0.9:
            temp.countryOfOrigin = "Canada"
        else:
            temp.countryOfOrigin = "Ghana"

        y = random()
        if x > 0.6 and y >0.4:
            temp.preferCountry = True

        z = random()
        if temp.countryOfOrigin == "China":
            if y > 0.8:
                temp.language = "Mandarin"
            else:
                temp.language = "Cantonese"
            if z > 0.3:
                temp.preferLanguage = True
        elif temp.countryOfOrigin == "India":
            if y > 0.8:
                temp.language = "Hindi"
            else:
                temp.language = "Pakistani" 
            if z > 0.3:
                temp.preferLanguage = True 
        elif temp.countryOfOrigin == "Canada":
            if y > 0.6:
                temp.language = "English"
            if z > 0.3:
                temp.preferLanguage = True 
        elif temp.countryOfOrigin == "Ghana":
            if y > 0.6:
                temp.language = "Akan"
            if z > 0.3:
                temp.preferLanguage = True 
        else:
            if z>.8:
                temp.language = "Spanish"
                temp.preferLanguage = True

        x = random()
        y = random()
        if(x>0.25):
            temp.option1 = "Play a game"
        elif(x>0.5):
            temp.option1 = "Talk about the class"
        elif(x>0.75):
            temp.option1 = "Talk about something that is njot the class"
        else:
            temp.option1 = "Watch a show/movie"

        if(y>0.25):
            temp.option2 = "Play a game"
        elif(y>0.5):
            temp.option2 = "Talk about the class"
        elif(y>0.75):
            temp.option2 = "Talk about something that is njot the class"
        else:
            temp.option2 = "Watch a show/movie"
        
    return listOfStudents


                    

