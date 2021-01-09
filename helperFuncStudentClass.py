#Two unfinished func:
#groupbefore- returns true if two people have been in a group before
#timeMatch - if one person at least in a group wants to be synch, they have another synch or no pref person who matches them in at least one time slot, return true OR  if both are asynch or no pref, return true
#scoreGroup - scores a quad and keeps the value as part of the class until updated
#movePair - There is a lot of repeated 4 lines of this code in match list that I was plannign to move here eventualy, may generalize to quad

#Create a pair of students, assumed to be valid
class Pair():
    student1 = Student()
    student2 = Student()
    
    def __init__(self, studentA, studentB):
        self.student1 = studentA
        self.student2 = studentB

#A set of four students, along with a "score" of how good the group is 
class Quad:
    student1 = Student()
    student2 = Student()
    student3 = Student()
    student4 = Student()
    score = 0

    def scoreGroup():
        #score the grouup goes here

    def __init__self(Pair1, Pair2):
        student1 = Pair1.student1
        student2 = Pair1.student2
        student3 = Pair2.student1
        student4 = Pair2.student2
        score = self.scoreGroup()

def groupBefore(student1, student2):
    #have to fill this in

def timeMatch(student1, student2):
    #have to fill this in

#A perfectly valid pair will pass this test
def pairFull(student1,student2):
    #if the students are the same, they fail
    if student1 == studen2:
        return False
    #if the students have been in a group before, they fail
    if not groupBefore(student1, student2):
        return False
    #if the students do not match in time, they fail
    if not timeMatch(student1, student2):
        return False
    #otherwise they pass
    return True

#A partially valid pair: they do not meet the time requirement
def pairGroup(student1,student2):
    #if they are the same student, they fail
    if student1 == student2:
        return False
    #if they were in a group before, they fail
    if not groupBefore(student1, student2):
        return False
    #otherwise they pass
    return True

#When you pull from allDontCare you need to figure out which sublist you also need to delete a student from, so that's here
def removeDontCare(student, womanDontCare, manDontCare, nonBinaryDontCare, allDontCare):
    if student.pronouns == "She/her":
        womanDontCare.remove(student)
    if student2.pronouns == "He/him/his":
        manDontCare.remove(student)
    if student2.pronouns == "They/them" or student2.pronouns == "Not Included":
        nonBinaryDontCare.remove(student)
    allDontCare.remove(student)
    return 

#There is a lot of repeated 4 lines of this code in match list that I was plannign to move here eventualy
def movePair():
    return 1
