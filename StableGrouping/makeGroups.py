from preferenceLists import preferenceSymmetricalSort, preferenceAsymmetricalSort
from matching.games import StableMarriage, StableRoommates
from scoringFunc import scoreGroupByOne, scoreTwoByTwo
from checkValidGroup import isValidGroup
from matchingFunc import matchPartner, matchSymPartner


def quadHasPartner(quad: list):
    flag = False
    for student1 in quad:
        for student2 in quad:
            if matchPartner(student1, student2) or matchPartner(student2, student1):
                flag = True
    return flag


def addExtras(quintuplets: list, leftoverStudents: list, matched_before: dict):
    for student in leftoverStudents:
        index = -1      # The index of the group the student will add onto
        maxScore = -20000 # The max score group that the student would like

        for i in range(len(quintuplets)):
            if len(quintuplets[i]) != 5:
                # Skip this index because its not a valid group of five
                continue

            # Test whether the group has matched before
            tempList = [student]
            tempList.extend(quintuplets[i])
            if isValidGroup(matched_before, tempList) == 0:
                # The group is valid so you may commence
                tempScore = scoreGroupByOne(student, quintuplets[i], matched_before)
                if tempScore > maxScore:
                    index = i
                    maxScore = tempScore

        if index == -1:
            print("Error: literally could not find student a group to match to, so I stuck the student in the first group")
            index = 0

        quintuplets[index].append(student)

    return quintuplets


def moveStudentsGroups(quintuplets: list, ans: dict, singles: dict, aloneStudents: dict, quads: list):
    for key in ans:
        if key != None and ans[key]!= None:
            tempList = [aloneStudents[int(str(key))]]
            quadStudent = singles[int(str(ans[key]))]

            # Search for the quad that the student the dict points to is in
            for quad in quads:
                if quadStudent in quad:
                    tempList.extend(quad)

            quintuplets.append(tempList)


# When you have a preference list of
def removeImpossibleQuin(ans: dict, matchDict: dict, students: dict, aloneStudents:dict, aloneSupposedToBeMatched:list, quadSupposedToBeMatched: list):
    remainingAlone = []
    remainingQuads = []

    # If the remaining along and quads from supposed to be matching do not show up in the ans, place them back to be matched
    for student in aloneSupposedToBeMatched:
        for key in ans:
            flag = False
            if aloneStudents[int(str(key))] == student:
                flag = True
                break
        if not flag:
            remainingAlone.append(student)

    for quad in quadSupposedToBeMatched:
        for key in ans:
            flag = False
            if students[int(str(ans[key]))] in quad:
                flag = True
                break
        if not flag:
            remainingQuads.append(quad)

    keysToTakeOut = []

    #For the rest, check to make sure the pairing is valid
    for key in ans:
        if key != None and ans[key] != None:
            tempList = [aloneStudents[int(str(key))]]
            quadStudent = students[int(str(ans[key]))]

            flagQuad = False
            for quad in quadSupposedToBeMatched:
                if quadStudent in quad:
                    tempList.extend(quad)
                    flagQuad = True
                    break

            if flagQuad == False:
                print("Could not find quad in removeImpossible")

            if isValidGroup(matchDict, tempList) != 0:
                keysToTakeOut.append(key)

    for key in keysToTakeOut:
        #Find the students that correspond to these keys
        remainingAlone.append(aloneStudents[int(str(key))])

        quadStudent = students[int(str(ans[key]))]
        for quad in quadSupposedToBeMatched:
            if quadStudent in quad:
                remainingQuads.append(quad)
                break
        ans.pop(key)

    aloneSupposedToBeMatched.clear()
    quadSupposedToBeMatched.clear()

    aloneSupposedToBeMatched.extend(remainingAlone)
    quadSupposedToBeMatched.extend(remainingQuads)

    return


