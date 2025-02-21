import enum
import logging

import yaml
import pydantic

import krystalium


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class Config:
    update_rate: int = 60

    api: krystalium.api.Config = pydantic.Field(default_factory = krystalium.api.Config)
    unreal: krystalium.unreal.Config = pydantic.Field(default_factory = krystalium.unreal.Config)
    serial: krystalium.serialcontroller.Config = pydantic.Field(default_factory = krystalium.serialcontroller.Config)


class Main(krystalium.component.MainLoop):
    class State(enum.Enum):
        Input = enum.auto()
        InputLocked = enum.auto()
        SampleLookup = enum.auto()
        SampleActive = enum.auto()
        Enlisted = enum.auto()

    def __init__(self):
        try:
            with open("config.yml", "r") as f:
                data = yaml.safe_load(f)
                self.__config = Config(**data)
        except FileNotFoundError:
            self.__config = Config()

        super().__init__(update_rate = self.__config.update_rate, interval = 0.1)

        self.__log = logging.getLogger()
        self.__input_values = []
        self.__state = self.State.Input
        self.__input_timeout = 0

    async def start(self):
        self.__api = krystalium.api.Api(self.__config.api)
        self.children.append(self.__api)
        self.__unreal = krystalium.unreal.UnrealCommunication(self.__config.unreal)
        self.children.append(self.__unreal)

        self.__serial_controller = krystalium.serialcontroller.SerialController(config = self.__config.serial)
        self.children.append(self.__serial_controller)

        self.__number_input = krystalium.number_input.NumberInput(controller = self.__serial_controller)
        self.children.append(self.__number_input)

        self.__rfid = krystalium.rfid.Rfid(controller = self.__serial_controller)
        self.children.append(self.__rfid)

        await super().start()

    async def update(self, elapsed: float) -> None:
        if self.__state == self.State.Input:
            await self.input_mode(elapsed)
        elif self.__state == self.State.InputLocked:
            await self.input_locked_mode(elapsed)
        elif self.__state == self.State.SampleLookup:
            await self.sample_lookup(elapsed)
        elif self.__state == self.State.SampleActive:
            await self.sample_active(elapsed)
        elif self.__state == self.State.Enlisted:
            await self.enlisted_mode(elapsed)

    async def update_input(self, *, elapsed: float, max: int) -> bool:
        if self.__input_timeout > 0:
            self.__input_timeout -= elapsed

            if self.__input_timeout <= 0:
                self.__input_values = []
                self.__number_input.clear()
                await self.__unreal.clear_numbers()
                await self.__unreal.message("Enter Code:")
                return True

        if len(self.__input_values) >= max:
            return False

        if len(self.__number_input.input) != len(self.__input_values):
            self.__input_values = self.__number_input.input.copy()
            await self.__unreal.set_numbers(self.__input_values)
            self.__input_timeout = 10

        return False

    async def input_mode(self, elapsed: float) -> None:
        await self.update_input(elapsed = elapsed, max = 5)

        if len(self.__input_values) < 5:
            return

        if self.__input_values == [0, 0, 0, 0, 0]:
            self.__state = self.State.SampleLookup
            await self.__unreal.clear_numbers()
            await self.__unreal.message("Awaiting Sample")
        else:
            number = ''.join(map(str, self.__input_values))
            self.__log.debug(f"Looking up enlisted {number}")
            enlisted = await self.__api.get_enlisted_by_number(number)
            if enlisted:
                await self.__unreal.update_from_enlisted(enlisted)
                await self.__unreal.reinitialize()
                await self.__unreal.valid()
                self.__state = self.State.Enlisted
            else:
                self.__number_input.clear()
                self.__input_values = []
                await self.__unreal.message("Invalid Input!")
                await self.__unreal.invalid()
                self.__input_timeout = 5
                self.__state = self.State.InputLocked

    async def input_locked_mode(self, elapsed: float) -> None:
        if await self.update_input(elapsed = elapsed, max = 0):
            self.__state = self.State.Input

    async def maybe_reset(self, elapsed: float) -> bool:
        await self.update_input(elapsed = elapsed, max = 3)
        if self.__input_values == [0, 0, 0]:
            self.__log.debug("Reset")
            await self.__unreal.reset()
            await self.__unreal.message("Enter Code:")
            self.__input_values = []
            self.__number_input.clear()
            self.__state = self.State.Input
            return True

        return False

    async def sample_lookup(self, elapsed: float) -> None:
        if await self.maybe_reset(elapsed):
            return

        blood = self.__rfid.blood_sample
        refined = self.__rfid.refined_sample

        if blood is None or refined is None:
            return

        await self.__unreal.update_from_samples(blood, refined)
        await self.__unreal.reinitialize()
        await self.__unreal.valid()

        self.__state = self.State.SampleActive

    async def sample_active(self, elapsed: float) -> None:
        await self.maybe_reset(elapsed)

    async def enlisted_mode(self, elapsed: float) -> None:
        await self.maybe_reset(elapsed)


if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)

    main = Main()
    main.run()
