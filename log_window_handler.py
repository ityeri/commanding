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

        for line in record.msg.split("\n"):
            self.logWindow.addstr(f"[{dt.strftime('%Y-%m-%d %H:%M:%S')}] ", curses.color_pair(10))
            self.logWindow.addstr(f"[{record.levelname}] ", curses.color_pair(11))

            color = None

            match record.levelno:
                case logging.INFO: color = curses.color_pair(1)
                case logging.WARN: color = curses.color_pair(2)
                case logging.ERROR: color = curses.color_pair(3)
                case logging.DEBUG: color = curses.color_pair(4)

            self.logWindow.addstr(f": {line}", color)
            self.logWindow.addstr("\n")

        self.logWindow.refresh()

        self.moveCurserTo(0, 0)

    def moveCurserTo(self, y: int, x: int):
        print(f'{ESC}{y};{x}H', end='')