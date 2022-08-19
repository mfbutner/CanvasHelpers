from matching.games import StableMarriage, StableRoommates

from ..matching.checkValidGroup import is_valid_group
from ..matching.matchingFunc import match_partner, match_sym_partner
from ..matching.preferenceLists import preference_symmetrical_sort, preference_asymmetrical_sort
from ..shared.scoringFunc import score_group_by_one, score_two_by_two


def quad_has_partner(quad: list):
    flag = False
    for student1 in quad:
        for student2 in quad:
            if match_partner(student1, student2) or match_partner(student2, student1):
                flag = True
    return flag


def add_extras(quintuplets: list, leftover_students: list, matched_before: dict):
    for student in leftover_students:
        index = -1  # The index of the group the student will add onto
        max_score = -20000  # The max score group that the student would like

        for i in range(len(quintuplets)):
            if len(quintuplets[i]) != 5:
                # Skip this index because it's not a valid group of five
                continue

            # Test whether the group has matched before
            temp_list = [student]
            temp_list.extend(quintuplets[i])
            if is_valid_group(matched_before, temp_list) == 0:
                # The group is valid so you may commence
                temp_score = score_group_by_one(student, quintuplets[i], matched_before)
                if temp_score > max_score:
                    index = i
                    max_score = temp_score

        if index == -1:
            print(
                "Error: literally could not find student a group to match to, so I stuck the student in the first group")
            index = 0

        quintuplets[index].append(student)

    return quintuplets


def move_students_groups(quintuplets: list, ans: dict, singles: dict, alone_students: dict, quads: list):
    for key in ans:
        if key is not None and ans[key] is not None:
            temp_list = [alone_students[int(str(key))]]
            quad_student = singles[int(str(ans[key]))]

            # Search for the quad that the student the dict points to is in
            for quad in quads:
                if quad_student in quad:
                    temp_list.extend(quad)

            quintuplets.append(temp_list)


# When you have a preference list of
def remove_impossible_quin(ans: dict, match_dict: dict, students: dict, alone_students: dict,
                           alone_supposed_to_be_matched: list, quad_supposed_to_be_matched: list):
    remaining_alone = []
    remaining_quads = []

    # If the remaining alone and quads from supposed to be matched are not in the ans, place them back to be matched
    for student in alone_supposed_to_be_matched:
        for key in ans:
            flag = False
            if alone_students[int(str(key))] == student:
                flag = True
                break
        if not flag:
            remaining_alone.append(student)

    for quad in quad_supposed_to_be_matched:
        for key in ans:
            flag = False
            if students[int(str(ans[key]))] in quad:
                flag = True
                break
        if not flag:
            remaining_quads.append(quad)

    keys_to_take_out = []

    # For the rest, check to make sure the pairing is valid
    for key in ans:
        if key is not None and ans[key] is not None:
            temp_list = [alone_students[int(str(key))]]
            quad_student = students[int(str(ans[key]))]

            flag_quad = False
            for quad in quad_supposed_to_be_matched:
                if quad_student in quad:
                    temp_list.extend(quad)
                    flag_quad = True
                    break

            if not flag_quad:
                print("Could not find quad in removeImpossible")

            if is_valid_group(match_dict, temp_list) != 0:
                keys_to_take_out.append(key)

    for key in keys_to_take_out:
        # Find the students that correspond to these keys
        remaining_alone.append(alone_students[int(str(key))])

        quad_student = students[int(str(ans[key]))]
        for quad in quad_supposed_to_be_matched:
            if quad_student in quad:
                remaining_quads.append(quad)
                break
        ans.pop(key)

    alone_supposed_to_be_matched.clear()
    quad_supposed_to_be_matched.clear()

    alone_supposed_to_be_matched.extend(remaining_alone)
    quad_supposed_to_be_matched.extend(remaining_quads)

    return


