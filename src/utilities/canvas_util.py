import canvasapi
import enum
import re
from typing import Callable, TypeVar, Iterable
from .str_helpers import clean_string, str_equal, str_starts_with

T = TypeVar('T')



def locate_item_in_canvas_by_name(item_name: str, lookup_method: Callable[[], Iterable[T]],
                                  match_method: Callable[[str, str], bool] = str_equal,
                                  ignore_case:bool=True, ignore_whitespace:bool=True) -> T:
    match_name = clean_string(item_name, ignore_case, ignore_whitespace)
    items = list(lookup_method())
    for item in items:
        if match_method()

