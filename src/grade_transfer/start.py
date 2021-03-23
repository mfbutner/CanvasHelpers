# Author: Qianhan Zhang


from src.grade_transfer.user_interface import UserInterface
from src.grade_transfer.canvas_grade_transfer import CanvasGradeTransfer

UI = UserInterface()
canvas = UI.build_canvas_connection()
csv_path = UI.get_csv_path()
course = UI.get_course(canvas)
assignments = UI.get_assignment_groups(course)
csv_ncol = UI.show_head(csv_path)
csv_header = UI.tell_me_about_header(csv_ncol, csv_path, assignments)

grade_uploader = CanvasGradeTransfer(course, csv_header, csv_path)


third_party_full_name_match_dic = grade_uploader.third_party_full_name_match()
canvas_full_name_match_dic = grade_uploader.Canvas_name_match(name_type="FULL", student_dic=third_party_full_name_match_dic)

third_party_last_name_match_dic = grade_uploader.third_party_last_name_match()
canvas_last_name_match_dic = grade_uploader.Canvas_name_match(name_type="LAST", student_dic=third_party_last_name_match_dic)


UI.verify_name_check(third_party_dic=third_party_full_name_match_dic, canvas_dict=canvas_full_name_match_dic,
                     name_type="FULL", csv_path=csv_path)
UI.verify_name_check(third_party_dic=third_party_last_name_match_dic, canvas_dict=canvas_last_name_match_dic,
                     name_type="LAST", csv_path=csv_path)

grade_uploader.change_manual_update(third_party_dic=third_party_full_name_match_dic, name_type="FULL")
grade_uploader.change_manual_update(third_party_dic=third_party_last_name_match_dic, name_type="LAST")


grade_uploader.fill_in_grade_data()

UI.pre_update_announcement()
for assignment in assignments:
    grade_uploader.bulk_update(assignment)
    UI.one_update_finish(assignment.name)

third_party_leftover_students = grade_uploader.get_leftover_third_party_students()

UI.show_csv_leftover(third_party_leftover_students, csv_path)
