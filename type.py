from typing import TypeVar, Callable

CommandArgType = TypeVar('CommandArgType', str, bool, int)
CommandFuncType = Callable[[CommandArgType], None]