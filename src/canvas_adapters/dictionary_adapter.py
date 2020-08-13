from typing import Dict, Any


class DictAdapter:
    def __init__(self, dictionary: Dict[str, Any]):
        for member, value in dictionary.items():
            setattr(self, member, value)

    def __eq__(self, other: "DictAdapter") -> bool:
        return isinstance(other, DictAdapter) and self.id == other.id

    def __ne__(self, other: "DictAdapter") -> bool:
        return not self == other

    def __str__(self) -> str:
        return '\n'.join(
            (f'{memeber} : {value}' for memeber, value in self.__dict__.items())
        )

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self):
        return self.id