def make_quintuplets(quads: list, alone_students: dict, singles: dict, matched_before: dict):
    # Each quad needs to match with one alone Student
    # Makes an empty list to avoid changing quads and alone_students
    extra_students_quads = []
    extra_students_alone = []
    for quad in quads:
        extra_students_quads.append(quad)
    for key in alone_students:
        extra_students_alone.append(alone_students[key])

    quintuplets = []

    finished = False
    if len(extra_students_alone) != len(extra_students_quads):
        print("Error: size mismatch in make_quintuplets")
    if len(extra_students_alone) == 0:
        finished = True
    i = 0

    while (not finished) and i < 5:
        preference_list_ones = preference_asymmetrical_sort(extra_students_alone, extra_students_quads, "GroupByOne",
                                                            matched_before)
        preference_list_quads = preference_asymmetrical_sort(extra_students_quads, extra_students_alone, "OneByGroup",
                                                             matched_before)

        game = StableMarriage.create_from_dictionaries(preference_list_ones, preference_list_quads)
        ans = game.solve()

        remove_impossible_quin(ans, matched_before, singles, alone_students, extra_students_alone, extra_students_quads)

        move_students_groups(quintuplets, ans, singles, alone_students, quads)

        if len(extra_students_alone) == 0:
            finished = True
        i += 1

        if len(extra_students_alone) != len(extra_students_quads):
            print("Error: size mismatch in make_quintuplets")

    list_used_indexes_alone = []
    list_used_indexes_quads = []
    groups_to_make = []
    for index1 in range(len(extra_students_alone)):
        for index2 in range(len(extra_students_quads)):
            if index1 not in list_used_indexes_alone and index2 not in list_used_indexes_quads:
                temp_list = [(extra_students_alone[index1])]
                temp_list.extend(extra_students_quads[index2])
                if is_valid_group(matched_before, temp_list) == 0:
                    list_used_indexes_alone.append(index1)
                    list_used_indexes_quads.append(index2)
                    groups_to_make.append([index1, index2])

    used_alone = []
    used_quads = []
    for groupToMake in groups_to_make:
        temp_list = [extra_students_alone[groupToMake[0]]]
        temp_list.extend(extra_students_quads[groupToMake[1]])
        quintuplets.append(temp_list)
        used_alone.append(extra_students_alone[groupToMake[0]])
        used_quads.append(extra_students_quads[groupToMake[1]])

    for student in used_alone:
        extra_students_alone.remove(student)

    for student in used_quads:
        extra_students_quads.remove(student)

    for index in range(0, len(extra_students_alone)):
        temp_list = extra_students_quads[index]
        temp_list.append(extra_students_alone[index])
        quintuplets.append(temp_list)

    extra_students_alone.clear()
    extra_students_quads.clear()

    return quintuplets


def remove_impossible_two(game: dict, match_dict: dict, students: dict, pairs: list,
                          student_supposed_to_be_matched: list):
    # create an empty list to store all the removed students
    extra_students = []

    # I can't change the dict size while it's going, so I need to record all the keys to take out in the iteration
    keys_to_take_out = []

    # The game ignores people it did not match, so if someone is supposed to matched and isn't, move them back into extra students
    for pair in student_supposed_to_be_matched:
        flag = False
        for key in game:
            if students[int(str(key))] in pair:
                flag = True
                break
        if not flag:
            extra_students.append(pair)

    for key in game:
        if key is not None and game[key] is not None:
            # only want to make a list of both students if they exist
            temp_list = [0] * 4
            student1 = students[int(str(key))]
            student2 = students[int(str(game[key]))]

            for pair in pairs:
                flag1 = False
                flag2 = False
                if student1 in pair:
                    flag1 = True
                    temp_list[0] = pair[0]
                    temp_list[1] = pair[1]
                if student2 in pair:
                    flag2 = True
                    temp_list[2] = pair[0]
                    temp_list[3] = pair[1]
                if flag1 and flag2:
                    break

            # If the two people cannot be in the group, then we are going to remove the first person
            if is_valid_group(match_dict, temp_list) != 0:
                # Delete both people from the list and move them into extra_students
                keys_to_take_out.append(key)

    for key in keys_to_take_out:
        # Need to add back both students in the pair
        for pair in pairs:
            # Find the pair that corresponds to this key
            # Should probably make pair into a dictionary later
            if students[int(str(key))] in pair:
                extra_students.append(pair)
                break
        game.pop(key)

    return extra_students


