from ..matchingFunc import matchGender, matchSkill, matchLanguage, matchTime, matchActivity, matchInternational
from ..scoringFunc import scoreAtLeastOneConfidenceLevel
from ..checkValidGroup import isValidGroup


# Analyze the groups on set criteria
def grade_groups(groups: list, match_before: dict):
    # Count the number of students who did or did not take the survey
    default_students = 0
    students_take_survey = 0

    # Count the number of students who successfully got a gender match out of the ones who wanted it
    students_gender_match = 0
    students_want_gender_match = 0

    # Count the number of students who wanted asynch/synch and got a match in their group
    students_want_time = 0
    students_got_time = 0

    # Count the number of groups and the valid groups
    num_groups = 0
    num_valid_groups = 0

    # Count the number of groups with a leader personality
    groups_got_leader = 0

    # Count the number of students who wanted another international student and got it
    students_want_international = 0
    students_got_international = 0

    # Count all the students who got their preferred language
    students_got_language = 0

    # Count all the students who got their preferred activity
    students_got_option = 0

    # Count which priority the students got first
    # If both second choice and first are met on one student, only firstChoice increases
    student_got_choice = [0, 0, 0, 0, 0, 0]

    # Count the number of groups where there are people of multiple confidence levels
    num_groups_mix_confidence = 0

    # Iterate through each group
    for group in groups:
        # Increment the number of overall Groups
        num_groups = num_groups + 1

        # increment valid group if the groups are valid
        if isValidGroup(match_before, group) == 0:
            num_valid_groups = num_valid_groups + 1

        # increment confidenceLevels if group has a mixture of high to low confidence
        if scoreAtLeastOneConfidenceLevel(group) > 0:
            num_groups_mix_confidence = num_groups_mix_confidence + 1

        # a flag that becomes true if anyone in the group is a leader
        flag_leader = False

        # The others are by person
        for person in group:
            # Flags to control what the person does and does not get
            flag_gender = False
            flag_time = False
            flag_international = False
            flag_language = False
            flag_option = False

            # Default students should not affect stats
            if not person.pronouns:
                default_students = default_students + 1
                continue
            else:
                students_take_survey = students_take_survey + 1

            # if anyone in the group is a leader, the whole group gets a leader
            if person.prefer_leader:
                flag_leader = True

            # check this person based on the rest of the group
            for person2 in group:
                # Don't check a person against themselves
                if person != person2:

                    # Gender
                    if matchGender(person, person2):
                        flag_gender = True

                    # Time
                    if matchTime(person, person2):
                        flag_time = True

                    # International
                    if matchInternational(person, person2):
                        flag_international = True

                    # Language
                    if person.language == person2.language:
                        flag_language = True

                    # Option
                    if person.activity_choice == person2.activity_choice:
                        flag_option = True

            # Only count the person if the person wanted to match on gender
            if person.prefer_same != 1:
                students_want_gender_match = students_want_gender_match + 1
                if flag_gender:
                    students_gender_match = students_gender_match + 1

            # Only count the person if the person wanted to match on time
            if person.prefer_async != 1:
                students_want_time = students_want_time + 1
                if flag_time:
                    students_got_time = students_got_time + 1

            # Only count the person if the person wanted to match on international
            if person.international == 2:
                students_want_international = students_want_international + 1
                if flag_international:
                    students_got_international = students_got_international + 1

            # The student matched at least one other person on language
            if flag_language:
                students_got_language = students_got_language + 1

            # The student matched at least one other person on activity
            if flag_option:
                students_got_option = students_got_option + 1

            # Find the highest priority that the student managed to get
            for i in range(5):
                # If at any point, they default, ignore the rest of their opinions
                if not person.priority_list[i]:
                    break
                elif person.priority_list[i] == "Gender":
                    if flag_gender:
                        student_got_choice[i] = student_got_choice[i] + 1
                        break
                elif person.priority_list[i] == "International":
                    if flag_international:
                        student_got_choice[i] = student_got_choice[i] + 1
                        break
                elif person.priority_list[i] == "Language":
                    if flag_language:
                        student_got_choice[i] = student_got_choice[i] + 1
                        break
                elif person.priority_list[i] == "What They Want to Do":
                    if flag_option:
                        student_got_choice[i] = student_got_choice[i] + 1
                        break
                elif person.priority_list[i] == "Matching Time to Meet":
                    if flag_time:
                        student_got_choice[i] = student_got_choice[i] + 1
                        break

        # If any student flagged as a leader, the group has a leader
        if flag_leader:
            groups_got_leader += 1

    print(f"{students_take_survey} of students took the survey while {default_students} did not.\n"
          f"Groups who got leader: {100 * (groups_got_leader / num_groups)}%\n"
          f"Groups who got confidence: {100 * (num_groups_mix_confidence / num_groups)}%\n"
          f"Students who got gender match: {100 * (students_gender_match / students_want_gender_match)}%\n"
          f"Students who got time: {100 * (students_got_time / students_want_time)}%\n"
          f"Students who got international: {100 * (students_got_international / students_want_international)}%\n"
          f"Students who got language: {100 * (students_got_language / students_take_survey)}%\n"
          f"Students who got activity: {100 * (students_got_option / students_take_survey)}%\n"
          f"\n"
          f"First choice: {student_got_choice[0]}\n"
          f"Second choice: {student_got_choice[1]}\n"
          f"Third choice: {student_got_choice[2]}\n"
          f"Fourth choice: {student_got_choice[3]}\n"
          f"Fifth choice: {student_got_choice[4]}\n"
          f"No choice: {students_take_survey - sum(student_got_choice)}\n"
          f"\n"
          f"Groups that are valid: {100 * (num_valid_groups / num_groups)}%\n")
