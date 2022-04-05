import os
import canvasapi
import datetime
import time
import sys
from src.logic.groups.groups import download_groups_to_csv, create_groups_from_csv, transform_study_group_matches, \
    update_group_names_to_reflect_membership
from src.logic.kudo_points.quiz_evaluator import evaluate_kudo_point_giving_quiz, get_group_memberships
from src.logic.kudo_points.extra_credit_balancer import create_extra_credit_balancer
from src.logic.download_users import download_users_to_csv
from src.logic.qualtrics import get_missing_qualtrics_users, upload_survey_completion
from src.logic.assignments import download_assignment_info
from src.logic.kudo_points.giving_quiz_creator.kudo_point_giving_quiz import KudoPointGivingQuiz
from src.logic.assignments.download_assignment_info import download_assignment_info



# https://canvas.ucdavis.edu/
# ECS 36A
# Upload File: D:\DDownloads\ECS 36ACanvasGradeUpload.csv
# Assignment Groups: 4, 5, 6, 7, 8, 9, 10, 11, 12
# CSV Columns: 1, 2, 5, 0, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 23, 25, 29, 26, 27, 28



canvas_connection = canvasapi.Canvas('https://canvas.ucdavis.edu/',
                                     sys.argv[1])

course = canvas_connection.get_course(1599, include=['term'])

assignment_groups = list(course.get_assignment_groups(include='assignments',
                                                      exclude_assignment_submission_types=(
                                                          'discussion_topic', 'wiki_page', 'external_tool')))

ecs36b = canvas_connection.get_course(677644, include=['term'])
ecs50 = canvas_connection.get_course(664353, include=['term'])
# ecs36a = canvas_connection.get_course(632679, include=['term'])

# ecs154a = canvas_connection.get_course(657719, include=['term'])
courses = [ecs36b, ecs50]


def test_late_policy():
    ecs154a = canvas_connection.get_course(471392)
    ecs154a.create_late_policy(late_policy={'missing_submission_deduction_enabled': True,
                                            'missing_submission_deduction': 100,
                                            'late_submission_deduction_enabled': False})
    late_policy = ecs154a.get_late_policy()
    print(late_policy)


def set_homework_group_evaluations_to100():
    courses_info = [
        {'course': ecs36a,
         'assignment_ids': [739581, 739567]},
        {'course': ecs32b,
         'assignment_ids': [764700, 764701]}
    ]
    for course_info in courses_info:
        course = course_info['course']
        for assignment_id in course_info['assignment_ids']:
            assignment = course.get_assignment(assignment_id)
            set_grades_to_100(course, assignment)

    # ecs50 = canvas_connection.get_course(487368)
    # ecs154a = canvas_connection.get_course(471392)
    # set_grades_to_100(ecs154a, ecs154a.get_assignment(602441))
    # set_grades_to_100(ecs50, ecs50.get_assignment(602597))


def set_grades_to_100(course, assignment):
    students = course.get_users(enrollment_type=['student'])
    grades = {student.id: {'posted_grade': assignment.points_possible} for student in students}
    assignment.submissions_bulk_update(grade_data=grades)


def ecs50_kudo_point_evaluation():
    ecs50 = canvas_connection.get_course(487368)
    kudo_point_giving_assignment_group_ids = 305590, 306643, 307445, 307446, 307450, 307451, 316612, 316613
    kudo_point_assignment_names = ('Group 1 Week 1 Kudo Point Results',
                                   'Group 1 Week 2 Kudo Point Results',
                                   'Group 2 Week 1 Kudo Point Results',
                                   'Group 2 Week 2 Kudo Point Results',
                                   'Group 3 Week 1 Kudo Point Results',
                                   'Group 3 Week 2 Kudo Point Results',
                                   'Group 4 Week 1 Kudo Point Results',
                                   'Group 4 Week 2 Kudo Point Results')
    assignment_points = 2
    dest_assignment_group = ecs50.get_assignment_group(301421)  # Kudo Point Extra Credit
    for giving_assignment_group_id, result_name in zip(kudo_point_giving_assignment_group_ids,
                                                       kudo_point_assignment_names):
        src_assignment_group = ecs50.get_assignment_group(giving_assignment_group_id,
                                                          include='assignments',
                                                          exclude_assignment_submission_types=(
                                                              'discussion_topic', 'wiki_page', 'external_tool'))

        evaluate_kudo_point_giving_quiz(ecs50, src_assignment_group, result_name, assignment_points,
                                        dest_assignment_group, )


