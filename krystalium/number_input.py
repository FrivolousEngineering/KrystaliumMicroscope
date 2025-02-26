import logging
import time

from .component import Component


log = logging.getLogger(__name__)


class NumberInput(Component):
    def __init__(self, *, name: str | None = None) -> None:
        super().__init__(name = name)
        self.__serial = None
        self.__input_values: list[int] = []
        self.__last_input: int = 0

    @property
    def input(self) -> list[int]:
        return self.__input_values

    @property
    def last_input(self) -> float:
        return self.__last_input

    def clear(self):
        self.__input_values = []

    def set_device(self, device):
        if self.__serial:
            self.__serial.set_callback(None)

        if device is not None:
            self.__serial = device
            self.__serial.set_callback(self.__process)
            log.info(f"Using serial device {self.__serial.name}")

    def __process(self, line):
        try:
            value = int(line)
        except ValueError:
            return

        if value < 0 or value > 9:
            return

        self.__input_values.append(value)
        self.__last_input = time.perf_counter()
