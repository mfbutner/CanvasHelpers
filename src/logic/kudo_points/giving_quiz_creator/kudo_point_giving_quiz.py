import canvasapi
import datetime
from typing import List, Callable, Optional


class KudoPointGivingQuiz:
    def __init__(self, course: canvasapi.course.Course,
                 assignment_name: str,
                 assignment_group: canvasapi.assignment.AssignmentGroup,
                 number_of_kudo_points,
                 due_date: Optional[datetime.datetime] = None,
                 unlock_date: Optional[datetime.datetime] = None,
                 lock_date: Optional[datetime.datetime] = None):
        """

        :param course:
        :param assignment_name:
        :param assignment_group:
        :param number_of_kudo_points:
        :param due_date:
        :param unlock_date:
        :param lock_date:
        """
        self.user = course
        self.assignment_name = assignment_name
        self.assignment_group = assignment_group
        self.unlock_date = unlock_date
        self.due_date = due_date
        self.lock_date = lock_date
        self.number_of_kudo_points = number_of_kudo_points

        students = course.get_users(sort='username', enrollment_type=['student'])
        self.students = {}
        for student in students:
            if student.sortable_name not in self.students:
                self.students[student.sortable_name] = []
            self.students[student.sortable_name].append(student)

        self.quiz_info = self._create_quiz_info()
        self.assignment_info = self._create_assignment_info()
        self.quiz_questions = self._create_quiz_questions()

    def _create_quiz_info(self) -> dict:
        prompt = """<p>Please fill out who you would like to give your Kudo points to. You can <strong>NOT </strong>give your Kudo point to</p>
<ol>
<li><span style="font-family: inherit; font-size: 1rem;">Yourself&nbsp;</span></li>
<li><span style="font-family: inherit; font-size: 1rem;">Anyone outside of your Study Group </span></li>
</ol>
<p><span style="font-family: inherit; font-size: 1rem;">If you break any of these rules, your Kudo point will <strong>NOT be counted</strong>. </span></p>
<p>&nbsp;</p>
<p><span style="font-family: inherit; font-size: 1rem;">To quickly find who you want to give your Kudo point to use ctrl+f if you are on Windows or Cmd+f if you are Mac and then enter the recipient's name.</span></p>
<p>&nbsp;</p>
<p><span style="font-family: inherit; font-size: 1rem;">After responding, please ignore Canvas's notification that your answer are incorrect. Your response has been recorded correctly, Canvas just does not know how to deal with multiple-choice questions where every answer is "correct."</span></p>"""
        return {
            'title': self.assignment_name,
            'description': prompt,
            'quiz_type': 'assignment',
            'assignment_group_id': self.assignment_group.id,
            'allowed_attempts': 10,
            'scoring_policy': 'keep_latest',
            'published': False,
            'show_correct_answers': False,
            'due_at': self.due_date,
            'lock_at': self.lock_date,
            'unlock_at': self.unlock_date
        }

    def _create_assignment_info(self) -> dict:
        return {
            # setting grading_type to not_graded breaks the association between Quiz and Assignment
            # not sure if this is a bug on Canvas's end or what so leaving it out for now.
            # 'grading_type': 'not_graded',
            'omit_from_final_grade': True,
            'published': True
        }

    def _create_quiz_questions(self) -> List[dict]:
        answers = self._create_answers()
        return [
            {
                'question_name': f'Kudo Point {point}',
                'question_text': 'Who do you want to give this Kudo Point to?',
                'question_type': 'multiple_choice_question',
                'answers': answers,
                'points_possible': 1
            } for point in range(1, self.number_of_kudo_points + 1)
        ]

    def _create_answers(self) -> List[dict]:
        answers = [
            {
                'answer_html': student_name,
                'answer_text': ','.join([str(s.id) for s in student]),
                'answer_weight': 1

            } for student_name, student in self.students.items()
        ]
        answers.append({
            'answer_html': 'I do not want to give this Kudo Point to anyone.',
            'answer_weight': 1
        })
        return answers

    def upload_to_canvas(self, course: canvasapi.course.Course) -> None:
        canvas_quiz = course.create_quiz(self.quiz_info)
        for question in self.quiz_questions:
            canvas_quiz.create_question(question=question)
        canvas_assignment = course.get_assignment(canvas_quiz.assignment_id)
        edited_canvas_assignment = canvas_assignment.edit(assignment=self.assignment_info)
        # edited_quiz = canvas_quiz.edit(quiz={'published': True})
        # second_assignment = course.get_assignment(canvas_quiz.assignment_id)
        pass
