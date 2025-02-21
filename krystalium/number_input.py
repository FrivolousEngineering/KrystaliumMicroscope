import logging
import time

from .component import Component


log = logging.getLogger(__name__)


class NumberInput(Component):
    def __init__(self, *, name: str | None = None, controller) -> None:
        super().__init__(name = name, interval = 1.0)
        self.__controller = controller
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

    async def update(self, elapsed: float) -> None:
        serials = self.__controller.devices_by_name("rotary")
        if serials and self.__serial is None:
            self.__serial = serials[0]
            self.__serial.set_callback(self.__process)
            log.info(f"Found serial device {self.__serial.name}")

    def __process(self, line):
        try:
            value = int(line)
        except ValueError:
            return

        if value < 0 or value > 9:
            return

        self.__input_values.append(value)
        self.__last_input = time.perf_counter()
