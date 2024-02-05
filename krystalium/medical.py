import logging
import dataclasses
import typing

import aiohttp
from pydantic import Field
from pydantic.dataclasses import dataclass


log = logging.getLogger(__name__)


@dataclass(kw_only = True, frozen = True)
class Config:
    host: str = "localhost"
    port: int = 30010


@dataclass(kw_only = True, frozen = True)
class Color:
    r: float
    g: float
    b: float
    a: float

    @classmethod
    def mix(first, second, amount):
        return Color(
            first.r * (1.0 - amount) + second.r * amount,
            first.g * (1.0 - amount) + second.g * amount,
            first.b * (1.0 - amount) + second.b * amount,
            first.a * (1.0 - amount) + second.a * amount,
        )


@dataclass(kw_only = True, frozen = True)
class SystemParameters:
    rbc_count: int | None = Field(title = "RBC Count", default = None)
    rbc_tint: Color | None = Field(title = "RBC Tint", default = None)
    rbc_movement_multiplier: float | None = Field(title = "RBC Movement Multiplier", default = None)
    rbc_scale: float | None = Field(title = "RBC Scale", default = None)

    wbc_count: int | None = Field(title = "WBC Count", default = None)
    wbc_tint: Color | None = Field(title = "WBC Tint", default = None)
    wbc_movement_multiplier: float | None = Field(title = "WBC Movement Multiplier", default = None)
    wbc_scale: float | None = Field(title = "WBC Scale", default = None)

    platelet_count: int | None = Field(title = "Platelet Count", default = None)
    platelet_tint: Color | None = Field(title = "Platelet Tint", default = None)
    platelet_movement_multiplier: float | None = Field(title = "Platelet Movement Multiplier", default = None)
    platelet_scale: float | None = Field(title = "Platelet Scale", default = None)

    movement_speed: float | None = Field(title = "Movement Speed", default = None)

    @classmethod
    def merged(first, second):
        def merge(first, second, op):
            if first is None and second is None:
                return None

            if first is not None and second is None:
                return first

            if first is None and second is not None:
                return second

            return op(first, second)

        params = SystemParameters()

        params.rbc_count = merge(first.rbc_count, second.rbc_count, lambda a, b: a + b)
        params.rbc_tint = merge(first.rbc_tint, second.rbc_tint, Color.mix)
        params.rbc_movement_multiplier = merge(first.rbc_movement_multiplier, second.rbc_movement_multiplier, lambda a, b: a + b)

        return params


class UnrealCommunication:
    SystemObjectPath: str = "/Game/Medical/L_Medical.L_Medical:PersistentLevel.NiagaraActor_1.NiagaraComponent0"
    LevelObjectPath: str = "/Game/Medical/L_Medical.L_Medical:PersistentLevel.L_Medical_C_0"

    def __init__(self, config: Config) -> None:
        self.__config = config

    async def start(self):
        self.__session = aiohttp.ClientSession(f"http://{self.__config.host}:{self.__config.port}")

    async def stop(self):
        await self.play_stop()
        await self.__session.close()

    async def update_from_sample(self, sample):
        parameters = effect_table.get(sample.primary_action, {}).get(sample.primary_target, None)
        if not parameters:
            return

        secondary_parameters = effect_table.get(sample.secondary_action, {}).get(sample.secondary_target, None)
        if secondary_parameters:
            parameters = SystemParameters.merged(parameters, secondary_parameters)

        batch = []

        for field in dataclasses.fields(parameters):
            value = getattr(parameters, field.name, None)
            if value is None:
                continue

            niagara_function, niagara_value = self.__toNiagara(field.type, value)
            if niagara_function is None:
                continue

            data = {
                "RequestId": len(batch),
                "URL": "/remote/object/call",
                "Verb": "PUT",
                "Body": {
                    "objectPath": self.SystemObjectPath,
                    "functionName": niagara_function,
                    "parameters": {
                        "InVariableName": field.default.title,
                        "InValue": niagara_value,
                    }
                }
            }

            batch.append(data)

        if batch:
            # Can't use actual batch API as it crashes for some reason
            for entry in batch:
                async with self.__session.put(entry["URL"], json = entry["Body"]) as response:
                    if not response.ok:
                        log.warning(f"Batch execution failed ({response.status}): {response.reason} {await response.text()}")

    async def reinitialize(self):
        await self.__rpc_call(object_path = self.SystemObjectPath, function_name = "ReinitializeSystem")

    async def play_startup(self):
        await self.__rpc_call(object_path = self.LevelObjectPath, function_name = "PlayStartup")

    async def play_stop(self):
        await self.__rpc_call(object_path = self.LevelObjectPath, function_name = "PlayStop")

    async def __rpc_call(self, *, object_path: str, function_name: str, **kwargs) -> bool:
        data = {
            "objectPath": object_path,
            "functionName": function_name,
        }
        if kwargs:
            data["parameters"] = kwargs

        async with self.__session.put("/remote/object/call", json = data) as response:
            if not response.ok:
                log.warning(f"Remote object call failed ({response.status}): {response.reason} {await response.text()}")
                return False
            else:
                return True

    @staticmethod
    def __toNiagara(python_type, value):
        source_type = typing.get_args(python_type)[0]

        if source_type == bool:
            return "SetNiagaraVariableBool", bool(value)
        elif source_type == int:
            return "SetNiagaraVariableInt", int(value)
        elif source_type == float:
            return "SetNiagaraVariableFloat", float(value)
        elif source_type == str:
            return "SetNiagaraVariableString", str(value)
        elif source_type == Color:
            return "SetNiagaraVariableLinearColor", {"R": value.r, "G": value.g, "B": value.b, "A": value.a}

        return None, None



effect_table = {
    "Contracting": {
        "Gas": SystemParameters(
            rbc_scale = 0.5,
            rbc_movement_multiplier = 0.5,
            wbc_scale = 0.5,
            wbc_movement_multiplier = 0.5,
        )
    }
}
