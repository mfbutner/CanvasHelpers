# Author: Qianhan Zhang
 
class ThirdPartyStudent:
    def __init__(self, first_name=None, last_name=None, sid=None, email=None, full_name=None):
        self.first_name = first_name
        self.last_name = last_name
        self.sid = sid
        self.email = email
        self.full_name = full_name
        self.assignment_list = []
        self.email_match = False
        self.sid_match = False
        self.full_name_match = False
        self.last_name_match = False
        self.manual_match = False

    def set_full_name(self):
        if (self.last_name is None) and (self.first_name is None):
            name = None
        elif self.last_name is None:
            name = ", " + self.first_name
        elif self.first_name is None:
            name = self.last_name + ", "
        else:
            name = self.last_name + ", " + self.first_name
        self.full_name = name
        return

    def add_assignment(self, assignment):
        self.assignment_list.append(assignment)

    def __str__(self):
        return str(self.__dict__)

