from typing import List
import canvasapi


class Group():
    def __init__(self, canvas_group: canvasapi.group.Group):
        self.canvas_group = canvas_group
        self._members = None

    @property
    def name(self) -> str:
        return self.canvas_group.name

    @property
    def members(self) -> List[canvasapi.user.User]:
        if self._members is None:
            self._members = list(self.canvas_group.get_users())
        return self._members

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)
