import canvasapi
import datetime
from typing import Dict


def evaluate_kudo_point_giving_quiz(course: canvasapi.course.Course,
                                    kudo_point_assignment_group: canvasapi.assignment.AssignmentGroup,
                                    assignment_name: str,
                                    assignment_points: float,
                                    destination_assignment_group: canvasapi.assignment.AssignmentGroup,
                                    ) -> canvasapi.assignment.Assignment:
    # if user forgot to include the assignments in the assignment group
    if not hasattr(kudo_point_assignment_group, 'assignments'):
        kudo_point_assignment_group = course.get_assignment_group(kudo_point_assignment_group.id,
                                                                  include=['assignments'],
                                                                  exclude_assignment_submission_types=(
                                                                      'discussion_topic', 'wiki_page', 'external_tool'))

    if not hasattr(destination_assignment_group, 'assignments'):
        destination_assignment_group = course.get_assignment_group(destination_assignment_group.id,
                                                                   include=['assignments'])

    point_map = _count_points(course, kudo_point_assignment_group)
    evaluation_assignment = _create_evaluation_assignment(assignment_name, assignment_points, course,
                                                          destination_assignment_group)

    evaluation_assignment.submissions_bulk_update(grade_data={student_id: {'posted_grade': grade}
                                                              for student_id, grade in point_map.items()})
    return evaluation_assignment


def _count_points(course: canvasapi.course.Course,
                 kudo_point_assignment_group: canvasapi.assignment.AssignmentGroup) -> Dict[int, float]:
    point_map = {user.id: 0 for user in course.get_users(enrollment_type=['student'])}
    for assignment in kudo_point_assignment_group.assignments:
        if 'online_quiz' in assignment['submission_types']:
            quiz = course.get_quiz(assignment['quiz_id'])  # TODO: Check if this can be replaced with class creation
            stats = list(quiz.get_statistics())[0]  # there should always be a single element in this list
            for question_stats in stats.question_statistics:
                # last answer means don't give points so don't look at it
                for answer in question_stats['answers'][:-1]:
                    if answer['responses'] > 0:  # user selected this choice
                        point_map[(int(answer['text']))] += 1  # this is the person the student awarded the point to
                        break  # user can only select one answer so stop looking after it is found
    return point_map


def _create_evaluation_assignment(assignment_name: str, assignment_points: float,
                                 course: canvasapi.course.Course,
                                 destination_assignment_group: canvasapi.assignment.AssignmentGroup) -> canvasapi.assignment.Assignment:
    now = datetime.datetime.now()
    return course.create_assignment(assignment={
        'name': assignment_name,
        'description': 'How many Kudo Points you received this week.',
        'position': len(destination_assignment_group.assignments),  # maybe + 1?
        'assignment_group_id': destination_assignment_group.id,
        'submission_types': ['none'],
        'points_possible': assignment_points,
        'due_at': now.isoformat(),
        'lock_at': now.isoformat(),
        'unlock_at': now.isoformat(),
        'published': True
    })
