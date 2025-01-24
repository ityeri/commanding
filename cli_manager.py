import logging
import os
import shutil
import curses
import threading

from commanding.command_manager import CommandManager
from commanding.log_window_handler import LogWindowHandler


ESC = '\033['

class CLIManager:
    _instance = None

    def __new__(cls, prefix):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, prefix: str="> ", logginLevel: int = logging.DEBUG):

        self.logger = logging.getLogger()
        self.logger.setLevel(level=logginLevel)

        self.prefix: str = prefix

        # 로그 핸들러 설정
        self.logWindowHandler: LogWindowHandler = LogWindowHandler()
        self.logger.addHandler(self.logWindowHandler)

        # 윈도우 설정 (main 함수에서 함)
        self.logWindow: curses.window = None
        self.inputWindow: curses.window = None

        # 화면
        self.screen: curses.window = None

        # 커맨드 매니저
        self.commandManager: CommandManager = CommandManager(self)



    @property
    def terminalSize(self) -> os.terminal_size:
        return shutil.get_terminal_size()

    def start(self):
        loggingThread = threading.Thread(target=curses.wrapper, args=[self.main])
        loggingThread.daemon = True
        loggingThread.start()
        screenResizeCheckThread = threading.Thread(target=self.screenResizeCheck)
        screenResizeCheckThread.daemon = True
        screenResizeCheckThread.start()

    def main(self, screen: curses.window):
        self.screen = screen

        curses.curs_set(0)
        self.screen.clear()

        curses.start_color()

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)

        curses.init_pair(10, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(11, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

        self.setWindow(self.terminalSize.lines, self.terminalSize.columns)

        while True:
            self.inputWindow.clear()
            self.inputWindow.addstr(0, 0, self.prefix)
            self.inputWindow.refresh()
            curses.echo()
            command = self.inputWindow.getstr(0, len(self.prefix), 256).decode("utf-8")
            self.onCommand(command)
            curses.noecho()

    def setWindow(self, lines: int, columns: int):
        if self.logWindow:
            self.logWindow.clear()
        if self.inputWindow:
            self.inputWindow.clear()

        # 로그가 나가는 창 설정
        self.logWindow = curses.newwin(
            lines - 2, columns, 0, 0
        )
        self.logWindow.scrollok(True)
        self.logWindow.idlok(True)

        self.logWindowHandler.setWindow(self.logWindow)

        # 명령어 받는창 정의
        self.inputWindow = curses.newwin(
            1, columns, lines - 1, 0
        )

        self.screen.clear()
        self.screen.refresh()

    def screenResizeCheck(self):
        lines = self.terminalSize.lines
        columns = self.terminalSize.columns

        while True:
            linesOld = lines
            columnsOld = columns
            lines = self.terminalSize.lines
            columns = columns = self.terminalSize.columns

            if lines != linesOld or columns != columnsOld:
                self.setWindow(lines, columns)



    def onCommand(self, command: str):
        if command == "__rscr__":
            commandChunks = command.split(' ')

            lines = self.terminalSize.lines
            columns = self.terminalSize.columns
            if len(commandChunks) == 2:
                try: lines = int(commandChunks[1])
                except:
                    self.error("잘못된 명령어 사용법 입니다!")
                    self.info("사용법: __rscr__ <화면 줄 갯수> <화면 열 갯수?>")
                    return
            elif len(commandChunks) == 3:
                try:
                    lines = int(commandChunks[1])
                    columns = int(commandChunks[2])
                except:
                    self.error("잘못된 명령어 사용법 입니다!")
                    self.info("사용법: __rscr__ <화면 줄 갯수> <화면 열 갯수?>")
                    return

            self.setWindow(lines, columns)

        elif command == '': return
        else:
            self.commandManager.onCommand(command)

    def info(self, *values, between: str = " "):
        self.logger.info(between.join([str(value) + between for value in values]))

    def warn(self, *values, between: str = " "):
        self.logger.warning(between.join([str(value) + between for value in values]))

    def error(self, *values, between: str = " "):
        self.logger.error(between.join([str(value) + between for value in values]))

    def debug(self, *values, between: str = " "):
        self.logger.debug(between.join([str(value) + between for value in values]))

    def moveCurserTo(self, y: int, x: int):
        print(f'{ESC}{y};{x}H', end='')
