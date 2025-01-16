import curses
import logging
import datetime

ESC = '\033['

class LogWindowHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logWindow: curses.window | None = None

    def setWindow(self, window: curses.window):
        self.logWindow = window

    # 로그 올라갈때 뜨는거
    def emit(self, record: logging.LogRecord):
        dt = datetime.datetime.fromtimestamp(record.created)
        message = f"[{dt.strftime('%Y-%m-%d %H:%M:%S')}] [{record.levelname}] : {record.msg}"

        self.logWindow.addstr(message + '\n')
        self.logWindow.refresh()

        self.moveCurserTo(0, 0)

    def moveCurserTo(self, y: int, x: int):
        print(f'{ESC}{y};{x}H', end='')