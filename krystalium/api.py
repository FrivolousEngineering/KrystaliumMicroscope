import logging

import aiohttp
import pydantic


log = logging.getLogger(__name__)


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class RefinedSample:
    id: int
    rfid_id: str

    primary_action: str
    primary_target: str
    secondary_action: str
    secondary_target: str
    purity: str
    purity_score: int


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class Config:
    host: str = "localhost"
    port: int = 8000


class Api:
    def __init__(self, config: Config) -> None:
        self.__config = config

    async def start(self) -> None:
        self.__session = aiohttp.ClientSession(f"http://{self.__config.host}:{self.__config.port}")

    async def stop(self) -> None:
        await self.__session.close()

    async def get(self, id: str) -> RefinedSample | None:
        async with self.__session.get(f"/refined/{id}") as response:
            if not response.ok:
                log.warning(f"Could not get data for ID {id}")
                return None

            json = await response.json()

            sample = RefinedSample(**json)

            log.debug(f"Found sample: {sample}")

            return sample
