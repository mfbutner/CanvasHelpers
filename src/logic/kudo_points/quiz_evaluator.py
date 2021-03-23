import canvasapi
import datetime
from typing import Dict, List, Set

CanvasUserId = int
Score = float


def evaluate_kudo_point_giving_quiz(course: canvasapi.course.Course,
                                    kudo_point_assignment: canvasapi.assignment.Assignment,
                                    group_category: canvasapi.group.GroupCategory,
                                    evaluation_assignment_name: str,
                                    evaluation_assignment_points: float,
                                    evaluation_assignment_group: canvasapi.assignment.AssignmentGroup) -> canvasapi.assignment.Assignment:
    # if user forgot to include the assignments in the assignment group
    if not hasattr(evaluation_assignment_group, 'assignments'):
        # get the assignments in the assignment group
        evaluation_assignment_group = course.get_assignment_group(evaluation_assignment_group.id,
                                                                  include=['assignments'])

        # try:
        point_map = _count_points(course, kudo_point_assignment, group_category)
        evaluation_assignment = _create_evaluation_assignment(evaluation_assignment_name, evaluation_assignment_points,
                                                              course,
                                                              evaluation_assignment_group)
        progress = evaluation_assignment.submissions_bulk_update(grade_data={student_id: {'posted_grade': grade}
                                                                             for student_id, grade in
                                                                             point_map.items()})
        return evaluation_assignment, progress
    # except ValueError as e:
    #     print(e)


def _count_points(course: canvasapi.course.Course,
                  kudo_point_assignment: canvasapi.assignment.Assignment,
                  group_category: canvasapi.group.GroupCategory) -> Dict[CanvasUserId, Score]:
    # everyone starts with 0 points
    point_map = {user.id: 0 for user in course.get_users(enrollment_type=['student'])}

    # find out which group each student is in
    group_memberships = get_group_memberships(group_category)

    if 'online_quiz' in kudo_point_assignment.submission_types:
        quiz = course.get_quiz(kudo_point_assignment.quiz_id)  # TODO: Check if this can be replaced with class creation

        stats = list(quiz.get_statistics())[0]  # there should always be a single element in this list
        for question_stats in stats.question_statistics:
            for answer in question_stats['answers']:
                # can only award points to students that are still in the class
                try:
                    students_awarded_points = [int(student_id) for student_id in answer['text'].split(',') if
                                               int(student_id) in point_map]
                except ValueError:  # skip responses that don't correspond to students
                    continue
                for student_receiving_points in students_awarded_points:
                    for student_giving_points in answer['user_ids']:
                        _give_points(int(student_giving_points), student_receiving_points, point_map, group_memberships)
        return point_map
    else:
        raise ValueError(f'{kudo_point_assignment} is not an online quiz. Cannot give points for this assignment.')


def _give_points(student_giving_points: CanvasUserId, student_receiving_points: CanvasUserId,
                 point_map: Dict[CanvasUserId, Score],
                 group_memberships: Dict[CanvasUserId, Set[CanvasUserId]]) -> None:
    """

    :param student_giving_points: The id of the student giving the points
    :param student_receiving_points: The student getting the point
    :param point_map: The dictionary mapping students to their score on this assignment
    :param group_memberships: a dictionary mapping students to the people that are in their group
    :return: None. Instead group point_map is updated with the point if the point can be given
    """

    # the student receiving the point must still be in the class and
    # they can't be giving the point to themselves and
    # the student giving the point must not be in the class anymore(because now we can't track which group they were in)
    # or (the student giving the point must be in a group and be in the same group as the student receiving the point)
    if (student_receiving_points in point_map and
            student_receiving_points != student_giving_points and
            student_giving_points not in point_map or
            (student_giving_points in group_memberships and
             student_receiving_points in group_memberships[student_giving_points])):
        point_map[student_receiving_points] += 1


def get_group_memberships(group_category: canvasapi.group.GroupCategory) -> \
        Dict[CanvasUserId, Set[CanvasUserId]]:
    """
    Get a mapping for each student to the members of the group they are in
    :param group_category: the group category to get the memberships of
    :return: Dictionary of CanvasUserId to List of the members that are in their group
    """
    user_to_group_map = {}
    for group in group_category.get_groups():
        members = {member.user_id for member in group.get_memberships(filter_states=('accepted',))}
        for member in members:
            user_to_group_map[member] = members  # maybe this should be a copy. not sure though.
    return user_to_group_map


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