def balance_ecs50_kudo_points():
    ecs50 = canvas_connection.get_course(487368)
    dest_assignment_group = ecs50.get_assignment_group(301421)  # Kudo Point Extra Credit
    create_extra_credit_balancer(ecs50, dest_assignment_group)  # Kudo Point Extra Credit)


def ecs154a_kudo_point_evaluation():
    ecs154a = canvas_connection.get_course(471392)
    kudo_point_giving_assignment_group_ids = 305276, 306636, 306637, 306638, 312518, 306640, 316615, 316616

    kudo_point_assignment_names = ('Group 1 Week 1 Kudo Point Results',
                                   'Group 1 Week 2 Kudo Point Results',
                                   'Group 2 Week 1 Kudo Point Results',
                                   'Group 2 Week 2 Kudo Point Results',
                                   'Group 3 Week 1 Kudo Point Results',
                                   'Group 3 Week 2 Kudo Point Results',
                                   'Group 4 Week 1 Kudo Point Results',
                                   'Group 4 Week 2 Kudo Point Results')
    assignment_points = 2
    dest_assignment_group = ecs154a.get_assignment_group(305275)  # Kudo Point Extra Credit
    for giving_assignment_group_id, result_name in zip(kudo_point_giving_assignment_group_ids,
                                                       kudo_point_assignment_names):
        src_assignment_group = ecs154a.get_assignment_group(giving_assignment_group_id,
                                                            include='assignments',
                                                            exclude_assignment_submission_types=(
                                                                'discussion_topic', 'wiki_page', 'external_tool'))

        evaluate_kudo_point_giving_quiz(ecs154a, src_assignment_group, result_name, assignment_points,
                                        dest_assignment_group, )


def balance_ecs154a_kudo_points():
    ecs154a = canvas_connection.get_course(471392)
    dest_assignment_group = ecs154a.get_assignment_group(305275)  # Kudo Point Extra Credit
    create_extra_credit_balancer(ecs154a, dest_assignment_group)  # Kudo Point Extra Credit)


def upload_ecs_36a_survey_completion():
    course = ecs36a
    canvas_survey_assignment_ids = 808040, 808063, 808064

    base_dir = 'D:\\GradeTransfers\\ECS36AWinter2022'
    csv_files = os.listdir(base_dir)
    csv_files.sort()
    print(csv_files)
    students = course.get_users(enrollment_type=['student'])
    for assignment_id, csv_file in zip(canvas_survey_assignment_ids, csv_files):
        print(f'\n{csv_file}')
        csv_file = os.path.join(base_dir, csv_file)
        canvas_assignment = course.get_assignment(assignment_id)
        upload_survey_completion(canvas_assignment, students, csv_file)


def upload_ecs_154a_survey_completion():
    course = ecs154a
    canvas_survey_assignment_ids = 817231, 817244, 817245

    base_dir = 'D:\\GradeTransfers\\ECS154AWinter2022'
    csv_files = os.listdir(base_dir)
    csv_files.sort()
    print(csv_files)
    students = course.get_users(enrollment_type=['student'])
    for assignment_id, csv_file in zip(canvas_survey_assignment_ids, csv_files):
        print(f'\n{csv_file}')
        csv_file = os.path.join(base_dir, csv_file)
        canvas_assignment = course.get_assignment(assignment_id)
        upload_survey_completion(canvas_assignment, students, csv_file)


