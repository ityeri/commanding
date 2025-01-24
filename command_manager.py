from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from commanding.cli_manager import CLIManager

from commanding.command import Command
from commanding.type import CommandFuncType
from commanding.exceptions import WrongCommandParameterError

class CommandManager:

    def __init__(self, cliManager: 'CLIManager'):
        self.commands: dict[str, Command] = dict()
        self.cliManager: 'CLIManager' = cliManager

    def onCommand(self, command: str):
        if command.split(' ')[0] == "help":
            commandChunks = command.split(' ')
            if len(commandChunks) == 2:
                if commandChunks[1] not in self.commands:
                    self.cliManager.error("그런 이름을 가진 명령어가 없습니다!")
            else:
                for commandName, commandObj in self.commands.items():
                    commandUsage = ' '.join([ f"<{commandArg.displayName}>"
                        for commandArg in commandObj.commandArgs
                    ])

                    self.cliManager.info(f"{commandName} {commandUsage} : "
                                         f"{commandObj.desc if not commandObj.desc is None else 'No desc'}")

        elif command.split(' ')[0] in self.commands:
            commandObj = self.commands[command.split(' ')[0]]
            try:
                commandObj.onCommand(command)
            except WrongCommandParameterError:
                self.cliManager.error("잘못된 명령어 사용법입니다")
                commandUsage = ' '.join([f"<{commandArg.displayName}>"
                                         for commandArg in commandObj.commandArgs
                                         ])

                self.cliManager.info(f"사용법: {commandObj.commandName} {commandUsage}")
        else: self.cliManager.error("알수 없는 명령어 입니다. type help for help")


    def registerCommand(self, name: str, desc: str|None = None):
        def decorator(func: CommandFuncType):
            newCommand = Command(
                name, desc, func
            )
            self.commands[name] = newCommand
            # return newCommand
        
        return decorator