import asyncio
import logging
import types
from typing import Any

import aiohttp
import pydantic
from async_lru import alru_cache

from .component import Component


log = logging.getLogger(__name__)


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class JsonApiObject:
    id: str
    type: str
    attributes: object = pydantic.Field(default_factory = dict)
    relationships: object = pydantic.Field(default_factory = dict)
    included: list["JsonApiObject"] = pydantic.Field(default_factory = list)

    @classmethod
    def from_json(cls, json: dict[str, Any], included: dict[str, Any] | None = None) -> "JsonApiObject":
        data = json["data"] if "data" in json else json

        if included is None:
            included = [cls.from_json(entry) for entry in json.get("included", [])]

        return cls(
            id = data["id"],
            type = data["type"],
            attributes = types.SimpleNamespace(**data["attributes"]),
            relationships = types.SimpleNamespace(**data.get("relationships", {})),
            included = included,
        )


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class Effect:
    id: int
    name: str
    strength: int
    action: str
    target: str



@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class BloodSample:
    id: int
    rfid_id: str
    strength: int
    effect: Effect


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class RefinedSample:
    id: int
    rfid_id: str

    strength: int
    primary_action: str
    primary_target: str
    secondary_action: str
    secondary_target: str


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class Config:
    host: str = "localhost"
    port: int = 8000


class Api(Component):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.__config = config

    async def start(self) -> None:
        self.__session = aiohttp.ClientSession(f"http://{self.__config.host}:{self.__config.port}")

    async def stop(self) -> None:
        await self.__session.close()

    async def get_samples(self, first_id: str, second_id: str):
        first_is_blood = False
        async with self.__session.get(f"/blood/{first_id}") as response:
            if response.ok:
                first_is_blood = True
            else:
                first_is_blood = False

        blood_id = first_id if first_is_blood else second_id
        krystal_id = second_id if first_is_blood else first_id

        async with asyncio.TaskGroup() as tg:
            blood_task = tg.create_task(self.get_blood_sample(blood_id))
            refined_task = tg.create_task(self.get_refined_sample(krystal_id))

        return blood_task.result(), refined_task.result()

    @alru_cache(maxsize = 500)
    async def get_blood_sample(self, id: str) -> BloodSample | None:
        async with self.__session.get(f"/blood/{id}") as response:
            if not response.ok:
                log.warning(f"Could not get blood sample with ID {id}")
                return None

            json = await response.json()

            sample = BloodSample(**json)

            log.debug(f"Found blood sample: {sample}")

            return sample

    @alru_cache(maxsize = 500)
    async def get_refined_sample(self, id: str) -> RefinedSample | None:
        async with self.__session.get(f"/refined/{id}") as response:
            if not response.ok:
                log.warning(f"Could not get refined sample with ID {id}")
                return None

            json = await response.json()

            sample = RefinedSample(**json)

            log.debug(f"Found refined sample: {sample}")

            return sample
