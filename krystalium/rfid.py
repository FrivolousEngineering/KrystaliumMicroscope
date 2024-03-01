import os
import logging
import threading
from pathlib import Path

import serial
import pydantic


log = logging.getLogger(__name__)


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class Config:
    device_path: str = "rfid"
    use_pipe: bool = True
    baud_rate: int = 9600


class RfidController:
    def __init__(self, config: Config) -> None:
        self.__config = config
        self.__running = False
        self.__rfid_id = ""
        self.__path = None

    @property
    def rfid_id(self):
        return self.__rfid_id

    async def start(self) -> None:
        if self.__config.use_pipe:
            self.__path = Path() / self.__config.device_path
            os.mkfifo(self.__path)
            log.info(f"Created FIFO at {self.__path}")
        else:
            self.__serial = serial.Serial(self.__config.device_path, self.__config.baud_rate, timeout = 3)
            if self.__serial is not None:
                log.info(f"Reading from serial at {self.__config.device_path}")

        self.__running = True
        self.__thread = threading.Thread(target = self.__detect, daemon=True)
        self.__thread.start()

    async def stop(self) -> None:
        self.__runnng = False

        if self.__path:
            os.unlink(self.__path)

    def __detect(self):
        if self.__path:
            f = open(self.__path)

        while self.__running:
            if self.__path:
                line = f.readline()
            else:
                line = self.__serial.readline().decode("utf-8")

            line = line.rstrip()
            if line.startswith("Tag found:"):
                self.__rfid_id = line.replace("Tag found: ", "")
            elif line.startswith("Tag lost:"):
                self.__rfid_id = ""
