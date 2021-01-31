
from studentClass import Student
from matchingFunc import matchGender
from matchingFunc import matchSkill
from matchingFunc import matchLanguage
from matchingFunc import matchTime
from matchingFunc import matchActivity
from matchingFunc import matchInternational
from scoringFunc import scoreAtLeastOneConfidenceLevel
from checkValidGroup import isValidGroup

def gradeGroups(groups: list, matchBefore: dict):

    defaultStudents = 0  #
    studentsTakeSurvey = 0 #

    studentsGenderMatch = 0  #
    studentsWantGenderMatch = 0 #

    studentsWantTime = 0 #
    studentsGotTime = 0 #

    numGroups = 0 #
    numValidGroups = 0 #
    groupsGotLeader = 0  #

    studentsWantInternational = 0 #
    studentsGotInternational = 0 #

    studentsGotLanguage = 0 #

    studentsGotOption = 0 #

    studentGotFirstChoice = 0
    studentGotSecondChoice = 0
    studentGotThirdChoice = 0
    studentGotFourthChoice = 0
    studentGotFifthChoice = 0
    studentGotNoChoice = 0
    
    numGroupsMixConfidence = 0  #

    for group in groups:
        numGroups = numGroups + 1

        if isValidGroup(matchBefore, group):
            numValidGroups = numValidGroups + 1

        #Leader
        flagLeader = False
        
        #The others are by person
        for person in group:
            flagGender = False
            flagTime = False
            flagInternational = False
            flagLanguage = False
            flagOption = False
            
            #Default students should not affect stats
            if person.pronouns == "default/defaults":
                defaultStudents = defaultStudents + 1
                continue
            else:
                studentsTakeSurvey = studentsTakeSurvey + 1


            if person.preferLeader == True:
                flagLeader = True

            for person2 in group:
                if person != person2:
                    #Gender
                    if matchGender(person, person2):
                        flagGender = True

                    #Time
                    if matchTime(person, person2):
                        flagTime = True

                    #International
                    if matchInternational(person, person2):
                        flagInternational = True

                    #Language
                    if person.language == person2.language:
                        flagLanguage = True

                    #Option
                    if person.option1 == person2.option1:
                        flagOption = True

            if person.preferSame != 1:
                studentsWantGenderMatch = studentsWantGenderMatch + 1
                if flagGender:
                    studentsGenderMatch = studentsGenderMatch + 1
                    
            if person.preferAsy != 1:
                studentsWantTime = studentsWantTime + 1
                if flagTime:
                    studentsGotTime = studentsGotTime + 1

            if person.international == 2:
                studentsWantInternational = studentsWantInternational + 1
                if flagInternational:
                    studentsGotInternational = studentsGotInternational + 1

            if flagLanguage:
                studentsGotLanguage = studentsGotLanguage + 1

            if flagOption:
                studentsGotOption = studentsGotOption + 1

            for i in range(5):
                if person.priorityList[i] == "default":
                    break
                elif person.priorityList[i] == "Gender":
                    if flagGender:
                        if i == 0:
                            studentGotFirstChoice = studentGotFirstChoice + 1
                            break
                        elif i == 1:
                            studentGotSecondChoice = studentGotSecondChoice + 1
                            break
                        elif i == 2:
                            studentGotThirdChoice = studentGotThirdChoice + 1
                            break
                        elif i == 3:
                            studentGotFourthChoice = studentGotFourthChoice + 1
                            break
                        elif i == 4:
                            studentGotFifthChoice = studentGotFifthChoice + 1
                            break
                elif person.priorityList[i] == "International":
                    if flagInternational:
                        if i == 0:
                            studentGotFirstChoice = studentGotFirstChoice + 1
                            break
                        elif i == 1:
                            studentGotSecondChoice = studentGotSecondChoice + 1
                            break
                        elif i == 2:
                            studentGotThirdChoice = studentGotThirdChoice + 1
                            break
                        elif i == 3:
                            studentGotFourthChoice = studentGotFourthChoice + 1
                            break
                        elif i == 4:
                            studentGotFifthChoice = studentGotFifthChoice + 1
                            break
                elif person.priorityList[i] == "Language":
                    if flagLanguage:
                        if i == 0:
                            studentGotFirstChoice = studentGotFirstChoice + 1
                            break
                        elif i == 1:
                            studentGotSecondChoice = studentGotSecondChoice + 1
                            break
                        elif i == 2:
                            studentGotThirdChoice = studentGotThirdChoice + 1
                            break
                        elif i == 3:
                            studentGotFourthChoice = studentGotFourthChoice + 1
                            break
                        elif i == 4:
                            studentGotFifthChoice = studentGotFifthChoice + 1
                            break
                elif person.priorityList[i] == "What They Want to Do":
                    if flagOption:
                        if i == 0:
                            studentGotFirstChoice = studentGotFirstChoice + 1
                            break
                        elif i == 1:
                            studentGotSecondChoice = studentGotSecondChoice + 1
                            break
                        elif i == 2:
                            studentGotThirdChoice = studentGotThirdChoice + 1
                            break
                        elif i == 3:
                            studentGotFourthChoice = studentGotFourthChoice + 1
                            break
                        elif i == 4:
                            studentGotFifthChoice = studentGotFifthChoice + 1
                            break
                elif person.priorityList[i] == "Matching Time to Meet":
                    if flagTime:
                        if i == 0:
                            studentGotFirstChoice = studentGotFirstChoice + 1
                            break
                        elif i == 1:
                            studentGotSecondChoice = studentGotSecondChoice + 1
                            break
                        elif i == 2:
                            studentGotThirdChoice = studentGotThirdChoice + 1
                            break
                        elif i == 3:
                            studentGotFourthChoice = studentGotFourthChoice + 1
                            break
                        elif i == 4:
                            studentGotFifthChoice = studentGotFifthChoice + 1
                            break

        if flagLeader:
            groupsGotLeader = groupsGotLeader + 1

        if scoreAtLeastOneConfidenceLevel(group) > 0:
            numGroupsMixConfidence = numGroupsMixConfidence + 1
            
    
    print(studentsTakeSurvey, " of students took the survey while ", defaultStudents,  " did not take it.")
    print("Group who got leader: "+ str((100 * (groupsGotLeader/numGroups))) + "%")   
    print("Group who got confidence: "+ str((100 * (numGroupsMixConfidence/numGroups))) + "%") 
    print("Students who got gender match: "+ str((100 * (studentsGenderMatch/studentsWantGenderMatch))) + "%")
    print("Students who got time: "+ str((100 * (studentsGotTime/studentsWantTime))) + "%")
    print("Students who got international: "+ str((100 * (studentsGotInternational/studentsWantInternational))) + "%")     
    print("Students who got language: " + str((100*(studentsGotLanguage/studentsTakeSurvey))) + "%")
    print("Students who got activity: "+ str((100*(studentsGotOption/studentsTakeSurvey)))+"%")
    print()
    print("First choice: ", studentGotFirstChoice)
    print("Second choice: ", studentGotSecondChoice)
    print("Third choice: ", studentGotThirdChoice)
    print("Fourth choice: ", studentGotFourthChoice)
    print("Fifth choice: ", studentGotFifthChoice)

    studentGotNoChoice = studentsTakeSurvey - studentGotFirstChoice - studentGotSecondChoice - studentGotThirdChoice - studentGotFourthChoice - studentGotFifthChoice
    print("Last choice: ", studentGotNoChoice)

    print("\nGroups that are valid: "+ str(numValidGroups/numGroups * 100) + "%")
    print()
