from StableGrouping.parsing.studentClass import Student

# Return levels of matching preference- From 2 (best) to 0 (worst)
def matchPartner(student1: Student, student2: Student):
    if student1.partner == student2.name:
        if student1.partner_email == student2.schoolEmail:
            return 2
        return 1
    return 0

#Return true if the people wanted eachother
def matchSymPartner(student1: Student, student2: Student):
    return matchPartner(student1, student2) > 0 and matchPartner(student2, student1) > 0

#return True if the two second student matches the first student's preferences
def matchInternational(student1: Student, student2: Student):

    #If the first student has no preference or is not an international student, then the second student does not matter
    if student1.international == 1 or student1.international == 0:
        return True

    #The first student is an internatinal student who prefers another international student
    if student1.international == 2:
        if student2.international == 2 or student2.international == 1:
        #The second student is an international student, so the first student likes them
            return True

    #Otherwise, the first student is not satisfied
    return False


#If the two students prefer the same activity, return true
def matchActivity(student1: Student, student2: Student):
    return student1.activity_choice == student2.activity_choice


#If the two students overlap in time slots at all, return true
def matchMeetingTimeSpecific(student1: Student, student2: Student):
    for i in range(7):
        for j in range(6):
            #If at any point, both students are right at the same time, return True
            if student1.meeting_times[i][j] and student2.meeting_times[i][j]:
                return True
    #If each time slot fails, the students don't overlap at all
    return False

#If the first student's preferences are fulfilled by the second return true, else return false
def matchTime(student1: Student, student2: Student):
    #The first student would prefer to be sync
    if student1.prefer_async == 0:
        #The second student also prefers to be sync, or does not care
        if student2.prefer_async == 0 or student2.prefer_async == 1:
            #If they overlap in time, then they are compatible
            return matchMeetingTimeSpecific(student1, student2)
        #The second student does not want to be synch, they are incompatible
        elif student2.prefer_async == 2:
            return False

    #The first student has no preference
    elif student1.prefer_async == 1:
        #If the second student doesn't care or prefersAsy
        if student2.prefer_async == 1 or student2.prefer_async == 2:
            #Then they can choose to be asynch together
            return True
        #If the second student is synch
        elif student2.prefer_async == 0:
            #The second student wants to synch, so they only match if they match in time
            return matchMeetingTimeSpecific(student1, student2)

    #The first student would prefer to be asynch
    elif student1.prefer_async == 2:
        #If the second student doesn't care or prefersAsy
        if student2.prefer_async == 1 or student2.prefer_async == 2:
            #Then they can choose to be asynch together
            return True
        #If the second student is synch, they are incompatible
        elif student2.prefer_async == 0:
            return False

#Return true if the two have the same values as leader
def matchLead(student1: Student, student2: Student):
    return student1.prefer_leader == student2.prefer_leader

#Return true if they speak the same language
def matchLanguage(student1: Student, student2: Student):
    return student1.language == student2.language

#Return true if the second student matches the first student's preferences
def matchGender(student1: Student, student2: Student):
    #The first student prefers same gender:
    if student1.prefer_same == 2:
        if student1.pronouns == student2.pronouns:
            return True
        else:
            return False

    #The first student does not have a preference
    elif student1.prefer_same == 1:
        return True

    #The first student prefers a different gender
    elif student1.prefer_same == 0:
        if student1.pronouns != student2.pronouns:
            return True
        else:
            return False

    #The first student has failed to find a good match
    return False

#Return true if two students match in skill (NOTE: you probaby dont want them too)
def matchSkill(student1: Student, student2: Student):
    return student1.confidence == student2.confidence

#Checks if the student matches with anyone in the group to meet their preference
def matchWithinGroup(student: Student, group: list, matchType:str):
    for studentCompare in group:
        #We don't want to use the student against themselves
        if studentCompare != student:
            #If it works for anyone, we return True
            if matchType == "Gender":
                if matchGender(student, studentCompare):
                    return True
            elif matchType == "Language":
                if matchLanguage(student, studentCompare):
                    return True
            elif matchType == "International":
                if matchLanguage(student, studentCompare):
                    return True
            else:
                print("Issue: attempt to list through with an incompatible preference type")

    #It failed for everyone, so we return False
    return False


