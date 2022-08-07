from StableGrouping.shared.constants import PreferInternational, Confident, PreferGender, PreferAsync


class Student:
    def __init__(self):
        # Basic student identification information
        self.name = ""
        self.id_num = 0
        self.schoolEmail = ""
        self.firstName = ""
        self.lastName = ""

        # Student preferences
        self.pronouns = ""
        self.language = "English"
        self.international = PreferInternational.not_international.value
        self.prefer_leader = False
        self.confidence = Confident.default_confidence.value

        # If student prefers the same pronouns
        self.prefer_same = PreferGender.same_pronouns.value

        # Does the student prefer to meet asynchronously
        self.prefer_async = PreferAsync.dont_care_async.value
        # Student available meeting times in PST
        # [day][time] in 4 hour in hr intervals from 12am to 12am starting Sunday
        self.meeting_times = [[False, False, False, False, False, False],
                              [False, False, False, False, False, False],
                              [False, False, False, False, False, False],
                              [False, False, False, False, False, False],
                              [False, False, False, False, False, False],
                              [False, False, False, False, False, False],
                              [False, False, False, False, False, False]]

        # contact preference and information (Order: [Discord, Phone Number, Email])
        self.contact_preference = [False, False, False, True]
        self.contact_information = ["", "", ""]

        # The what the student prioritizes in a study group from most to least.
        self.priority_list = ["", "", "", "", ""]
        # What activity the student prefers to do.
        self.activity_choice = ""
        self.free_response = ""

        # partner the student wants and their email
        self.partner = ""
        self.partner_email = ""

    def __str__(self):
        student_details = (f"Student: {self.name} ({self.lastName}, {self.firstName})\n"
                           f"ID: {self.id_num} | Email: {self.schoolEmail}\n"
                           f"Pronouns: {self.pronouns} - Prefer Same Pronouns: {self.prefer_same}\n"
                           f"  Meeting Times (Prefer Async: {self.prefer_async})")

        for week in self.meeting_times:
            student_details += "\n "
            for day in week:
                student_details += f" {str(day)} "
        student_details += "\n"

        student_details += "Contact Preferences: "
        for contact_preference in self.contact_preference:
            student_details += f" {str(contact_preference)}, "
        student_details += "\n"

        student_details += "Contact Information: "
        for contact_information in self.contact_preference:
            student_details += f" {contact_information}, "
        student_details += "\n"

        student_details += (f"Prefer Leader: {self.prefer_leader} | International: {self.international} | "
                            f"Language: {self.language} | Activity: {self.activity_choice} - {self.free_response}\n"
                            f"Confidence: {self.confidence}\n"
                            f"Priorities: ")
        for value in self.priority_list:
            student_details += f" {value}, "

        return student_details
