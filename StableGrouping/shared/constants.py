from enum import Enum

# String constants
NO_ANSWER = "No Answer"


# Enum constants
class PreferGender(Enum):
    diff_pronouns = 0
    dont_care_pronouns = 1
    same_pronouns = 2


class PreferAsync(Enum):
    dont_care_async = 0
    like_sync = 1
    like_async = 2


class PreferInternational(Enum):
    not_international = 0
    dont_care_international = 1
    prefer_international_partner = 2


class Confident(Enum):
    not_confident = 0
    default_confidence = 1
    is_confident = 2