def makeQuintuplets(quads: list, aloneStudents: dict, singles: dict, matched_before: dict):
    # Each quad needs to match with one alone Student
    # make an empty list to avoid changing quads and aloneStudents
    extraStudentsQuads = []
    extraStudentsAlone = []
    for quad in quads:
        extraStudentsQuads.append(quad)
    for key in aloneStudents:
        extraStudentsAlone.append(aloneStudents[key])

    quintuplets = []

    finished = False
    if len(extraStudentsAlone) != len(extraStudentsQuads):
        print("Error: size mismatch in makeQuintuplets")
    if len(extraStudentsAlone) == 0:
        finished = True
    i = 0

    while (not finished) and i < 5:
        preferenceListOnes = preferenceAsymmetricalSort(extraStudentsAlone, extraStudentsQuads, "GroupByOne", matched_before)
        preferenceListQuads = preferenceAsymmetricalSort(extraStudentsQuads, extraStudentsAlone, "OneByGroup", matched_before)

        game = StableMarriage.create_from_dictionaries(preferenceListOnes, preferenceListQuads)
        ans = game.solve()


        removeImpossibleQuin(ans, matched_before, singles, aloneStudents, extraStudentsAlone, extraStudentsQuads)

        moveStudentsGroups(quintuplets, ans, singles, aloneStudents, quads)

        if len(extraStudentsAlone) == 0:
            finished = True
        i = i+ 1

        if len(extraStudentsAlone) != len(extraStudentsQuads):
            print("Error: size mismatch in makeQuintuplets")


    listUsedIndexesAlone = list()
    listUsedIndexesQuads = list()
    groupsToMake = list()
    for index1 in range(len(extraStudentsAlone)):
        for index2 in range(len(extraStudentsQuads)):
            if index1 not in listUsedIndexesAlone and index2 not in listUsedIndexesQuads:
                tempList = [(extraStudentsAlone[index1])]
                tempList.extend(extraStudentsQuads[index2])
                if isValidGroup(matched_before, tempList) == 0:
                    listUsedIndexesAlone.append(index1)
                    listUsedIndexesQuads.append(index2)
                    groupsToMake.append([index1, index2])

    usedAlone = list()
    usedQuads = list()
    for groupToMake in groupsToMake:
        tempList = [extraStudentsAlone[groupToMake[0]]]
        tempList.extend(extraStudentsQuads[groupToMake[1]])
        quintuplets.append(tempList)
        usedAlone.append(extraStudentsAlone[groupToMake[0]])
        usedQuads.append(extraStudentsQuads[groupToMake[1]])

    for student in usedAlone:
        extraStudentsAlone.remove(student)

    for student in usedQuads:
        extraStudentsQuads.remove(student)

    for index in range(0, len(extraStudentsAlone)):
        tempList = extraStudentsQuads[index]
        tempList.append(extraStudentsAlone[index])
        quintuplets.append(tempList)

    extraStudentsAlone.clear()
    extraStudentsQuads.clear()

    return quintuplets


def removeImpossibleTwo(game: dict, matchDict: dict, students: dict, pairs: list, studentSupposedToBeMatched: list):
    # create an empty list to store all the removed students
    extraStudents = []

    # I can't change the dict size while it's going, so I need to record all the keys to take out in the iteration
    keysToTakeOut = []

    # The game ignores people it did not match, so if someone is supposed to matched and isn't, move them back into extra students
    for pair in studentSupposedToBeMatched:
        flag = False
        for key in game:
            if students[int(str(key))] in pair:
                flag = True
                break
        if not flag:
            extraStudents.append(pair)

    for key in game:
        if key != None and game[key]!= None:
            # only want to make a list of both students if they exist
            tempList = [0] * 4
            student1 = students[int(str(key))]
            student2 = students[int(str(game[key]))]

            for pair in pairs:
                flag1 = False
                flag2 = False
                if student1 in pair:
                    flag1 = True
                    tempList[0] = pair[0]
                    tempList[1] = pair[1]
                if student2 in pair:
                    flag2 = True
                    tempList[2] = pair[0]
                    tempList[3] = pair[1]
                if flag1 and flag2:
                    break

            # If the two people cannot be in the group, then we are going to remove the first person
            if isValidGroup(matchDict, tempList) != 0:
                # Delete both people from the list and move them into extraStudents
                keysToTakeOut.append(key)


    for key in keysToTakeOut:
        # Need to add back both students in the pair
        for pair in pairs:
            # Find the pair that corresponds to this key
            # Should probably make pair into a dictionary later
            if students[int(str(key))] in pair:
                extraStudents.append(pair)
                break
        game.pop(key)

    return extraStudents