def test_upload_survey_completion():
    sandbox = canvas_connection.get_course(1599)
    test_assignment = sandbox.get_assignment(601416)
    students = sandbox.get_users(enrollment_type=['student'])
    upload_survey_completion(test_assignment, students,
                             'D:\\DDownloads\\CanvasHelpers+Testing+Survey_December+21,+2020_16.24\\CanvasHelpers Testing Survey_December 21, 2020_16.24.csv')


def test_download_assignment_info():
    for course in courses:
        download_assignment_info.download_assignment_info(course, f'{course.name}_assignment_info.csv')


def test_kudo_point_creation():
    number_of_kudo_points = 2
    kudo_point_giving_group_ids = [469533, 469556]  # 36B, 50
    assignment_name = 'Kudo Point Giving Study Group 1 Week 2'
    # assignment_group = course.get_assignment_group(285318)  # Assignment Group Kudo Point Giving  (285318)
    weeks_into_the_quarter = datetime.timedelta(
        1 * 7)  # 1 was for this week change to 2 future me. Yes it really should be week 6 next time
    first_due_date_of_the_quarter = datetime.datetime(2022, 4, 4, 23, 59)
    first_open_date_of_the_quarter = datetime.datetime(2022, 4, 4, 00, 1)

    due_date = first_due_date_of_the_quarter + weeks_into_the_quarter
    close_date = due_date + datetime.timedelta(days=1)
    open_date = first_open_date_of_the_quarter + weeks_into_the_quarter

    now = datetime.datetime.now()
    one_hour_from_now = now + datetime.timedelta(hours=1)

    for course, assignment_group_id in zip(courses, kudo_point_giving_group_ids):
        assignment_group = course.get_assignment_group(assignment_group_id)
        quiz = KudoPointGivingQuiz(course, assignment_name, assignment_group, number_of_kudo_points, due_date,
                                   open_date,
                                   close_date)
        quiz.upload_to_canvas(course)

    # quiz_creator = KudoPointGivingQuiz(course, 'Kudo Points for All', assignment_group, number_of_kudo_points, one_hour_from_now, now,
    #                                   None)
    # quiz_creator.upload_to_canvas(course)


def look_at_quiz_statistics():
    quiz = course.get_quiz(83857)
    quiz_questions = list(quiz.get_questions())
    stats = list(quiz.get_statistics())
    print(stats)


def get_submissions_for_an_assignment_that_does_not_take_submissions():
    assignment = course.get_assignment(536205)
    subs = list(assignment.get_submissions())
    for sub in subs:
        print(sub)


def test_kudo_point_evaluation():
    src_assignment_group = course.get_assignment_group(377838,  # Assignment Group Kudo Point Giving  (377838)
                                                       include='assignments',
                                                       exclude_assignment_submission_types=(
                                                           'discussion_topic', 'wiki_page', 'external_tool'))

    kudo_point_giving_testing_group_category = canvas_connection.get_group_category(12584)
    # group_memberships = get_group_memberships(kudo_point_giving_testing_group_category)
    assignment_name = 'Kudo Point ALL Evaluation Test'
    assignment_points = 2
    dest_assignment_group = course.get_assignment_group(294590)  # Kudo Point Extra Credit
    assignment = course.get_assignment(616930)
    evaluate_kudo_point_giving_quiz(course, assignment, kudo_point_giving_testing_group_category, assignment_name,
                                    assignment_points, dest_assignment_group)


def test_balancer():
    dest_assignment_group = course.get_assignment_group(294590)  # Kudo Point Extra Credit
    create_extra_credit_balancer(course, dest_assignment_group)  # Kudo Point Extra Credit)


def test_download_users_to_csv():
    for course in courses:
        download_users_to_csv(course.name + '.csv', course)


