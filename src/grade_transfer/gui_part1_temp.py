# Author: Qianhan Zhang

import canvasapi


class gui_part1:

    # list length = first row length
    a_list = [NA, NA, NA, NA]

    # After user finish drag and drop (tell me which column is what), a_list get modified, and a_list get passed in to
    # Canvas_grade_transfer's init method to creat an instance of the class (start.py).
    assignments = list(course.get_assignments())
    x = 5
    # Final_exam is entry 3 in assignments
    # example of final a_List = ["first_name", "last_name", NA, "SID", self.assignments[3], self.x]
    # so for Canvas_grade_transfer class, it will be an instance of canvasapi.assignment.Assignment, to know the name
    # need to use canvasapi.assignment.Assignment.getname().
