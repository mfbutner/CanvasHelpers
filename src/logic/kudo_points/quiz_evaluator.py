import canvasapi
import datetime


def evaluate_kudo_point_giving_quiz(course: canvasapi.course.Course,
                                    kudo_point_assignment_group: canvasapi.assignment.AssignmentGroup,
                                    assignment_name: str,
                                    assignment_points: float,
                                    destination_assignment_group: canvasapi.assignment.AssignmentGroup,
                                    ) -> None:
    #assignment_ids = [assignment['id'] for assignment in kudo_point_assignment_group.assignments]
    for assignment in kudo_point_assignment_group.assignments:
        if 'online_quiz' in assignment['submission_types']:
            quiz = course.get_quiz(assignment['quiz_id'])
            stats = list(quiz.get_statistics())[0] #TODO check what happens when there are no responses
            for question in stats.question_statistics:
                # last answer means don't give points so don't look at it
                for answer in question['answers'][:-1]:
                    if answer['responses'] > 0: # user selected this choice





    evaluation_assignment = create_evaluation_assignment(assignment_name, assignment_points, course,
                                                         destination_assignment_group)


def create_evaluation_assignment(assignment_name, assignment_points, course, destination_assignment_group):
    now = datetime.datetime.now()
    return course.create_assignment(assignment={
        'name': assignment_name,
        'description': 'How many Kudo Points you received this week.',
        'position': len(destination_assignment_group.assignments),  # maybe + 1?
        'submission_types': ['none'],
        'points_possible': assignment_points,
        'due_at': now.isoformat(),
        'lock_at': now.isoformat(),
        'unlock_at': now.isoformat(),
        'published': False
    })
