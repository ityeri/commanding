import logging
import os
import shutil
import curses
import threading

from commanding.log_window_handler import LogWindowHandler

ESC = '\033['

class Logger:
    _instance = None

    def __new__(cls, prefix):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, prefix: str):

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        self.prefix: str = prefix

        # 로그 핸들러 설정
        self.logWindowHandler: LogWindowHandler = LogWindowHandler()
        self.logger.addHandler(self.logWindowHandler)



    @property
    def terminalSize(self) -> os.terminal_size:
        return shutil.get_terminal_size()

    def start(self):
        loggingThread = threading.Thread(target=curses.wrapper, args=[self.main])
        loggingThread.daemon = True
        loggingThread.start()

    def main(self, screen: curses.window):
        curses.curs_set(0)
        screen.clear()

        lines = self.terminalSize.lines
        columns = self.terminalSize.columns

        # 로그가 나가는 창 설정
        logWindow: curses.window = curses.newwin(
            lines - 2, columns, 0, 0
        )
        logWindow.scrollok(True)
        logWindow.idlok(True)

        self.logWindowHandler.setWindow(logWindow)

        # 명령어 받는창 정의
        inputWindow: curses.window = curses.newwin(
            1, columns, lines - 1, 0
        )


        while True:
            inputWindow.clear()
            inputWindow.addstr(0, 0, self.prefix)
            inputWindow.refresh()
            curses.echo()
            command = inputWindow.getstr(0, len(self.prefix), 64).decode("utf-8")
            curses.noecho()


    def onCommand(self, command: str):
        self.info(command)

    def info(self, *values, between: str = " "):
        self.logger.info(between.join([str(value) + between for value in values]))
        # self.moveCurserTo(0, 0)


    def warn(self, *values, between: str = " "):
        self.logger.warning(between.join([str(value) + between for value in values]))
        # self.moveCurserTo(0, 0)

    def error(self, *values, between: str = " "):
        self.logger.error(between.join([str(value) + between for value in values]))
        # self.moveCurserTo(0, 0)

    def moveCurserTo(self, y: int, x: int):
        print(f'{ESC}{y};{x}H', end='')
