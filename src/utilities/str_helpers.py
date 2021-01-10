import re


def clean_string(string: str, ignore_case: bool, ignore_whitespace) -> str:
    if ignore_whitespace:
        string = re.sub(r'''\s+''', '', string)
    if ignore_case:
        string = string.lower()
    return string


def str_equal(str1: str, str2: str, ignore_case: bool = True, ignore_whitespace: bool = True) -> bool:
    return clean_string(str1, ignore_case, ignore_whitespace) == \
           clean_string(str2, ignore_case, ignore_whitespace)


def str_starts_with(string: str, prefix: str, ignore_case: bool = True, ignore_whitespace: bool = True) -> bool:
    return str.startswith(clean_string(string, ignore_case, ignore_whitespace),
                          clean_string(prefix, ignore_case, ignore_whitespace)
                          )
