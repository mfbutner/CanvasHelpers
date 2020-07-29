import sys
import canvasapi
from .group import Group
from datetime import datetime, timedelta


def create_kudo_point_answers(user, group: Group):
    answers = [
        {
            'answer_text': member.name,
            'answer_weight': 1
        } for member in group.members if user.id != member.id
    ]
    answers.append({
        'answer_text': 'I do not want to give this Kudo Point to anyone.',
        'answer_weight': 1
    })
    return answers


def create_kudo_point_giving_quiz_for_user(user: canvasapi.user.User,
                                           group: Group,
                                           course: canvasapi.course.Course,
                                           unlock_date: datetime,
                                           due_date: datetime,
                                           late_days: int = 0,
                                           number_of_kudo_points: int = 2 ) -> None:
    the_override = {
        'student_ids': [user.id],
        'title': f'Override for {user}',
        'due_at': due_date.isoformat(),
        'unlock_at': unlock_date,
        'lock_at': due_date + timedelta(days=late_days)
    }
    the_quiz = course.create_quiz({
        'title': f"{user.name}'s Kudo Point Givings for {group.name}",
        'quiz_type': 'assignment',
        'allowed_attempts': 10,
        'scoring_policy': 'keep_latest',
        'published': False,
        'show_correct_answers': False,
        'only_visible_to_overrides': True,
    })

    # create the questions for this quiz.
    # the questions in this case are who the student wants to give the Kudo points to
    answers = create_kudo_point_answers(user, group)
    for point in range(1, number_of_kudo_points + 1):
        question = {
            'question_name': f'Kudo Point {point}',
            'question_text': 'Who do you want to give this Kudo Point to?',
            'question_type': 'multiple_choice_question',
            'answers': answers
        }
        the_quiz.create_question(question=question)

    # This part is needed to make sure the assignment only shows up to
    # the single person we want to assign it to
    # for some reason it has to be set for both the quiz and the assignment
    the_assignment = course.get_assignment(the_quiz.assignment_id)
    the_assignment = the_assignment.edit(assignment={
        'grading_type': 'not_graded',
        'omit_from_final_grade': True,
        'only_visible_to_overrides': True,
        'assignment_overrides': [the_override],
        'published': True
    })
    print(the_quiz)


def main():
    canvas_key = sys.argv[1]
    course_id = int(sys.argv[2])
    canvas_url = 'https://canvas.ucdavis.edu'
    canvas_connection = canvasapi.Canvas(canvas_url, canvas_key)
    course = canvas_connection.get_course(course_id)
    group_categories = course.get_group_categories()

    for category in group_categories:
        if category.name == 'Kudo Point Giving Testing':
            print(category)
            for group in category.get_groups():
                group = Group(group)
                if group.name == 'Accessible':
                    print(f'\t{group}')
                    for user in group.members:
                        print(f'\t\t{user}')
                        create_kudo_point_giving_quiz_for_user(user, group, course, 2)
                    # return


if __name__ == '__main__':
    main()
