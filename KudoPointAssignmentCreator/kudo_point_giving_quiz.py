import canvasapi
import datetime
from typing import List
from .group import Group


class KudoPointGivingQuiz:
    def __init__(self, user: canvasapi.user.User,
                 group: canvasapi.group.Group,
                 assignment_group: canvasapi.assignment.AssignmentGroup,
                 unlock_date: datetime.datetime,
                 due_date: datetime.datetime,
                 late_days: int = 0,
                 number_of_kudo_points: int = 2):
        self.user = user
        self.group = Group(group)
        self.assignment_group = assignment_group
        self.unlock_date = unlock_date
        self.due_date = due_date
        self.lock_date = due_date + datetime.timedelta(days=late_days)
        self.number_of_kudo_points = number_of_kudo_points

        self.quiz_info = self._create_quiz_info()
        self.assignment_info = self._create_assignment_info()
        self.quiz_questions = self._create_quiz_questions()

    def _create_quiz_info(self) -> dict:
        return {
            'title': f"{self.user.name}'s Kudo Point Givings for {self.group.name}",
            'quiz_type': 'assignment',
            'assignment_group_id': self.assignment_group.id,
            'allowed_attempts': 10,
            'scoring_policy': 'keep_latest',
            'published': False,
            'show_correct_answers': False,
            'only_visible_to_overrides': True,
        }

    def _create_assignment_info(self) -> dict:
        date_info = {
            'student_ids': [self.user.id],
            'title': f'Override for {self.user.name}',
            'due_at': self.due_date.isoformat(),
            'unlock_at': self.unlock_date,
            'lock_at': self.lock_date
        }

        return {
            'grading_type': 'not_graded',
            'omit_from_final_grade': True,
            'only_visible_to_overrides': True,
            'assignment_overrides': [date_info],
            'published': True
        }

    def _create_quiz_questions(self) -> List[dict]:
        answers = self._create_answers()
        return [
            {
                'question_name': f'Kudo Point {point}',
                'question_text': 'Who do you want to give this Kudo Point to?',
                'question_type': 'multiple_choice_question',
                'answers': answers
            } for point in range(1, self.number_of_kudo_points + 1)
        ]

    def _create_answers(self) -> List[dict]:
        answers = [
            {
                'answer_text': member.name,
                'answer_weight': 1
            } for member in self.group.members if self.user.id != member.id
        ]
        answers.append({
            'answer_text': 'I do not want to give this Kudo Point to anyone.',
            'answer_weight': 1
        })
        return answers

    def upload_to_canvas(self, course: canvasapi.course.Course, print_when_done: bool = True) -> None:
        canvas_quiz = course.create_quiz(self.quiz_info)
        for question in self.quiz_questions:
            canvas_quiz.create_question(question=question)
        canvas_assignment = course.get_assignment(canvas_quiz.assignment_id)
        canvas_assignment = canvas_assignment.edit(assignment=self.assignment_info)
        if print_when_done:
            print(f'Created "{canvas_quiz}" in "{self.assignment_group}"')
