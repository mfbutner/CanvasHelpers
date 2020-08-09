import sys
import re
import argparse
import datetime
import canvasapi
from typing import List
from .group import Group
from src.utilities.str_helpers import str_equal, str_starts_with


def configure_subparser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    """
    Add in a subparser to process kudo poing giving assignment creation
    :param subparsers: subparsers to add this subparser to
    :return: the argument parser created to process kudo poing giving assignment creation
    """
    parser = subparsers.add_parser('kudo_point_giving_assignment_creator',
                                   description='Create an individual assignment for each student in a group set to '
                                               'allow students in a group to award points to other members in their '
                                               'group points.')

    parser.add_argument('-group_set',
                        dest='group+set',
                        required=True,
                        help='The name of the group set you want to generate the Kudo Point Giving assignment for.')
    update_or_create_assignment_group = parser.add_mutually_exclusive_group(required=True)
    update_or_create_assignment_group.add_argument('-assignment_group',
                                                   dest='assignment_group',
                                                   required=True,
                                                   help='The name of the assignment group for the '
                                                        'Kudo Point Giving assignments to be created under.')
    update_or_create_assignment_group.add_argument('-create_assignment_group',
                                                   dest='create_assignment_group',
                                                   help='The name of the NEW assignment group to create')

    parser.add_argument('-due_date',
                        dest='due_date',
                        required=True,
                        type=datetime.datetime.fromisoformat,
                        help='The date and time that the assignment is due in ISO Format: YYYY-MM-DDTHH:MM.'
                             'For example, 2020-5-10T20:32 would make the assignment due on May 5th, 2020 at 8:32 PM'
                        )
    parser.add_argument('-unlock_date',
                        dest='unlock_date',
                        type=datetime.datetime.fromisoformat,
                        default=datetime.datetime.now(),
                        help='The date the assignment should unlock. '
                             'If not specified the assignment is made immediately available to students')
    parser.add_argument('-late_days',
                        dest='late_days',
                        type=int,
                        default=0,
                        help='The number of days an assignment can be turned in late. '
                             'By default there are no late days.')
    parser.add_argument('-kudo_points',
                        dest='kudo_points',
                        type=int,
                        default=2,
                        help='The number of Kudo Points each student can give to another. '
                             'By default each student can give 2.')

    parser.add_argument('-respect_case',
                        dest='ignore_case',
                        metavar='respect_case',
                        action='store_true',
                        help='If set, the case of group sets and assignment group names will be respected when '
                             'attempting to find a match.')

    parser.set_defaults(exe=create_kudo_point_giving_assignments)

    return parser


def create_kudo_point_giving_assignments(canvas_key: str, course_id: int, canvas_url: str,
                                         group_set_name: str, assignment_group_name: str,
                                         kudo_points: int,
                                         due_date: datetime.datetime, unlock_date: datetime.datetime,
                                         lock_date: datetime.datetime, ignore_case: bool = True):
    canvas_connection = canvasapi.Canvas(canvas_url, canvas_key)
    course = canvas_connection.get_course(course_id)
    group_categories = course.get_group_categories()
    assignment_group = locate_assignment_group(assignment_group_name, course, ignore_case)


# def locate_group_category(group_category_name: str, course: canvasapi.course.Course,
#                             ignore_case: bool = True):
#     group_categories = list(course.get_group_categories())
#     for group_category in group_categories:
#         if



def locate_assignment_group(assignment_group_name: str, course: canvasapi.course.Course,
                            ignore_case: bool = True) -> canvasapi.assignment.AssignmentGroup:
    assignment_groups = list(course.get_assignment_groups())
    for assignment_group in assignment_groups:
        if str_equal(assignment_group_name, assignment_group.name, ignore_case, ignore_whitespace=True):
            return assignment_group
    return resolve_missing_assignment_group(assignment_group_name, assignment_groups, course, ignore_case)


def resolve_missing_assignment_group(assignment_group_name: str,
                                     assignment_groups: List[canvasapi.assignment.AssignmentGroup],
                                     course: canvasapi.course.Course,
                                     ignore_case: bool = True) -> canvasapi.assignment.AssignmentGroup:
    while True:
        print(f'Could not locate an assignment group named "{assignment_group_name}"\n'
              f'The groups in your class are')
        for pos, group in enumerate(assignment_groups):
            print(f'\t{pos}. {group}')
        choice = input(f'Enter the number of the group you want to add the assignments to or CREATE if you want '
                       f'to create a new assignment group named {assignment_group_name}').strip().lower()
        err_msg = f'{choice} is not a value between 0 and {len(assignment_groups) - 1} or CREATE. Please try again.'
        if 'create'.startswith(choice):
            return create_assignment_group(assignment_group_name, course, ignore_case)
        else:
            try:
                choice = int(choice)
                if 0 <= choice < len(assignment_groups):
                    return assignment_groups[choice]
                else:
                    print(err_msg)
            except ValueError:
                print(err_msg)


def create_assignment_group(assignment_group_name: str,
                            course: canvasapi.course.Course,
                            ignore_case: bool = True) -> canvasapi.assignment.AssignmentGroup:
    assignment_groups = list(course.get_assignment_groups())

    number_of_times_named_used = sum(
        (str_starts_with(assignment_group.name, assignment_group_name, ignore_case, ignore_whitespace=True)
         for assignment_group in assignment_groups)
    )
    assignment_group_name += '' if number_of_times_named_used == 0 else f'({number_of_times_named_used})'

    return course.create_assignment_group(
        name=assignment_group_name,
        position=len(assignment_groups),
        group_weight=0
    )



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
                                           number_of_kudo_points: int = 2) -> None:
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