def test_download_groups_to_csv():
    # ECS 50 First Study Groups (13712)
    # ECS 154A First Study Groups (13710)
    download_groups_to_csv(canvas_connection.get_group_category(13712), 'ecs50_group_1_downloads.csv')
    download_groups_to_csv(canvas_connection.get_group_category(13710), 'ecs154a_group_1_downloads.csv')


def test_get_missing_qualtrics_users():
    courses = [ecs36a, ecs154a]
    csv_paths = ['''D:\DDownloads\Winter_2022___36A_Students.csv''',
                 '''D:\DDownloads\Winter_2022___ECS_154A_Students.csv''']

    # ecs_36A_students = ecs36a.get_users(enrollment_type=['student'])
    # ecs_32B_students = ecs32b.get_users(enrollment_type=['student'])

    def printing(students, path_to_csv):
        missing_from_qualtrics, missing_from_canvas = get_missing_qualtrics_users(students, path_to_csv)

        print(f'Found on Qualtrics but not Canvas\n')
        for student in missing_from_canvas:
            print(f'{student.first_name} | {student.last_name} | {student.email}')

        print('\nFound on Canvas but not Qualtrics\n')
        for student in missing_from_qualtrics:
            last_name, first_name = student.sortable_name.split(',')

            print(f'{first_name} | {last_name}  | {student.email}')

    for course, csv_path in zip(courses, csv_paths):
        students = course.get_users(enrollment_type=['student'])
        print(f'-------------------------{course.name}-------------------------')
        printing(students, csv_path)
        print(f'-------------------------END-----------------------------------')

    # printing(ecs_36A_students, r'D:\DDownloads\ECS36A__Fall_2021_Students.csv')
    # printing(ecs_32B_students, r'D:\DDownloads\ECS32B__Fall_2021_Students.csv')


def test_update_group_names_to_reflect_memberships():
    for course in courses:
        for group_category in course.get_group_categories():
            update_group_names_to_reflect_membership(group_category, f'{group_category.name}: ')


def print_group_categories():
    for course in courses:
        print(course.name)
        for group_category in course.get_group_categories():
            print(f'\t{group_category}')


def test_download_assignment_info():
    for course in courses:
        download_assignment_info(course, f'{course.name}_AssignmentInfo.csv')