def moveStudentsTwo(ans: dict, quads: list, students: dict, pairs: list):
    # Keep a list of all the used keys so we don't add a pair twice
    usedKeys = []

    # Make student-student if matchType is OneByOne
    for key in ans:
        if key != None and ans[key]!= None:
            thisStudentKey = int(str(key))
            otherStudentKey = int(str(ans[key]))

            # Don't add a pair if its reverse was already added
            if not (otherStudentKey in usedKeys):
                usedKeys.append(thisStudentKey)
                # Find the appropriate pairs
                tempList = [0] * 4
                student1 = students[thisStudentKey]
                student2 = students[otherStudentKey]
                for pair in pairs:
                    flag1 = False
                    flag2 = False
                    if student1 in pair:
                        flag1 = True
                        tempList[0] = pair[0]
                        tempList[1] = pair[1]
                    if student2 in pair:
                        flag2 = True
                        tempList[2] = pair[0]
                        tempList[3] = pair[1]
                    if flag1 and flag2:
                        break

                # Add the set of two students to the quad list
                quads.append(tempList)

    return quads


# There are some options from game that we cannot actually use, so we need to take them out of game, and return the unused students to make the next run as extra students
# game: a list of student's with another student's id as the key- these are "good" matches
# matchedDict: a dictionary of student id matches to check who has matched before
# I need the full list of students
def removeImpossibleOne(game: dict, matchDict: dict, students: dict, studentsSupposedToBeMatched: list):
    # create an empty list to store all the removed students
    extraStudents = []

    # I can't change the dict size while it's going, so I need to record all the keys to take out in the iteration
    keysToTakeOut = []

    # The game ignores people it did not match, so if someone is supposed to matched and isn't, move them back into extra students
    for student in studentsSupposedToBeMatched:
        flag = False
        for key in game:
            if students[int(str(key))] == student:
                flag = True
                break
        if not flag:
            extraStudents.append(student)

    for key in game:
        if game[key] == "":
            keysToTakeOut.append(key)
            continue

        # only want to make a list of both students if they exist
        if key != None and game[key]!= None:
            listStudents = [students[int(str(key))], students[int(str(game[key]))]]

            # If the two people cannot be in the group, then we are going to remove the first person
            if isValidGroup(matchDict, listStudents) != 0:
                # Delete both people from the list and move them into extraStudents
                keysToTakeOut.append(key)
                continue


    # For each key to take out, add that student to extraStudents
    for key in keysToTakeOut:
        extraStudents.append(students[int(str(key))])
        game.pop(key)

    return extraStudents


# Move the now correct student pairs into the actual pairs
def moveStudentsOne(ans: dict, pairs: list, students: dict):
    # Keep a list of all the used keys so we don't add a pair twice


    usedKeys = []

    # Make student-student if matchType is OneByOne

    for key in ans:
        if key != None and ans[key]!= None:
            thisStudentKey = int(str(key))
            otherStudentKey = int(str(ans[key]))

            # Don't add a pair if its reverse was already added
            if not (otherStudentKey in usedKeys):
                usedKeys.append(thisStudentKey)
                pairs.append([students[thisStudentKey], students[otherStudentKey]])

    return