def move_students_two(ans: dict, quads: list, students: dict, pairs: list):
    # Keep a list of all the used keys, so we don't add a pair twice
    used_keys = []

    # Make student-student if match_type is OneByOne
    for key in ans:
        if key is not None and ans[key] is not None:
            this_student_key = int(str(key))
            other_student_key = int(str(ans[key]))

            # Don't add a pair if its reverse was already added
            if not (other_student_key in used_keys):
                used_keys.append(this_student_key)
                # Find the appropriate pairs
                temp_list = [0] * 4
                student1 = students[this_student_key]
                student2 = students[other_student_key]
                for pair in pairs:
                    flag1 = False
                    flag2 = False
                    if student1 in pair:
                        flag1 = True
                        temp_list[0] = pair[0]
                        temp_list[1] = pair[1]
                    if student2 in pair:
                        flag2 = True
                        temp_list[2] = pair[0]
                        temp_list[3] = pair[1]
                    if flag1 and flag2:
                        break

                # Add the set of two students to the quad list
                quads.append(temp_list)

    return quads


# There are some options from game that we cannot actually use, so we need to take them out of game, and return the unused students to make the next run as extra students
# game: a list of student's with another student's id as the key - these are "good" matches
# matchedDict: a dictionary of student id matches to check who has matched before
# I need the full list of students
def remove_impossible_one(game: dict, match_dict: dict, students: dict, students_supposed_to_be_matched: list):
    # create an empty list to store all the removed students
    extra_students = []

    # I can't change the dict size while it's going, so I need to record all the keys to take out in the iteration
    keys_to_take_out = []

    # The game ignores people it did not match, so if someone is supposed to matched and isn't, move them back into extra students
    for student in students_supposed_to_be_matched:
        flag = False
        for key in game:
            if students[int(str(key))] == student:
                flag = True
                break
        if not flag:
            extra_students.append(student)

    for key in game:
        if game[key] == "":
            keys_to_take_out.append(key)
            continue

        # only want to make a list of both students if they exist
        if key is not None and game[key] is not None:
            list_students = [students[int(str(key))], students[int(str(game[key]))]]

            # If the two people cannot be in the group, then we are going to remove the first person
            if is_valid_group(match_dict, list_students) != 0:
                # Delete both people from the list and move them into extra_students
                keys_to_take_out.append(key)
                continue

    # For each key to take out, add that student to extra_students
    for key in keys_to_take_out:
        extra_students.append(students[int(str(key))])
        game.pop(key)

    return extra_students


# Move the now correct student pairs into the actual pairs
def move_students_one(ans: dict, pairs: list, students: dict):
    # Keep a list of all the used keys, so we don't add a pair twice

    used_keys = []

    # Make student-student if match_type is OneByOne

    for key in ans:
        if key is not None and ans[key] is not None:
            this_student_key = int(str(key))
            other_student_key = int(str(ans[key]))

            # Don't add a pair if its reverse was already added
            if not (other_student_key in used_keys):
                used_keys.append(this_student_key)
                pairs.append([students[this_student_key], students[other_student_key]])

    return


