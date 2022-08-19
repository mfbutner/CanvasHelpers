from StableGrouping.parsing.indexQuestions import index_questions
from StableGrouping.shared.constants import NO_ANSWER, PreferGender, PreferAsync, PreferInternational, Confident
from StableGrouping.shared.studentClass import Student


def parse_students(canvas_students):
    all_students = {}
    for student in canvas_students:
        if not hasattr(student, "email"):
            continue

        student_instance = Student()
        student_instance.id_num = student.id
        student_instance.name = student.name
        name = student.sortable_name.split(",")
        if len(name) == 1:
            student_instance.firstName = name[0]
        elif len(name) != 0:
            student_instance.firstName = name[1]
            student_instance.lastName = name[0]
        student_instance.schoolEmail = student.email
        all_students[student.id] = student_instance

    return all_students


def filter_students_submitted(all_students, quiz_submissions):
    students_submitted = {}
    for submission in quiz_submissions:
        for student in all_students.values():
            # Side effect: If the student is not found in all_students, the submission is ignored
            # The student either may be no longer enrolled or something has gone wrong
            if student.id_num != submission.user_id:
                continue

            students_submitted[student.id_num] = student
            break
    return students_submitted


def remove_any_tags(source_str):
    first_close = source_str.find('>')
    end_close = source_str.rfind('<')
    return source_str[first_close + 1:end_close]


def parse_submissions(students_submitted, course, quiz, config):
    question_index = index_questions(course, quiz, config)
    default_student = Student()

    for answer in question_index["pronouns_select"]["answers"]:
        answer_text = answer["text"]
        if answer_text == NO_ANSWER:
            continue

        for user_id in answer["user_ids"]:
            students_submitted[user_id].pronouns = answer_text

    for answer in question_index["prefer_same_gender"]["answers"]:
        answer_text = answer["text"]
        if answer_text == NO_ANSWER:
            continue

        for user_id in answer["user_ids"]:
            if answer_text == "I would prefer another person who as the same pronouns as I do.":
                students_submitted[user_id].prefer_same = PreferGender.same_pronouns.value
            elif answer_text == "I would prefer another person who does not have the same pronouns as I do.":
                students_submitted[user_id].prefer_same = PreferGender.diff_pronouns.value
            else:
                students_submitted[user_id].prefer_same = PreferGender.dont_care_pronouns.value

    # No preference (Default)
    for answer in question_index["prefer_synchronous"]["answers"]:
        answer_text = answer["text"]
        if answer_text == NO_ANSWER:
            continue

        for user_id in answer["user_ids"]:
            if answer_text == "Synchronously":
                students_submitted[user_id].prefer_async = PreferAsync.like_sync.value
            elif answer_text == "Asynchronously":
                students_submitted[user_id].prefer_async = PreferAsync.like_async.value
            else:
                students_submitted[user_id].prefer_async = PreferAsync.dont_care_async.value

    for answer in question_index["prefer_to_lead"]["answers"]:
        answer_text = answer["text"]
        if answer_text == NO_ANSWER:
            continue

        for user_id in answer["user_ids"]:
            students_submitted[user_id].prefer_leader = (answer_text == "I like to lead.")

    # Not international (Default)
    for answer in question_index["prefer_other_international"]["answers"]:
        answer_text = answer["text"]
        if answer_text == NO_ANSWER:
            continue

        for user_id in answer["user_ids"]:
            if answer_text == "I am not an international student.":
                students_submitted[user_id].international = PreferInternational.not_international.value
            elif answer_text == "I would like to be placed with another international student.":
                students_submitted[user_id].international = PreferInternational.prefer_international_partner.value
            else:
                students_submitted[user_id].international = PreferInternational.dont_care_international.value

    for answer in question_index["activity_select"]["answers"]:
        answer_text = answer["text"]
        if answer_text == NO_ANSWER:
            continue

        for user_id in answer["user_ids"]:
            students_submitted[user_id].activity_choice = answer_text

    # Have some questions (Default)
    for answer in question_index["confidence"]["answers"]:
        answer_text = answer["text"]
        if answer_text == NO_ANSWER:
            continue

        for user_id in answer["user_ids"]:
            if answer_text == "I'm confident.":
                students_submitted[user_id].confidence = Confident.is_confident.value
            elif answer_text == "I could really use some help.":
                students_submitted[user_id].confidence = Confident.not_confident.value
            else:
                students_submitted[user_id].confidence = Confident.default_confidence.value

    # time_free
    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for answer in question_index["time_free"]["answer_sets"]:
        answer_text = answer["text"]
        day_text = answer_text[0:3]
        if day_text in days_of_week:
            first_index = days_of_week.index(day_text)
            second_index = int(answer_text[3]) - 1
            for response in answer["answers"]:
                available = response["correct"]
                if not available:
                    continue

                for user_id in response["user_ids"]:
                    students_submitted[user_id].meeting_times[first_index][second_index] = available

    # priorities
    priority_list = ["top", "second", "third", "fourth", "fifth"]
    for answer in question_index["priorities"]["answer_sets"]:
        answer_text = answer["text"]
        if answer_text in priority_list:
            index = priority_list.index(answer["text"])
            for priority in answer["answers"]:
                priority_text = priority["text"]
                if priority_text == NO_ANSWER:
                    continue

                for user_id in priority["user_ids"]:
                    students_submitted[user_id].priority_list[index] = priority_text

    # language_select
    for answer in question_index["language_select"]["answer_sets"][0]["answers"]:
        answer_text = answer["text"]
        if answer_text == NO_ANSWER:
            continue

        for user_id in answer["user_ids"]:
            students_submitted[user_id].language = answer_text

    # pronouns_other
    for user_id, answer in question_index["pronouns_other"].items():
        student = students_submitted[user_id]
        if student.pronouns == "Not Included" or student.pronouns == default_student.pronouns:
            pronouns = remove_any_tags(answer["text"])
            if len(pronouns):
                student.pronouns = pronouns

    # language_other
    for user_id, answer in question_index["language_other"].items():
        student = students_submitted[user_id]
        if student.language == "Not included" or student.language == default_student.language:
            language = remove_any_tags(answer["text"])
            if len(language):
                student.language = language

    # prefer_communication_method
    communication_method_dict = {
        "Discord": 0,
        "Text/Phone Number": 1,
        "Email": 2,
        "Canvas Groups": 3
    }
    for answer_set in question_index["prefer_communication_method"]["answers"]:
        answer_text = answer_set["text"]
        if answer_text not in communication_method_dict:
            continue

        contact_index = communication_method_dict[answer_text]
        for user_id in answer_set["user_ids"]:
            students_submitted[user_id].contact_preference[contact_index] = True

    # prefer_communication_info
    communication_info_keys = {
        "answer_for_Discord": 0,
        "answer_for_Phone": 1,
        "answer_for_Email": 2
    }
    for user_id, answer in question_index["prefer_communication_info"].items():
        for info_key, info_index in communication_info_keys.items():
            if info_key in answer:
                students_submitted[user_id].contact_information[info_index] = answer[info_key]

    # activity_specify
    for user_id, answer in question_index["activity_specify"].items():
        answer_text = remove_any_tags(answer["text"])
        if len(answer_text):
            students_submitted[user_id].free_response = answer_text

    # Returns nothing. Modifies students_submitted by filling their respective fields
    return