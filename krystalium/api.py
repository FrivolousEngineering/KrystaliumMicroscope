import logging

import aiohttp
import pydantic

log = logging.getLogger(__name__)


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class Sample:
    id: str


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class Config:
    host: str = "localhost"
    port: int = 9999


class Api:
    def __init__(self, config: Config) -> None:
        self.__config = config

    async def start(self) -> None:
        self.__session = aiohttp.ClientSession(f"http://{self.__config.host}:{self.__config.port}")

    async def stop(self) -> None:
        await self.__session.close()

    async def get(self, id: str) -> Sample | None:
        async with self.__session.get("/sample") as response:
            if response.status != 200:
                logging.warning(f"Could not get data for ID {id}")
                return None

            json = await response.json()

            sample = Sample(
                id = id,

            )

            return sample
