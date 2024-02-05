import aiofiles
import pydantic


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class Config:
    device_path: str = "/dev/ttyACM0"


class RfidController:
    def __init__(self, config: Config) -> None:
        self.__config = config

    async def start(self):
        pass

    async def stop(self):
        pass

    async def detect(self) -> str:
        pass