def true_kudo_point_evaluation():
    assignment_points = 2
    course_info = [
        {'course': ecs154a,
         'kudo_point_giving_assignment_group_id': 428415,
         'kudo_point_evaluation_group_id': 428416,
         'completion_statuses': []
         },

        {'course': ecs36a,
         'kudo_point_giving_assignment_group_id': 428413,
         'kudo_point_evaluation_group_id': 428414,
         'completion_statuses': []
         }

    ]

    for info in course_info:
        cur_course = info['course']
        kudo_point_giving_assignment_group = cur_course.get_assignment_group(
            info['kudo_point_giving_assignment_group_id'],
            include='assignments',
            exclude_assignment_submission_types=(
                'discussion_topic', 'wiki_page',
                'external_tool'))

        kudo_point_giving_assignment_group.assignments = [
            canvasapi.assignment.Assignment(kudo_point_giving_assignment_group._requester, assignment)
            for assignment in kudo_point_giving_assignment_group.assignments]

        kudo_point_giving_assignment_group.assignments.sort(
            key=lambda x: datetime.datetime.fromisoformat(x.due_at[:-1]))
        kudo_point_evaluation_group = cur_course.get_assignment_group(info['kudo_point_evaluation_group_id'])
        study_groups = sorted(cur_course.get_group_categories(), key=lambda x: x.created_at_date)

        for pos, giving_assignment in enumerate(kudo_point_giving_assignment_group.assignments):
            study_group = study_groups[pos // 2]  # study groups go for 2 weeks in a row
            evaluation_assignment_name = giving_assignment.name + ' - Results'
            assignment, progress = evaluate_kudo_point_giving_quiz(cur_course, giving_assignment, study_group,
                                                                   evaluation_assignment_name,
                                                                   assignment_points, kudo_point_evaluation_group)
            info['completion_statuses'].append((assignment, progress))

    print('Assignments uploading, waiting for grades to updated')
    while True:
        all_assignments_uploaded = True
        for info in course_info:
            for pos, (assignment, progress) in enumerate(info['completion_statuses']):
                print(info['course'].name)
                progress = progress.query()
                info['completion_statuses'][pos] = (assignment, progress)
                print(f'\t{assignment.name}. {progress.completion}% completed')
                if progress.workflow_state != 'completed':
                    all_assignments_uploaded = False
        if all_assignments_uploaded:
            break
        else:
            time.sleep(10)

    for info in course_info:
        cur_course = info['course']
        kudo_point_evaluation_group = cur_course.get_assignment_group(info['kudo_point_evaluation_group_id'])
        create_extra_credit_balancer(cur_course, kudo_point_evaluation_group)


def winter2021ecs36a_kudo_point_evaluation():
    cur_course = ecs36a
    kudo_point_giving_assignment_group_id = 330703
    kudo_point_evaluation_group_id = 339108
    assignment_points = 2
    kudo_point_giving_assignment_group = cur_course.get_assignment_group(kudo_point_giving_assignment_group_id,
                                                                         include='assignments',
                                                                         exclude_assignment_submission_types=(
                                                                             'discussion_topic', 'wiki_page',
                                                                             'external_tool'))
    kudo_point_evaluation_group = cur_course.get_assignment_group(kudo_point_evaluation_group_id)

    # kudo_point_giving_assignment_group.assignments = [
    #     canvasapi.assignment.Assignment(kudo_point_giving_assignment_group._requester, assignment)
    #     for assignment in kudo_point_giving_assignment_group.assignments]
    # kudo_point_giving_assignment_group.assignments.sort(key= lambda x: x.created_at_date)
    #
    # study_groups = sorted(cur_course.get_group_categories(), key=lambda x: x.created_at_date)
    #
    # completion_statuses = []
    #
    # for pos, giving_assignment in enumerate(kudo_point_giving_assignment_group.assignments):
    #     study_group = study_groups[pos // 2]  # study groups go for 2 weeks in a row
    #     evaluation_assignment_name = giving_assignment.name + ' - Results'
    #     assignment, progress = evaluate_kudo_point_giving_quiz(cur_course, giving_assignment,study_group,evaluation_assignment_name,
    #                                     assignment_points,kudo_point_evaluation_group)
    #     completion_statuses.append(progress)
    #
    # print('Assignments uploading, waiting for grades to updated')
    # while True:
    #     for pos, progress in enumerate(completion_statuses):
    #         progress = progress.query()
    #         completion_statuses[pos] = progress
    #         print(f'{pos}. {progress.completion}% completed')
    #     if all((progress.workflow_state == 'completed' for progress in completion_statuses)):
    #         break
    #     else:
    #         time.sleep(5)

    create_extra_credit_balancer(cur_course, kudo_point_evaluation_group)


def winter2021ecs154a_kudo_point_evaluation():
    cur_course = ecs154a
    kudo_point_giving_assignment_group_id = 330702
    kudo_point_evaluation_group_id = 343960
    assignment_points = 2
    kudo_point_giving_assignment_group = cur_course.get_assignment_group(kudo_point_giving_assignment_group_id,
                                                                         include='assignments',
                                                                         exclude_assignment_submission_types=(
                                                                             'discussion_topic', 'wiki_page',
                                                                             'external_tool'))
    kudo_point_evaluation_group = cur_course.get_assignment_group(kudo_point_evaluation_group_id)

    kudo_point_giving_assignment_group.assignments = [
        canvasapi.assignment.Assignment(kudo_point_giving_assignment_group._requester, assignment)
        for assignment in kudo_point_giving_assignment_group.assignments]
    kudo_point_giving_assignment_group.assignments.sort(key=lambda x: x.created_at_date)

    study_groups = sorted(cur_course.get_group_categories(), key=lambda x: x.created_at_date)

    completion_statuses = []

    for pos, giving_assignment in enumerate(kudo_point_giving_assignment_group.assignments):
        study_group = study_groups[pos // 2]  # study groups go for 2 weeks in a row
        evaluation_assignment_name = giving_assignment.name + ' - Results'
        assignment, progress = evaluate_kudo_point_giving_quiz(cur_course, giving_assignment, study_group,
                                                               evaluation_assignment_name,
                                                               assignment_points, kudo_point_evaluation_group)
        completion_statuses.append(progress)

    print('Assignments uploading, waiting for grades to updated')
    while True:
        for pos, progress in enumerate(completion_statuses):
            progress = progress.query()
            completion_statuses[pos] = progress
            print(f'{pos}. {progress.completion}% completed')
        if all((progress.workflow_state == 'completed' for progress in completion_statuses)):
            break
        else:
            time.sleep(5)

    create_extra_credit_balancer(cur_course, kudo_point_evaluation_group)


def main():
    # ones I normally use
    test_kudo_point_creation()
    # test_download_assignment_info()
    # test_download_users_to_csv()
    # test_update_group_names_to_reflect_memberships()
    # test_get_missing_qualtrics_users()
    # true_kudo_point_evaluation()
    # upload_ecs_36a_survey_completion()
    # upload_ecs_154a_survey_completion()

    # winter2021ecs36a_kudo_point_evaluation()
    # winter2021ecs154a_kudo_point_evaluation()

    # print_group_categories()
    # test_late_policy()
    # set_homework_group_evaluations_to100()
    # balance_ecs50_kudo_points()
    # balance_ecs154a_kudo_points()
    # ecs50_kudo_point_evaluation()
    # ecs154a_kudo_point_evaluation()

    # test_upload_survey_completion()
    # test_download_assignment_info()
    # look_at_quiz_statistics()

    # get_submissions_for_an_assignment_that_does_not_take_submissions()
    # test_kudo_point_evaluation()
    # test_balancer()

    # test_download_groups_to_csv()
    # ecs_154a =  canvas_connection.get_course(471392, include=['term'])
    # ecs_50 = canvas_connection.get_course(487368)
    # create_groups_from_csv(ecs_50, 'ecs50_study_groups_week1.csv', behavior='overwrite')
    # create_groups_from_csv(ecs_154a,'ecs154a_study_groups_week1.csv',behavior='overwrite')
    # transform_study_group_matches('D:/DDownloads/ECS50 Matches .csv', 'ecs50_study_groups_week1.csv','First Study Groups')


main()

# roles = ['teacher', 'ta', 'designer']
# courses = []
# for role in roles:
#     courses.extend(canvas_connection.get_courses(enrollment_type=role, include=['term']))
# for course in courses:
#     term = course.term['name'] if hasattr(course, 'term') else 'No Term'
#     print(f'{course.name} starts at {course.term["start_at"]} (ID: {course.term["id"]})in term {term}')


# term_dict = {'id': 46,
#              'name': 'Spring Quarter (SQ) 2018',
#              'start_at': '2017-03-28T07:00:00Z',
#              'end_at': '2023-06-15T07:00:00Z',
#              'created_at': '2017-08-31T15:56:15Z',
#              'workflow_state': 'active',
#              'grading_period_group_id': None}
# t = Term(term_dict)
# print(t)
# print(id(t))
# me = canvas_connection.get_current_user()
# courses = get_courses_enrolled_in_by_role(me.get_favorite_courses,
#                                           (CanvasRole.TEACHER, CanvasRole.TA, CanvasRole.DESIGNER),
#                                           include=['term'])
# for course in courses:
#     print(course)
