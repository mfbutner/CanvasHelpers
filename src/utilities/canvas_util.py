import canvasapi
import enum
import re
from typing import Callable, TypeVar, Iterable, List, Container
from .str_helpers import clean_string, str_equal, str_starts_with

T = TypeVar('T')


def locate_item_in_canvas_by_name(item_name: str, lookup_method: Callable[[], Iterable[T]],
                                  match_method: Callable[[str, str], bool] = str_equal,
                                  ignore_case: bool = True, ignore_whitespace: bool = True) -> T:
    match_name = clean_string(item_name, ignore_case, ignore_whitespace)
    items = list(lookup_method())
    for item in items:
        if match_method():
            ...


class CanvasRole(enum.Enum):
    TEACHER = 'teacher'
    STUDENT = 'student'
    TA = 'ta'
    DESIGNER = 'designer'
    OBSERVER = 'observer'


def get_courses_enrolled_in_by_role(lookup_method: Callable[..., Iterable[canvasapi.course.Course]],
                                    roles: Iterable[CanvasRole] = (CanvasRole.TEACHER,),
                                    **kwargs) -> List[canvasapi.course.Course]:
    """

    :param lookup_method: a method that returns a iterable of canvas course. Likely an Instance of either
    canvasapi.Canvas.get_courses or canvasapi.current_user.CurrentUser.get_favorite_courses
    :param roles:
    :param kwargs:
    :return:
    """
    roles = {role.value for role in roles}
    courses = list()
    for course in lookup_method(**kwargs):
        for enrollment in course.enrollments:
            if enrollment['type'] in roles:
                courses.append(course)
                break
    return courses