# Make pairs of student-student
def makePairs(students: dict, matchDict: dict):
    # Make a copy that won't change the original students
    extraStudents = []

    for student in students:
        extraStudents.append((students[student]))

    pairs = []

    # Control mechanisms for the loop: check if all the students have been paired, and that the list has not been
    finished = False
    if len(extraStudents) == 0:
        finished = True

    i = 0
    # You don't want to loop too many times, but run five times at most to find good matches that have not matched before
    while(not finished and i < 10):
        preferenceList = preferenceSymmetricalSort(extraStudents, "OneByOne", matchDict)
        game = StableRoommates.create_from_dictionary(preferenceList)
        ans = game.solve()

        # remove the students who did not find matches out, delete them from the ans dict
        extraStudents = removeImpossibleOne(ans, matchDict, students, extraStudents)

        # Take the remaining, successful students, and place them into pairs
        moveStudentsOne(ans, pairs, students)

        # Update your controls
        if len(extraStudents) == 0:
            finished = True
            break

        i = i + 1

    for index in range(5):
        listUsedIndexes = list()
        pairsToMake = list()
        for index1 in range(len(extraStudents)):
            for index2 in range(len(extraStudents)):
                if index1 != index2 and (index1 not in listUsedIndexes) and (index2 not in listUsedIndexes):
                    if isValidGroup(matchDict, [extraStudents[index1], extraStudents[index2]]) == 0:
                        listUsedIndexes.append(index1)
                        listUsedIndexes.append(index2)
                        pairsToMake.append([index1, index2])

        usedStudents = list()
        for pairToMake in pairsToMake:
            pairs.append([extraStudents[pairToMake[0]], extraStudents[pairToMake[1]]])
            usedStudents.extend([extraStudents[pairToMake[0]], extraStudents[pairToMake[1]]])

        for student in usedStudents:
            extraStudents.remove(student)

    if len(extraStudents) % 2 == 1:
        print("Problem: odd number of students in extraStudents")

    # Match the rest of the students randomly and print that the matching sucked
    for index in range(0, len(extraStudents), 2):
        if (index+1) < len(extraStudents):
            pairs.append([extraStudents[index], extraStudents[index+1]])
    extraStudents.clear()

    # Return the pairs list (list[Student, Student])
    return pairs


# We probably want to fold this code in with make pairs eventually, but for now it's here
# students dict - a dictionary of all the students
# matchDict - a dictionary of all invalid matching
def makeQuads(students: dict, matchDict: dict, pairs: list):
    # Make a copy that won't change the original students
    extraStudents = []

    for pair in pairs:
        extraStudents.append(pair)

    quads = []

    # Control mechanisms for the loop: check if all the pairs been put into quads
    finished = False
    if len(extraStudents) == 0:
        finished = True
    i = 0

    # You don't want to loop too many times, but run five times at most to find good matches that have not matched before
    while not finished and i < 10:
        preferenceList = preferenceSymmetricalSort(extraStudents, "TwoByTwo", matchDict)
        game = StableRoommates.create_from_dictionary(preferenceList)
        ans = game.solve()


        #remove the students who did not find matches out, delete them from the ans dict
        extraStudents = removeImpossibleTwo(ans, matchDict, students, pairs, extraStudents)

        #Take the remaining, successful students, and place them into pairs
        moveStudentsTwo(ans, quads, students, pairs)

        #Update your controls
        if len(extraStudents) == 0:
            finished = True
        i = i + 1

    for index in range(5):
        listUsedIndexes = list()
        pairsToMake = list()
        for index1 in range(len(extraStudents)):
            for index2 in range(len(extraStudents)):
                if index1 != index2 and (index1 not in listUsedIndexes) and (index2 not in listUsedIndexes):
                    if isValidGroup(matchDict, [extraStudents[index1][0], extraStudents[index1][1], extraStudents[index2][0], extraStudents[index2][1]]) == 0:
                        listUsedIndexes.append(index1)
                        listUsedIndexes.append(index2)
                        pairsToMake.append([index1, index2])

        usedStudents = list()
        for pairToMake in pairsToMake:
            quads.append([extraStudents[pairToMake[0]][0], extraStudents[pairToMake[0]][1], extraStudents[pairToMake[1]][0], extraStudents[pairToMake[1]][1]])
            usedStudents.extend([extraStudents[pairToMake[0]], extraStudents[pairToMake[1]]])


        for student in usedStudents:
            extraStudents.remove(student)

    # Now do random
    for index in range(0, len(extraStudents), 2):
        quads.append([extraStudents[index][0], extraStudents[index][1], extraStudents[index+1][0], extraStudents[index+1][1]])
    extraStudents.clear()

    return quads


