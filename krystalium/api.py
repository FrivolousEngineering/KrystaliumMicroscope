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

    @classmethod
    def from_jsonapi(cls, json_api: JsonApiObject) -> "Effect":
        return cls(
            id = int(json_api.id),
            name = json_api.attributes.name,
            strength = int(json_api.attributes.strength),
            action = json_api.attributes.action,
            target = json_api.attributes.target,
        )


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class BloodSample:
    id: int
    rfid_id: str
    strength: int
    effect: Effect

    @classmethod
    def from_jsonapi(cls, json_api: JsonApiObject) -> "BloodSample":
        effect_id = json_api.relationships.effect["data"]["id"]

        effect = None
        for include in json_api.included:
            if include.id == effect_id:
                effect = Effect.from_jsonapi(include)
                break

        return cls(
            id = int(json_api.id),
            rfid_id = json_api.attributes.rfid_id,
            strength = json_api.attributes.strength,
            effect = effect,
        )


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class RefinedSample:
    id: int
    rfid_id: str

    strength: int
    primary_action: str
    primary_target: str
    secondary_action: str
    secondary_target: str

    @classmethod
    def from_jsonapi(cls, json_api: JsonApiObject) -> "RefinedSample":
        return cls(
            id = int(json_api.id),
            rfid_id = json_api.attributes.rfid_id,
            strength = int(json_api.attributes.strength),
            primary_action = json_api.attributes.primary_action,
            primary_target = json_api.attributes.primary_target,
            secondary_action = json_api.attributes.secondary_action,
            secondary_target = json_api.attributes.secondary_target,
        )


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class Enlisted:
    id: int

    name: str
    number: str

    effects: list[Effect] = pydantic.Field(default_factory = list)

    @classmethod
    def from_jsonapi(cls, json_api: JsonApiObject) -> "Enlisted":
        effect_ids = [entry["id"] for entry in json_api.relationships.effects["data"]]

        effects = []
        for include in json_api.included:
            if include.id in effect_ids:
                effects.append(Effect.from_jsonapi(include))

        return cls(
            id = int(json_api.id),
            name = json_api.attributes.name,
            number = json_api.attributes.number,
            effects = effects
        )


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
    async def get_effect(self, id: str) -> Effect | None:
        async with self.__session.get(f"/effect/{id}") as response:
            if not response.ok:
                log.warning(f"Could not get effect with ID {id}")
                return None

            jsonapi = JsonApiObject.from_json(await response.json())
            return Effect.from_jsonapi(jsonapi)

    @alru_cache(maxsize = 500)
    async def get_blood_sample(self, id: str) -> BloodSample | None:
        async with self.__session.get(f"/blood/{id}?include=") as response:
            if not response.ok:
                log.warning(f"Could not get blood sample with ID {id}")
                return None

            jsonapi = JsonApiObject.from_json(await response.json())
            return BloodSample.from_jsonapi(jsonapi)

    @alru_cache(maxsize = 500)
    async def get_refined_sample(self, id: str) -> RefinedSample | None:
        async with self.__session.get(f"/refined/{id}") as response:
            if not response.ok:
                log.warning(f"Could not get refined sample with ID {id}")
                return None

            jsonapi = JsonApiObject.from_json(await response.json())
            return RefinedSample.from_jsonapi(jsonapi)

    @alru_cache(maxsize = 500)
    async def get_enlisted(self, id: str) -> Enlisted | None:
        async with self.__session.get(f"/enlisted/{id}?include=effects") as response:
            if not response.ok:
                log.warning(f"Could not get enlisted with ID {id}")
                return None

            jsonapi = JsonApiObject.from_json(await response.json())
            return Enlisted.from_jsonapi(jsonapi)

    @alru_cache(maxsize = 500)
    async def get_enlisted_by_number(self, number: str) -> Enlisted | None:
        async with self.__session.get(f"/enlisted?filter[number]={number}&include=effects") as response:
            if not response.ok:
                return None

            json = await response.json()
            if len(json["data"]) > 0:
                jsonapi = JsonApiObject.from_json(json["data"][0])
                return Enlisted.from_jsonapi(jsonapi)

            return None
