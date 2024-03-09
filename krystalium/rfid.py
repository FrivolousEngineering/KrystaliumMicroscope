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
    serial_paths: list[str] = pydantic.Field(default_factory = list)
    use_pipe: bool = True
    baud_rate: int = 9600


class RfidController:
    def __init__(self, config: Config) -> None:
        self.__config = config
        self.__running = False
        self.__rfid_id = ""
        self.__path = None
        self.__serial = None

    @property
    def rfid_id(self):
        return self.__rfid_id

    async def start(self) -> None:
        if self.__config.use_pipe:
            self.__path = Path() / self.__config.device_path
            os.mkfifo(self.__path)
            log.info(f"Created FIFO at {self.__path}")
        else:
            self.__create_serial()

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
                if self.__serial is None:
                    self.__create_serial()

                try:
                    line = self.__serial.readline().decode("utf-8")
                except serial.SerialException:
                    log.exception("Error reading serial")
                    self.__serial = None
                    continue

            line = line.rstrip()
            if line.startswith("Tag found:"):
                self.__rfid_id = line.replace("Tag found: ", "")
                log.debug(f"Detected tag {self.__rfid_id}")
            elif line.startswith("Tag lost:"):
                log.debug(f"Lost tag {self.__rfid_id}")
                self.__rfid_id = ""

    def __create_serial(self):
        for path in self.__config.serial_paths:
            s = serial.Serial(path, self.__config.baud_rate, timeout = 3)
            if s is not None:
                log.info(f"Reading from serial at {path}")
                self.__serial = s
                break
