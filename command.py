from typing import Callable, TypeVar, Generic
import inspect
from commanding.type import *

from commanding.exceptions import *



class Command:
    def __init__(self, commandName: str, desc: str|None, commandFunc: CommandFuncType):
        self.commandName: str = commandName
        self.desc: str|None = desc
        self.commandArgs: list[CommandArg] = list()
        self.commandFunc: CommandFuncType = commandFunc

        signature = inspect.signature(commandFunc)
        for paramName, param in signature.parameters.items():
            if param.default is None:
                raise WrongCommandFuncParameterError("함수 인자의 기본값으로 명령어 상의 인자의 표시 이름을 지정해야 합니다")
            elif not isinstance(param.default, str):
                raise WrongCommandFuncParameterError("함수 인자의 기본값은 모두 문자열 이여야 합니다")

            elif param.annotation not in (str, bool, int):
                raise WrongCommandFuncParameterError("함수 인자의 타입 힌트는 str, bool, int 중에 하나여야 합니다")

            self.commandArgs.append(CommandArg(paramName, param.default, param.annotation))

    def onCommand(self, command: str):
        argsStr = command.split()[1:]
        args = list()

        if len(argsStr) != len(self.commandArgs):
            raise WrongCommandParameterError(f"인자의 갯수가 일치하지 않습니다 "
                                             f"{len(self.commandArgs)}개가 필요하지만, {len(argsStr)}개가 주어졌습니다")

        for commandArg, argStr in zip(self.commandArgs, argsStr):
            args.append(
                commandArg.toValue(argStr)
            )

        self.commandFunc(*args)



class CommandArg(Generic[CommandArgType]):
    def __init__(self, parameterName: str, displayName: str, argType: type[CommandArgType]):
        self.parameterName: str = parameterName
        self.displayName: str = displayName
        self.argType = argType

    def toValue(self, arg: str) -> CommandArgType:
        if self.argType == str: return arg

        if self.argType == int:
            try:
                return int(arg)
            except ValueError: raise WrongCommandParameterError

        if self.argType == bool:
            if (
                arg == '0' or
                arg.lower() == 'false' or
                arg.lower() == 'f'
            ): return False
            elif (
                arg == '1' or
                arg.lower() == 'true' or
                arg.lower() == 't'
            ): return True
            else: raise WrongCommandParameterError

        else: raise WrongCommandFuncParameterError("self.argType 가 잘못되었습니다")