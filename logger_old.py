import msvcrt
import os
import shutil
import threading
import time

ESC = '\033['

class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.buffer: list[str] = list()
        self.logs: list[str] = list()
        self.command: str = str()
        self.commandPrefix: str = ""
        self.commandLineCurserPos: int = len(self.commandPrefix)

    def info(self, *values):
        line = str()
        for value in values:
            line += str(value) + " "
        self.buffer.append(line)


    @property
    def terminalRows(self) -> int: return shutil.get_terminal_size().lines

    @property
    def terminalColumns(self) -> int: return shutil.get_terminal_size().columns

    def run(self):
        os.system('cls')
        loggerThread = threading.Thread(target=self.runLogger)
        commandLineThread = threading.Thread(target=self.runCommandLine)

        loggerThread.start()
        commandLineThread.start()

    def runLogger(self):
        while True:
            if self.buffer:
                # os.system('cls')
                self.logs.extend(self.buffer)
                for i, line in enumerate(self.logs):
                    self.insertLine(-1 - len(self.logs) + i,
                                    line + " " * (self.terminalColumns - len(line)))

                self.buffer.clear()

                self.moveCurserTo(self.terminalRows, len(self.commandPrefix))
                print(self.command + " " * (self.terminalColumns - len(self.command)), end='')
                self.moveCurserTo(self.terminalRows, len(self.command)+1)



    def runCommandLine(self):
        while True:
            time.sleep(0.1)
            self.commandLineCurserPos = len(self.commandPrefix)
            self.moveCurserTo(self.terminalRows, self.commandLineCurserPos)
            print(self.commandPrefix, end='')
            self.command = ""

            while True:
                self.moveCurserTo(self.terminalRows, self.commandLineCurserPos)
                char = msvcrt.getch()  # 하나의 문자 입력

                if char == b'\r':  # Enter 키
                    logger.info("커맨드 입력됨!:", self.command)
                    self.command = ""
                    break

                elif char == b'\x08':  # Backspace 키
                    self.command = self.command[:-1]  # 마지막 문자를 지우고
                    self.moveCurserTo(self.terminalRows, self.commandLineCurserPos)
                    print('\b \b', end='')  # 화면에서 지우기
                    self.commandLineCurserPos -= 1

                else:
                    self.command += char.decode('utf-8')  # 입력된 문자 추가
                    self.moveCurserTo(self.terminalRows, self.commandLineCurserPos)
                    print(char.decode('utf-8'), end='')
                    self.commandLineCurserPos += 1



    def moveCurserTo(self, y: int, x: int):
        if 0 <= y:
            print(f'{ESC}{y};{x}H', end='')
        else: print(f'{ESC}{self.terminalRows+y};{x}H', end='')

    def insertLine(self, y: int, string: str):
        self.moveCurserTo(y, 0)

        # print(f'{ESC}L', end='')
        # print(f'{ESC}1F{ESC}L', end='')

        print(string)

logger = Logger()

logger.run()

while True:
    time.sleep(1)
    logger.info("asdf")
