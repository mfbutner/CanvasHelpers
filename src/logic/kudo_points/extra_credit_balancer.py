import canvasapi
import datetime


def create_extra_credit_balancer(course: canvasapi.course.Course,
                                 assignment_group: canvasapi.assignment.AssignmentGroup) -> canvasapi.assignment.Assignment:
    if not hasattr(assignment_group, 'assignments'):
        assignment_group = course.get_assignment_group(assignment_group.id, include=['assignments'])

    total_points = 0

    for assignment in assignment_group.assignments:
        total_points += assignment['points_possible']

    students = list(course.get_multiple_submissions(student_ids=['all'],
                                               assignment_ids=[assignment['id'] for assignment in
                                                               assignment_group.assignments],
                                               grouped=True))
    point_map = dict()
    for student in students:
        student_total = 0
        for submission in student.submissions:
            student_total += submission.entered_score if submission.entered_score is not None else 0
        point_map[student.user_id] = min(total_points - student_total, 0)

    now = datetime.datetime.now()
    balancer = course.create_assignment(assignment={
        'name': f'{assignment_group.name} Balancer',
        'description': 'How many Kudo Points you received this week.',
        'position': len(assignment_group.assignments),  # maybe + 1?
        'assignment_group_id': assignment_group.id,
        'submission_types': ['none'],
        'points_possible': 0,
        'due_at': now.isoformat(),
        'lock_at': now.isoformat(),
        'unlock_at': now.isoformat(),
        'published': True
    })
    balancer.submissions_bulk_update(grade_data={student_id: {'posted_grade': grade}
                                                 for student_id, grade in point_map.items()})
    return balancer
