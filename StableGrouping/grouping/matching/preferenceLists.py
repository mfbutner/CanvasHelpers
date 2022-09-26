from ..shared.scoringFunc import score_one_by_one, score_two_by_two, score_group_by_one, score_one_by_group


# Creates a dictionary of students, where each student corresponds to a list of students in order of preference
def preference_symmetrical_sort(list_students: list, type_sort: str, matched_before: dict):
    dict_student_return = {}

    # First select the student or group you are scoring
    for student1 in list_students:
        # Initialize an empty array
        temp_array = []

        # Rotate through all the other students in the list
        for student2 in list_students:
            # We need to differentiate between student and student-student pairs
            if type_sort == "OneByOne":
                # Don't gauge students by themselves
                if student1.id_num != student2.id_num:
                    temp_array.append([str(student2.id_num), score_one_by_one(student1, student2, matched_before)])

            elif type_sort == "TwoByTwo":
                # Don't gauge student pairs by themselves
                if student1[0].id_num != student2[0].id_num:
                    temp_array.append([str(student2[0].id_num), score_two_by_two(student1, student2, matched_before)])

        # Now sort the list with max score first
        sorted(temp_array, key=lambda score: score[1], reverse=True)

        # Take only the ids
        temp_array = [student[0] for student in temp_array]

        if type_sort == "OneByOne":
            dict_student_return[str(student1.id_num)] = temp_array
        elif type_sort == "TwoByTwo":
            dict_student_return[str(student1[0].id_num)] = temp_array
        else:
            print("Error: This should not run (Function: preference_symmetrical_sort)")

    return dict_student_return


# Create a dictionary of students, where each student/student Group Ranks another
# list_students1: the list of students judging
# list_students2: the list of the list of students to be judged
def preference_asymmetrical_sort(list_students1: list, list_students2: list, type_sort: str, match_before: dict):
    # Create an empty dictionary to fill
    dict_student = {}

    # First select the student or group you are scoring
    for student1 in list_students1:
        temp_array = []
        for student2List in list_students2:
            if type_sort == "OneByGroup":
                temp_array.append([str(student2List.id_num), score_one_by_group(student2List, student1, match_before)])
            elif type_sort == "GroupByOne":
                temp_array.append(
                    [str(student2List[0].id_num), score_group_by_one(student1, student2List, match_before)])

        # Now sort the list with max score first
        sorted(temp_array, key=lambda score: score[1], reverse=True)

        # Take only the ids of the first student of the sets
        temp_array = [student[0] for student in temp_array]
        if type_sort == "OneByGroup":
            dict_student[str(student1[0].id_num)] = temp_array
        elif type_sort == "GroupByOne":
            dict_student[str(student1.id_num)] = temp_array
        else:
            print("Error: This should not run (Function: preference_asymmetrical_sort)")

    return dict_student
