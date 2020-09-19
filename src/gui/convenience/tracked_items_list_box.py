import tkinter
from typing import Iterable, Union, overload, Callable, TypeVar, Optional

T = TypeVar('T')


class TkinterDisplayableList(list):

    def __init__(self, iterable=(), to_string: Callable[[T], str] = str) -> None:
        super().__init__(iterable)
        self.to_string = to_string
        self.string_values = [self.to_string(value) for value in self]
        self.tkinter_values = tkinter.StringVar(value=self.string_values)

    def clear(self) -> None:
        super().clear()
        self.string_values.clear()
        self.tkinter_values.set(self.string_values)

    def append(self, __object) -> None:
        super().append(__object)
        self.string_values.append(str(__object))
        self.tkinter_values.set(self.string_values)

    def extend(self, __iterable: Iterable) -> None:
        super().extend(__iterable)
        self.string_values.extend([self.to_string(value) for value in __iterable])
        self.tkinter_values.set(self.string_values)

    def pop(self, __index: int = ...):
        self.string_values.pop(__index)
        self.tkinter_values.set(self.string_values)
        return super().pop(__index)

    def insert(self, __index: int, __object) -> None:
        super().insert(__index, __object)
        self.string_values.insert(__index, self.to_string(__object))
        self.tkinter_values.set(self.string_values)

    def remove(self, __value) -> None:
        index = super().index(__value)
        self.pop(index)
        self.tkinter_values.set(self.string_values)

    def reverse(self) -> None:
        super().reverse()
        self.string_values.reverse()
        self.tkinter_values.set(self.string_values)

    @overload
    def sort(self, *, key: None = ..., reverse: bool = False) -> None: ...

    @overload
    def sort(self, *, key, reverse: bool = False) -> None: ...

    def sort(self, *, key: None = None, reverse: bool = False) -> None:
        super().sort(key=key, reverse=reverse)
        self.string_values = [self.to_string(value) for value in self]
        self.tkinter_values.set(self.string_values)

    @overload
    def __setitem__(self, i: int, o) -> None: ...

    @overload
    def __setitem__(self, s: slice, o) -> None: ...

    def __setitem__(self, i: int, o) -> None:
        super().__setitem__(i, o)
        self.string_values[i] = [self.to_string(value) for value in o] if isinstance(o, slice) else o
        self.tkinter_values.set(self.string_values)

    def __delitem__(self, i: Union[int, slice]) -> None:
        super().__delitem__(i)
        self.string_values.__delitem__(i)
        self.tkinter_values.set(self.string_values)

    def __iadd__(self, x):
        self.string_values.__iadd__([self.to_string(value) for value in x])
        self.tkinter_values.set(self.string_values)
        return super().__iadd__(x)

    def __imul__(self, n: int):
        self.string_values.__imul__(n)
        self.tkinter_values.set(self.string_values)
        return super().__imul__(n)


class TrackedItemListBox(tkinter.Listbox):
    def __init__(self, master=None, values: Optional[Iterable] = None, to_string: Callable[[T], str] = str, cnf={},
                 **kw):
        super().__init__(master, cnf, **kw)
        self._values = TkinterDisplayableList(values, to_string) if values is not None \
            else TkinterDisplayableList(to_string=to_string)
        self['listvariable'] = self.values.tkinter_values

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, value):
        if isinstance(value, TkinterDisplayableList):
            self._values = value
        else:
            self._values.clear()
            self._values.extend(value)

    def get_selected_items(self) -> list:
        return [self.values[index] for index in self.curselection()]
