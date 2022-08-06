import re

def reindex_essay_questions(course, quiz, question_index):
    quiz_assignment = course.get_assignment(quiz.assignment_id)
    quiz_submissions = quiz_assignment.get_submissions(include="submission_history")
    quiz_filtered_submissions = [submission for submission in quiz_submissions if submission.submitted_at is not None]

    for question_key, question in question_index.items():
        question_type = question["question_type"]
        if question_type != "essay_question" and question_type != "fill_in_multiple_blanks_question":
            continue

        question_id = question["id"]
        reindexed_dict = {}
        question_index[question_key] = reindexed_dict

        # TODO: Account for people submitting twice (Keep latest using submission.attempt)
        for submission in quiz_filtered_submissions:
            # TODO: Check to make sure submission_history is always a single item
            submitter_id = submission.user_id
            submission_details = submission.submission_history[0]["submission_data"]
            for answer in submission_details:
                if str(answer["question_id"]) == question_id:
                    reindexed_dict[submitter_id] = answer
                    break

    print("===== Reindexed Essay Questions ======")


def index_questions(course, quiz, config):
    statistics = list(quiz.get_statistics())[0]
    all_questions = statistics.question_statistics

    # Returns this object with None replaced with the corresponding item from all_questions
    question_index = {
        "pronouns_select": None,
        "pronouns_other": None,
        "prefer_same_gender": None,
        "prefer_synchronous": None,
        "time_free": None,
        "prefer_communication_method": None,
        "prefer_communication_info": None,
        "prefer_to_lead": None,
        "prefer_other_international": None,
        "language_select": None,
        "language_other": None,
        "activity_select": None,
        "activity_specify": None,
        "priorities": None,
        "confidence": None
    }

    patterns = config["patterns"]
    for question in all_questions:
        for index_key in question_index.keys():
            # TODO: Fix possibility that multiple questions could match
            if re.search(patterns[index_key], question["question_text"]):
                question_index[index_key] = question
                continue

        # Warning: No matches found for this question
        if question not in question_index.values():
            print("No Match for Question:")
            print(question["question_text"])

    print("===== Question Indexing Complete =====")
    print("===== See Missed Questions Above =====")

    # Change the format of free response (essay_question) questions by replacing their key: values
    # with responses instead of useless data
    # Modifies question_index directly
    reindex_essay_questions(course, quiz, question_index)

    return question_index