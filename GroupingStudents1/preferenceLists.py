from studentClass import Student
from scoringFunc import scoreOneByOne
from scoringFunc import scoreTwoByTwo
from scoringFunc import scoreGroupByOne
from scoringFunc import scoreOneByGroup


#Create a dictionary of students, where each student corresponds to a list of students in order of preference
def preferenceSymmetricalSort(listStudents: list, typeSort: str, matchedBefore: dict):
    dictStudentReturn = dict()

    #First select the student or group you are scoring
    for student1 in listStudents:
        #Intialize an empty array 
        tempArray = [] 

        #Rotate through all the other students in the list
        for student2 in listStudents:

            #We need to differentiate between student and student-student pairs
            if typeSort == "OneByOne":
                #Don't guage students by themselves
                if student1.idNum != student2.idNum:
                    tempArray.append([str(student2.idNum), scoreOneByOne(student1,student2, matchedBefore)])

            elif typeSort == "TwoByTwo":
                #Don't guage student pairs by themselves
                if student1[0].idNum !=  student2[0].idNum:
                    tempArray.append([str(student2[0].idNum), scoreTwoByTwo(student1, student2, matchedBefore)])

        #Now sort the list with max score first
        sorted(tempArray, key = lambda score: score[1], reverse = True)
        
        #Take only the ids
        tempArray = [student[0] for student in tempArray]

        if typeSort == "OneByOne":
            dictStudentReturn[str(student1.idNum)] = tempArray
        elif typeSort == "TwoByTwo":
            dictStudentReturn[str(student1[0].idNum)] = tempArray
        else:
            print("Error, shoud not get here, in preferenceSymmetrical")

    return dictStudentReturn
        
#Create a dictionary of students, where each student/student Group Ranks another
#listStudent1: the list of students judging
#listStudent2: the list of the list of students to be judged
def preferenceAsymmetricalSort(listStudents1:list , listStudents2: list, typeSort: str, matchBefore: dict):
    #Create an empty dictionary to fill
    dictStudent = dict()
    
    #First select the student or group you are scoring
    for student1 in listStudents1:
        #Intialize an empty array 
        tempArray = [] 
        for student2List in listStudents2:
            if typeSort == "OneByGroup":
                tempArray.append([str(student2List.idNum), scoreOneByGroup(student2List, student1, matchBefore)])
            elif typeSort == "GroupByOne":
                tempArray.append([str(student2List[0].idNum), scoreGroupByOne(student1, student2List, matchBefore)])    

        #Now sort the list with max score first
        sorted(tempArray, key = lambda score: score[1], reverse = True)
        
        #Take only the ids of the first student of the sets
        tempArray = [student[0] for student in tempArray]
        if typeSort == "OneByGroup":
            dictStudent[str(student1[0].idNum)] = tempArray
        elif typeSort == "GroupByOne":
            dictStudent[str(student1.idNum)] = tempArray
        else:
            print("Error, shoud not get here, in preferenceSymmetrical")

    return dictStudent

    
