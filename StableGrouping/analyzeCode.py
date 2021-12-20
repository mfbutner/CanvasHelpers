from studentClass import Student
from matchingFunc import matchGender
from matchingFunc import matchSkill
from matchingFunc import matchLanguage
from matchingFunc import matchTime
from matchingFunc import matchActivity
from matchingFunc import matchInternational
from scoringFunc import scoreAtLeastOneConfidenceLevel
from checkValidGroup import isValidGroup

#Analyze the groups on set criteria
def gradeGroups(groups: list, matchBefore: dict):

    #Count the number of students who did or did not take the survey
    defaultStudents = 0  
    studentsTakeSurvey = 0 

    #Count the number of students who succesfully got a gender match out of the ones who wanted it
    studentsGenderMatch = 0  
    studentsWantGenderMatch = 0 

    #Count the number of students who wanted asynch/synch and got a match in their group
    studentsWantTime = 0 
    studentsGotTime = 0 

    #Count the number of groups and the valid groups
    numGroups = 0 
    numValidGroups = 0 

    #Count the number of groups with a leader personality
    groupsGotLeader = 0  

    #Count the number of students who wanted another international student and got it
    studentsWantInternational = 0 
    studentsGotInternational = 0 

    #Count all the students who got their preferred language
    studentsGotLanguage = 0 

    #Count all the students who got their preferred activity
    studentsGotOption = 0 

    #Count which priority the students got first
    #If both second choice and first are met on one student, only firstChoice increases
    studentGotChoice = [0, 0, 0, 0, 0, 0]
    
    #Count the number of groups where there are people of multiple confidence levels
    numGroupsMixConfidence = 0  

    #Iterate through each group
    for group in groups:
        #Increment the number of overall Groups
        numGroups = numGroups + 1

        #increment valid group if the groups are valid
        if isValidGroup(matchBefore, group) == 0:
            numValidGroups = numValidGroups + 1

        #increment confidenceLevels if group has a mixture of high to low confidence
        if scoreAtLeastOneConfidenceLevel(group) > 0:
            numGroupsMixConfidence = numGroupsMixConfidence + 1

        #a flag that becomes true if anyone in the group is a leader
        flagLeader = False
        
        #The others are by person
        for person in group:
            #Flags to control what the person does and does not get
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

            #if anyone in the group is a leader, the whole group gets a leader
            if person.preferLeader == True:
                flagLeader = True

            #check this person based on the rest of the group
            for person2 in group:
                #Don't check a person against themself
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

            #Only count the person if the person wanted to match on gender
            if person.preferSame != 1:
                studentsWantGenderMatch = studentsWantGenderMatch + 1
                if flagGender:
                    studentsGenderMatch = studentsGenderMatch + 1
            
            #Only count the person if the person wanted to match on time
            if person.preferAsy != 1:
                studentsWantTime = studentsWantTime + 1
                if flagTime:
                    studentsGotTime = studentsGotTime + 1

            #Only count the person if the person wanted to match on international
            if person.international == 2:
                studentsWantInternational = studentsWantInternational + 1
                if flagInternational:
                    studentsGotInternational = studentsGotInternational + 1

            #The student matched at least one other person on language
            if flagLanguage:
                studentsGotLanguage = studentsGotLanguage + 1

            #The student matched at least one other person on activity
            if flagOption:
                studentsGotOption = studentsGotOption + 1

            #Find the highest priority that the student managed to get
            for i in range(5):
                #If at any point, they default, ignore the rest of their opinions
                if person.priorityList[i] == "default":
                    break
                elif person.priorityList[i] == "Gender":
                    if flagGender:
                        studentGotChoice[i] = studentGotChoice[i]+1
                        break
                elif person.priorityList[i] == "International":
                    if flagInternational:
                        studentGotChoice[i] = studentGotChoice[i]+1
                        break
                elif person.priorityList[i] == "Language":
                    if flagLanguage:
                        studentGotChoice[i] = studentGotChoice[i]+1
                        break
                elif person.priorityList[i] == "What They Want to Do":
                    if flagOption:
                        studentGotChoice[i] = studentGotChoice[i]+1
                        break
                elif person.priorityList[i] == "Matching Time to Meet":
                    if flagTime:
                        studentGotChoice[i] = studentGotChoice[i]+1
                        break
        
        #If any student flagged as a leader, the group has a leader
        if flagLeader:
            groupsGotLeader = groupsGotLeader + 1

        
            
    
    print(studentsTakeSurvey, " of students took the survey while ", defaultStudents,  " did not take it.")
    print("Group who got leader: "+ str((100 * (groupsGotLeader/numGroups))) + "%")   
    print("Group who got confidence: "+ str((100 * (numGroupsMixConfidence/numGroups))) + "%") 
    print("Students who got gender match: "+ str((100 * (studentsGenderMatch/studentsWantGenderMatch))) + "%")
    print("Students who got time: "+ str((100 * (studentsGotTime/studentsWantTime))) + "%")
    print("Students who got international: "+ str((100 * (studentsGotInternational/studentsWantInternational))) + "%")     
    print("Students who got language: " + str((100*(studentsGotLanguage/studentsTakeSurvey))) + "%")
    print("Students who got activity: "+ str((100*(studentsGotOption/studentsTakeSurvey)))+"%")
    print()
    print("First choice: ", studentGotChoice[0])
    print("Second choice: ", studentGotChoice[1])
    print("Third choice: ", studentGotChoice[2])
    print("Fourth choice: ", studentGotChoice[3])
    print("Fifth choice: ", studentGotChoice[4])

    studentGotNoChoice = studentsTakeSurvey - sum(studentGotChoice)

    print("\nGroups that are valid: "+ str(numValidGroups/numGroups * 100) + "%")
    print()