# Make pairs of student-student
def make_pairs(students: dict, match_dict: dict):
    # Make a copy that won't change the original students
    extra_students = []

    for student in students:
        extra_students.append((students[student]))

    pairs = []

    # Control mechanisms for the loop: check if all the students have been paired, and that the list has not been
    finished = len(extra_students) == 0

    i = 0
    # You don't want to loop too many times, but run five times at most to find good matches that have not matched before
    while not finished and i < 10:
        preference_list = preference_symmetrical_sort(extra_students, "OneByOne", match_dict)
        game = StableRoommates.create_from_dictionary(preference_list)
        ans = game.solve()

        # remove the students who did not find matches out, delete them from the ans dict
        extra_students = remove_impossible_one(ans, match_dict, students, extra_students)

        # Take the remaining, successful students, and place them into pairs
        move_students_one(ans, pairs, students)

        # Update your controls
        if len(extra_students) == 0:
            finished = True
            break

        i += 1

    for index in range(5):
        list_used_indexes = []
        pairs_to_make = []
        for index1 in range(len(extra_students)):
            for index2 in range(len(extra_students)):
                if index1 != index2 and (index1 not in list_used_indexes) and (index2 not in list_used_indexes):
                    if is_valid_group(match_dict, [extra_students[index1], extra_students[index2]]) == 0:
                        list_used_indexes.append(index1)
                        list_used_indexes.append(index2)
                        pairs_to_make.append([index1, index2])

        used_students = []
        for pairToMake in pairs_to_make:
            pairs.append([extra_students[pairToMake[0]], extra_students[pairToMake[1]]])
            used_students.extend([extra_students[pairToMake[0]], extra_students[pairToMake[1]]])

        for student in used_students:
            extra_students.remove(student)

    if len(extra_students) % 2 == 1:
        print("Problem: odd number of students in extra_students")

    # Match the rest of the students randomly and print that the matching sucked
    for index in range(0, len(extra_students), 2):
        if (index + 1) < len(extra_students):
            pairs.append([extra_students[index], extra_students[index + 1]])
    extra_students.clear()

    # Return the pairs list (list[Student, Student])
    return pairs


# We probably want to fold this code in with make pairs eventually, but for now it's here
# students dict - a dictionary of all the students
# match_dict - a dictionary of all invalid matching
def make_quads(students: dict, match_dict: dict, pairs: list):
    # Make a copy that won't change the original students
    extra_students = []

    for pair in pairs:
        extra_students.append(pair)

    quads = []

    # Control mechanisms for the loop: check if all the pairs been put into quads
    finished = False
    if len(extra_students) == 0:
        finished = True
    i = 0

    # You don't want to loop too many times, but run five times at most to find good matches that have not matched before
    while not finished and i < 10:
        preference_list = preference_symmetrical_sort(extra_students, "TwoByTwo", match_dict)
        game = StableRoommates.create_from_dictionary(preference_list)
        ans = game.solve()

        # remove the students who did not find matches out, delete them from the ans dict
        extra_students = remove_impossible_two(ans, match_dict, students, pairs, extra_students)

        # Take the remaining, successful students, and place them into pairs
        move_students_two(ans, quads, students, pairs)

        # Update your controls
        if len(extra_students) == 0:
            finished = True
        i += 1

    for index in range(5):
        list_used_indexes = []
        pairs_to_make = []
        for index1 in range(len(extra_students)):
            for index2 in range(len(extra_students)):
                if index1 != index2 and (index1 not in list_used_indexes) and (index2 not in list_used_indexes):
                    if is_valid_group(match_dict,
                                      [extra_students[index1][0], extra_students[index1][1], extra_students[index2][0],
                                       extra_students[index2][1]]) == 0:
                        list_used_indexes.append(index1)
                        list_used_indexes.append(index2)
                        pairs_to_make.append([index1, index2])

        used_students = []
        for pairToMake in pairs_to_make:
            quads.append(
                [extra_students[pairToMake[0]][0], extra_students[pairToMake[0]][1], extra_students[pairToMake[1]][0],
                 extra_students[pairToMake[1]][1]])
            used_students.extend([extra_students[pairToMake[0]], extra_students[pairToMake[1]]])

        for student in used_students:
            extra_students.remove(student)

    # Now do random
    for index in range(0, len(extra_students), 2):
        quads.append([extra_students[index][0], extra_students[index][1], extra_students[index + 1][0],
                      extra_students[index + 1][1]])
    extra_students.clear()

    return quads


