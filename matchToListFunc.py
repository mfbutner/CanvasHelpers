#Match List Cares
def matchListCare(listToMatch, listToMatchDontCare, allDontCare, pairs, didNotTakeSurvey):
    #try to create all the perfect matches you can first
    for student1 in listToMatch:
        for student2 in listToMatch:
            if pairFull(student1, student2):
                pairs.append(Pair(student1, student2))
                listToMatch.remove(student1)
                listToMatchDontCare.remove(student2)
                break

    #All the perfect matches are taken out, so try to match now the remainder
    for student1 in listToMatch:
        found = False
        
        #if the match is not found, check for a possible match in the listToMatchDontCare
        for student2 in listToMatchDontCare:
            if pairFull(student1, student2):
                found = True                                    #a match has been found and is placed in pairs
                pairs.append(Pair(student1, student2))          #The students are removed from the singles lists
                listToMatchCare.remove(student1)
                listToMatchDontCare.remove(student2)
                allDontCare.remove(student2)
                break                                           #no longer need to look for this student1's match

        #if the match is not found still, relax the checking to only looking for two students who have not shared a group and match gender
        if not found:
            for student2 in listToMatch:
                if pairGroup(student1, student2):
                    found = True
                    pairs.append(Pair(student1, student2))
                    listToMatch.remove(student1)
                    listToMatch.remove(student2)
                    break

        #if the match is not found still, relax the checking to only looking for two students who have not shared a group, where the second is in Dont Care but in the same gender
        if not found:
            for student2 in listToMatchDontCare:
                if pairGroup(student1, student2):
                    found = True
                    pairs.append(Pair(student1, student2))
                    listToMatch.remove(student1)
                    listToMatchDontCare.remove(student2)
                    allDontCare.remove(student2)
                    break

        #If still not found, pull a match from the largest all dont care who is valid in time and has not shared a group
        if not found:
            for student2 in allDontCare:
                if pairFull(student1, student2):
                    found = True
                    pairs.append(Pair(student1, student2))
                    listToMatch.remove(student1)
                    removeDontCare(student2, womanDontCare, manDontCare, listToMatchDontCare, allDontCare)
                    break

        #If still not found, pull a match from the largest all dont care without time requirement
        if not found:
            for student2 in allDontCare:
                if pairGroup(student1, student2):
                    found = True
                    pairs.append(Pair(student1, student2))
                    listToMatch.remove(student1)
                    removeDontCare(student2, womanDontCare, manDontCare, listToMatchDontCare, allDontCare)
                    break

        #If still not found, pull the first person in all dont care
        if not found:
            if(len(allDontCare)>0):
                student2 = allDontCare[0];
                found = True
                pairs.append(Pair(student1, student2))
                listToMatch.remove(student1)
                removeDontCare(student2, womanDontCare, manDontCare, listToMatchDontCare, allDontCare)
                break

        #if still not found, move the person to the singles list with the people who did not compete the survey (sorry dude, we really tried)
        if not found:
            didNotTakeSurvey.append(student1)
            listToMatch.remove(student1)

#Match list Dont Cares:
def matchListDontCare(allDontCare, pairs, didNotTakeSurvey):
    for student1 in allDontCare:
        for student2 in allDontCare:
            if pairFull(student1, student2):
                pairs.append(Pair(student1, student2))
                allDontCare.remove(student1)
                allDontCare.remove(student2)
                break

    #All the perfect matches are done, so try to make imperfect matches where time no longer matters but they have not been in a group together before
    for student1 in allDontCare:
        for student2 in allDontCare:
            if pairGroup(student1, student2):
                found = True
                pairs.append(Pair(student1, student2))
                allDontCare.remove(student1)
                allDontCare.remove(student2)
                break

    #if there are any other people, place them into the unrestrcited singles group
    for student1 in allDontCare:
        didNotTakeSurvey.append(student1)

    

    

    
            
                
            
