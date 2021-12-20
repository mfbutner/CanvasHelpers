# Author: Qianhan Zhang

from src.grade_transfer.user_interface import UserInterface
from src.grade_transfer.canvas_grade_transfer import CanvasGradeTransfer

# For detailed instructions, please refer to the steps in ExternalDocumentation (./src/grade_transfer/ExternalDocumentation).


# Step 1
UI = UserInterface()

# Step 2
canvas = UI.build_canvas_connection()

# Step 3
csv_path = UI.get_csv_path()

# Step 4
course = UI.get_course(canvas)

# Step 5
assignments = UI.get_assignment_groups(course)

# Step 6
csv_ncol = UI.show_head(csv_path)

# Step 7
csv_header = UI.tell_me_about_header(csv_ncol, csv_path, assignments)

# Step 8
grade_uploader = CanvasGradeTransfer(course, csv_header, csv_path)

# Step 9
third_party_full_name_match_dic = grade_uploader.third_party_full_name_match()

# Step 10
canvas_full_name_match_dic = grade_uploader.Canvas_name_match(name_type="FULL", student_dic=third_party_full_name_match_dic)

# Step 11
third_party_last_name_match_dic = grade_uploader.third_party_last_name_match()

# Step 12
canvas_last_name_match_dic = grade_uploader.Canvas_name_match(name_type="LAST", student_dic=third_party_last_name_match_dic)

# Step 13
UI.verify_name_check(third_party_dic=third_party_full_name_match_dic, canvas_dict=canvas_full_name_match_dic,
                     name_type="FULL", csv_path=csv_path)

# Step 14
UI.verify_name_check(third_party_dic=third_party_last_name_match_dic, canvas_dict=canvas_last_name_match_dic,
                     name_type="LAST", csv_path=csv_path)

# Step 15
grade_uploader.change_manual_update(third_party_dic=third_party_full_name_match_dic, name_type="FULL")

# Step 16
grade_uploader.change_manual_update(third_party_dic=third_party_last_name_match_dic, name_type="LAST")

# Step 17
grade_uploader.fill_in_grade_data()

# Step 18
UI.pre_update_announcement()
# TODO: Change the per assignment update announcements to after the grades are uploaded to Canvas.
for assignment in assignments:
    grade_uploader.bulk_update(assignment)
    UI.one_update_finish(assignment.name)

# Step 19
third_party_leftover_students = grade_uploader.get_leftover_third_party_students()

# Step 20
UI.show_csv_leftover(third_party_leftover_students, csv_path)