def find_min_index(quads: list, matched_before: dict, no_take_list: list):
    index = 0
    min_score = score_two_by_two([quads[0][0], quads[0][1]], [quads[0][2], quads[0][3]], matched_before)

    for i in range(len(quads)):
        pair1 = [quads[i][0], quads[i][1]]
        pair2 = [quads[i][2], quads[i][3]]

        if score_two_by_two(pair1, pair2, matched_before) < min_score and i not in no_take_list:
            min_score = score_two_by_two(pair1, pair2, matched_before)
            index = i

    return index


def clean_quads(quads: list, singles: dict, num_groups: int, matched_before: dict):
    if len(quads) == num_groups:
        return

    no_take_list = []
    # In the case that there are too many quads, break up the least happy ones
    while len(quads) > num_groups:
        index = find_min_index(quads, matched_before, no_take_list)
        remove_quad = quads[index]
        if not quad_has_partner(remove_quad):
            quads.remove(remove_quad)
            for person in remove_quad:
                singles[int(person.id_num)] = person
        else:
            no_take_list.append(index)

    # This should not happen
    if len(quads) < num_groups:
        print("ERROR: the number of quads should match the number of needed groups")


# Make a list of the possible students
def make_groups(singles: dict, extra_students: dict, matched_before: dict):
    # Calculate the number of needed groups
    len_class = len(singles) + len(extra_students)
    num_groups = len_class // 5

    # move students from extras to free singles until I have 4/5 the class AND it's divisible by 4
    while len(singles) < num_groups * 4 and len(extra_students) > 0:
        id_num, student = extra_students.popitem()
        singles[id_num] = student

    # People need to move between the two lists in order to make the students divisible by 4
    while len(singles) % 4 != 0:
        # If there are not enough students to move out of extra students, move some people who took the survey in
        if len(extra_students) < len(singles) % 4:
            student = singles.popitem()
            extra_students[student[0]] = student[1]
        else:
            # Else you can just add extra_students in to the singles list
            student = extra_students.popitem()
            singles[student[0]] = student[1]

    singles1 = {}
    singles2 = {}
    pairs = []
    place_in1_flag = False
    id_placed_in_pairs = []
    # Separate out anyone who wanted each other
    for student1Key in singles:
        flag = False
        for student2Key in singles:
            if student1Key == student2Key:
                continue

            if match_sym_partner(singles[student1Key], singles[student2Key]):
                if student1Key not in id_placed_in_pairs and student2Key not in id_placed_in_pairs:
                    pairs.append([singles[student1Key], singles[student2Key]])
                    id_placed_in_pairs.extend([student1Key, student2Key])

                flag = True

        if not flag and place_in1_flag:
            singles2[student1Key] = singles[student1Key]
            place_in1_flag = False
        elif not flag:
            singles1[student1Key] = singles[student1Key]
            place_in1_flag = True

    for pair in pairs:
        print(pair[0].name, pair[1].name)

    if len(singles1) % 2 == 1 or len(singles2) % 2 == 1:
        print("ERROR: singles should be divisible by 2")
        return 1

    # Make the first set of pairs
    pairs1 = make_pairs(singles1, matched_before)
    pairs2 = make_pairs(singles2, matched_before)

    # Place the pairs together
    for i in range(len(pairs1)):
        pairs.append(pairs1[i])
    for i in range(len(pairs2)):
        pairs.append(pairs2[i])

    # Make the pairs into quads
    quads = make_quads(singles, matched_before, pairs)

    # The quads needed to be broken down if there are too many
    clean_quads(quads, extra_students, num_groups, matched_before)

    leftover_students = []
    # I need a list of alone_students that is equal to the size of num_groups
    while len(extra_students) != num_groups:
        if len(extra_students) > num_groups:
            leftover_students.append(((extra_students.popitem())[1]))
        elif len(extra_students) < num_groups:
            print("This should not happen, more quads need to be broken in clean quads")

    # With the proper number of quads and singles, make sets of 5
    quintuplets = make_quintuplets(quads, extra_students, singles, matched_before)

    if len(leftover_students) > 0:
        groups = add_extras(quintuplets, leftover_students, matched_before)
    elif len(leftover_students) == 0:
        return quintuplets

    return quintuplets