def findMinIndex(quads: list, matched_before: dict, noTakeList:list):
    index = 0
    minScore = scoreTwoByTwo([quads[0][0], quads[0][1]],  [quads[0][2], quads[0][3]], matched_before)

    for i in range(len(quads)):
        pair1 = [quads[i][0], quads[i][1]]
        pair2 = [quads[i][2], quads[i][3]]

        if scoreTwoByTwo(pair1, pair2, matched_before) < minScore and i not in noTakeList:
            minScore = scoreTwoByTwo(pair1, pair2, matched_before)
            index = i

    return index


def cleanQuads(quads: list, singles: dict, numGroups: int, matched_before: dict):
    if len(quads) == numGroups:
        return

    noTakeList = list()
    # In the case that there are too many quads, break up the least happy ones
    while(len(quads) > numGroups):
        index = findMinIndex(quads, matched_before, noTakeList)
        removeQuad = quads[index]
        if not quadHasPartner(removeQuad):
            quads.remove(removeQuad)
            for person in removeQuad:
                singles[int(person.idNum)] = person
        else:
            noTakeList.append(index)


    # This should not happen
    if len(quads) < numGroups:
        print("ERROR: the number of quads should match the number of needed groups")


# Make a list of the possible students
def makeGroups(singles: dict, extra_students: dict, matched_before: dict):
    # Calculate the number of needed groups
    lenClass = len(singles) + len(extra_students)
    numGroups = lenClass // 5

    i = 0 # temp

    # move students from extras to free singles until I have 4/5 the class and it's divisible by 4
    while(len(singles) < numGroups*4 and len(extra_students) > 0):
        student = extra_students.popitem()
        singles[student[0]] = student[1]

    # People need to move between the two lists in order to make the students divisible by 4
    while(len(singles)%4 != 0):
        # If there are not enough students to move out of extra students, you gotta move some people who took the survey in
        if len(extra_students) < len(singles)%4:
            student = singles.popitem()
            extra_students[student[0]] = student[1]
        else:
            # Else you can just add extra_students in to the singles list
            student = extra_students.popitem()
            singles[student[0]] = student[1]

    index = 0
    singlesOther = dict()
    singles1 = dict()
    singles2 = dict()

    pairs = list()
    placeIn1Flag = False
    idPlacedInPairs = list()
    # Separate out anyone who wanted eachother
    for student1Key in singles:
        flag = False
        for student2Key in singles:
            if student1Key != student2Key:
                if matchSymPartner(singles[student1Key], singles[student2Key]):
                    if student1Key not in idPlacedInPairs and student2Key not in idPlacedInPairs:
                        pairs.append([singles[student1Key], singles[student2Key]])
                        idPlacedInPairs.extend([student1Key, student2Key])

                    flag = True

        if not flag and placeIn1Flag:
            singles2[student1Key] = singles[student1Key]
            placeIn1Flag = False
        elif not flag:
            singles1[student1Key] = singles[student1Key]
            placeIn1Flag = True

    for pair in pairs:
        print(pair[0].name, pair[1].name)

    if len(singles1) % 2 == 1 or len(singles2) % 2 == 1:
        print("ERROR: singles should be divisible by 2")
        return 1

    # Make the first set of pairs
    pairs1 = makePairs(singles1, matched_before)
    pairs2 = makePairs(singles2, matched_before)

    # Place the pairs together
    for i in range(len(pairs1)):
        pairs.append(pairs1[i])
    for i in range(len(pairs2)):
        pairs.append(pairs2[i])

    # Make the pairs into quads
    quads = makeQuads(singles, matched_before, pairs)

    # The quads needed to be broken down if there are too many
    cleanQuads(quads, extra_students, numGroups, matched_before)

    leftoverStudents = list()
    # I need a list of aloneStudents that is equal to the size of numGroups
    while(len(extra_students) != numGroups):
        if len(extra_students) > numGroups:
            leftoverStudents.append(((extra_students.popitem())[1]))
        elif len(extra_students) < numGroups:
            print("This should not happen, more quads need to be broken in clean quads")

    # With the proper number of quads and singles, make sets of 5
    quintuplets = makeQuintuplets(quads, extra_students, singles, matched_before)

    if len(leftoverStudents) > 0:
        groups = addExtras(quintuplets, leftoverStudents, matched_before)
    elif len(leftoverStudents) == 0:
        return quintuplets

    return quintuplets
