# from typing import List, Callable, Dict
from pathlib import Path
from typing import Callable
import logging
import threading

import pydantic
import serial
from serial import SerialException

from .component import Component


log = logging.getLogger(__name__)


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class Config:
    baud_rate: int = 115200
    patterns: list[str] = pydantic.Field(default_factory = list)


class Serial(Component):
    def __init__(self, *, path: Path, baud_rate: int = 115200, controller):
        super().__init__(name = f"Serial@{path}")
        self.__controller = controller
        self.__baud_rate: int = baud_rate
        self.__path: Path = path
        self.__callback: Callable[[str], None] | None = None
        self.__device_name = ""
        self.__serial = None

    @property
    def path(self):
        return self.__path

    @property
    def device_name(self):
        return self.__device_name

    def set_callback(self, callback: Callable[[str], None]) -> None:
        self.__callback = callback

    async def start(self) -> None:
        self.__thread = threading.Thread(target = self.__read, daemon = True)
        self.__thread.start()

    async def stop(self) -> None:
        self.__serial.close()
        self.__serial = None
        self.__thread.join()

    def __read(self):
        self.__serial = serial.Serial(str(self.__path), baudrate = self.__baud_rate, timeout = 1)
        self.__serial.write(b"NAME\n")

        while serial:
            try:
                if not self.__device_name:
                    self.__serial.write(b"NAME\n")

                line = self.__serial.readline()
                line = line.decode("utf-8").rstrip().lower()

                if not line:
                    continue

                if line.startswith("name:"):
                    self.__device_name = line.replace("name: ", "")
                    self.__controller.device_identified(self)
                elif self.__callback:
                    self.__callback(line)
            except SerialException:
                self.__controller.device_lost(self)


class SerialController(Component):
    def __init__(self, *, config: Config):
        super().__init__(interval = 5)
        self.__config = config
        self.__devices: dict[Path, Serial] = {}
        self.__devices_to_remove: list[Serial] = []

        self.__device_added_callback: Callable[[Serial], None] | None = None
        self.__device_removed_callback: Callable[[Serial], None] | None = None

    def set_callbacks(self, device_added: Callable[[Serial], None], device_removed: Callable[[Serial], None]) -> None:
        self.__device_added_callback = device_added
        self.__device_removed_callback = device_removed
    def devices_by_name(self, name: str) -> list[Serial]:
        return [device for device in self.__devices.values() if device.device_name == name]

    async def update(self, elapsed: float) -> None:
        for device in self.__devices_to_remove:
            del self.__devices[device.path]
            self.children.remove(device)
            await device.stop()
            if self.__device_removed_callback:
                self.__device_removed_callback(device)
            log.info(f"Lost serial device {device.path}")
        self.__devices_to_remove.clear()

        for pattern in self.__config.patterns:
            for path in Path("/dev").glob(pattern):
                if path in self.__devices:
                    continue

                try:
                    serial = Serial(path = path, baud_rate = self.__config.baud_rate, controller = self)
                except Exception:
                    log.warning(f"Could not start serial {path}")
                    continue

                log.debug(f"Starting serial device {serial.name}")
                await serial.start()

                self.children.append(serial)
                self.__devices[path] = serial

    def device_identified(self, device: Serial):
        if device.path not in self.__devices:
            return

        if self.__device_added_callback:
            self.__device_added_callback(device)

    def device_lost(self, device: Serial):
        if device.path not in self.__devices:
            return

        self.__devices_to_remove.append(device)
