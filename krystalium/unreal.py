import logging
import dataclasses
from typing import Any

import aiohttp
from pydantic import Field
from pydantic.dataclasses import dataclass

from .component import Component
from .types import Color, ParameterModifier
from . import effect_table as et
from .api import BloodSample, RefinedSample, Enlisted


log = logging.getLogger(__name__)


@dataclass(kw_only = True, frozen = True)
class Config:
    host: str = "localhost"
    port: int = 30010


@dataclass(kw_only = True)
class SystemParameters:
    base_spawn_rate: float = Field(title = "Base Spawn Rate", default = 10.0)
    base_movement_speed: float = Field(title = "Base Movement", default = 6.0)
    base_movement_jitter: float = Field(title = "Base Movement Jitter", default = 0.1)
    base_color: Color = Field(title = "Base Color", default = Color(r = 0.7, g = 0.7, b = 0.7, a = 1.0))

    rbc_spawn_chance: float = Field(title = "RBC Spawn Chance", default = 0.5)
    rbc_tint: Color = Field(title = "RBC Tint", default = Color(r = 0.0, g = 0.0, b = 0.0, a = 0.0))
    rbc_scale: float = Field(title = "RBC Scale", default = 1.0)
    rbc_movement_multiplier: float = Field(title = "RBC Movement Multiplier", default = 1.0)
    rbc_movement_jitter: float = Field(title = "RBC Movement Jitter", default = 0.0)
    rbc_normal_chance: float = Field(title = "RBC Normal Chance", default = 1.0)
    rbc_helmet_chance: float = Field(title = "RBC Helmet Chance", default = 0.0)
    rbc_burr_chance: float = Field(title = "RBC Burr Chance", default = 0.0)
    rbc_oval_chance: float = Field(title = "RBC Oval Chance", default = 0.0)

    wbc_spawn_chance: float = Field(title = "WBC Spawn Chance", default = 0.01)
    wbc_tint: Color = Field(title = "WBC Tint", default = Color(r = 0.0, g = 0.0, b = 0.0, a = 0.0))
    wbc_scale: float = Field(title = "WBC Scale", default = 1.0)
    wbc_movement_multiplier: float = Field(title = "WBC Movement Multiplier", default = 2.0)
    wbc_movement_jitter: float = Field(title = "WBC Movement Jitter", default = 0.0)

    platelet_spawn_chance: float = Field(title = "Platelet Spawn Chance", default = 0.1)
    platelet_tint: Color = Field(title = "Platelet Tint", default = Color(r = 0.0, g = 0.0, b = 0.0, a = 0.0))
    platelet_scale: float = Field(title = "Platelet Scale", default = 1.0)
    platelet_movement_multiplier: float = Field(title = "Platelet Movement Multiplier", default = 0.75)
    platelet_movement_jitter: float = Field(title = "Platelet Movement Jitter", default = 0.0)

    strand_tint: Color = Field(title = "Coagulated Strand Tint", default = Color(r = -0.2, g = -0.2, b = -0.2, a = 0.0))
    strand_spawn_chance: float = Field(title = "Coagulated Strand Spawn Chance", default = 0.0)
    strand_scale: float = Field(title = "Coagulated Strand Scale", default = 1.0)
    strand_lifetime: float = Field(title = "Coagulated Strand Lifetime", default = 1000.0)
    strand_movement: float = Field(title = "Coagulated Strand Movement", default = 0.03)

    krystal_spawn_chance: float = Field(title = "Krystal Spawn Chance", default = 0.0)
    krystal_tint: Color = Field(title = "Krystal Tint", default = Color(r = -0.4, g = -0.3, b = 2.0, a = 0.0))
    krystal_scale: float = Field(title = "Krystal Scale", default = 0.5)
    krystal_movement_multiplier: float = Field(title = "Krystal Movement Multiplier", default = 1.0)
    krystal_movement_jitter: float = Field(title = "Krystal Movement Jitter", default = 0.0)

    plant_spawn_chance: float = Field(title = "Plant Spawn Chance", default = 0.0001)
    plant_tint: Color = Field(title = "Plant Tint", default = Color(r = -0.2, g = -0.1, b = -0.2, a = 0.0))
    plant_scale: float = Field(title = "Plant Scale", default = 1.0)
    plant_movement_multiplier: float = Field(title = "Plant Movement Multiplier", default = 1.0)
    plant_movement_jitter: float = Field(title = "Plant Movement Jitter", default = 0.0)

    dead_spawn_chance: float = Field(title = "Dead Cell Spawn Chance", default = 0.0001)
    dead_tint: Color = Field(title = "Dead Cell Tint", default = Color(r = 0.0, g = 0.0, b = 0.0, a = 0.0))
    dead_scale: float = Field(title = "Dead Cell Scale", default = 1.0)
    dead_movement_multiplier: float = Field(title = "Dead Cell Movement Multiplier", default = 1.0)

    def to_batch(self) -> list[dict]:
        batch: list[dict] = []
        for field in dataclasses.fields(self):
            value = getattr(self, field.name, None)
            if value is None:
                continue

            niagara_function, niagara_value = UnrealCommunication.toNiagara(field.type, value)
            if niagara_function is None:
                continue

            data = {
                "RequestId": len(batch),
                "URL": "/remote/object/call",
                "Verb": "PUT",
                "Body": {
                    "objectPath": UnrealCommunication.SystemObjectPath,
                    "functionName": niagara_function,
                    "parameters": {
                        "InVariableName": field.default.title,
                        "InValue": niagara_value,
                    }
                }
            }

            batch.append(data)

        return batch


class UnrealCommunication(Component):
    SystemObjectPath: str = "/Game/Medical/L_Medical.L_Medical:PersistentLevel.NiagaraActor_1.NiagaraComponent0"
    ControllerObjectPath: str = "/Game/Medical/L_Medical.L_Medical:PersistentLevel.BP_Controller_C_1"

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.__config = config
        self.__active = False
        self.__session: aiohttp.ClientSession | None = None

    @property
    def connected(self) -> bool:
        return self.__session is not None

    @property
    def active(self) -> bool:
        return self.__active

    async def set_active(self, active: bool) -> None:
        if active == self.__active:
            return

        self.__active = active

    async def start(self) -> None:
        self.__session = aiohttp.ClientSession(f"http://{self.__config.host}:{self.__config.port}")

        try:
            await self.__session.get("/remote/info")

            await self.reset()
            await self.message("Enter Code:")
        except aiohttp.ClientConnectionError:
            await self.__session.close()
            self.__session = None
            log.warning("Could not connect to Unreal application")

    async def stop(self):
        await self.clear_numbers()

        if self.__session:
            await self.__session.close()

    async def update_from_samples(self, blood_sample: BloodSample, krystal_sample: RefinedSample) -> None:
        if not self.__session:
            return

        parameters = SystemParameters()

        blood_modifiers = et.get_modifiers(blood_sample.effect.action, blood_sample.effect.target)
        if blood_modifiers is None:
            log.warning(f"Unknown action/target combination for blood sample: {blood_sample.effect.action}/{blood_sample.effect.target}")
        else:
            self.apply_modifiers(parameters, blood_modifiers, blood_sample.strength)

        primary_modifiers = et.get_modifiers(krystal_sample.primary_action, krystal_sample.primary_target)
        if primary_modifiers is None:
            log.warning(f"Unknown action/target combination for primary: {krystal_sample.primary_action}/{krystal_sample.primary_target}")
        else:
            self.apply_modifiers(parameters, primary_modifiers, krystal_sample.strength)

        secondary_modifiers = et.get_modifiers(krystal_sample.secondary_action, krystal_sample.secondary_target)
        if secondary_modifiers is None:
            log.warning(f"Unknown action/target combination for secondary: {krystal_sample.secondary_action}/{krystal_sample.secondary_target}")
        else:
            self.apply_modifiers(parameters, secondary_modifiers, krystal_sample.strength)

        await self.__batch_call(parameters.to_batch())

    async def update_from_enlisted(self, enlisted: Enlisted) -> None:
        if not self.__session:
            return

        parameters = SystemParameters()

        for effect in enlisted.effects:
            modifiers = et.get_modifiers(effect.action, effect.target)
            if modifiers is not None:
                self.apply_modifiers(parameters, modifiers, effect.strength)
            else:
                log.warning(f"Found no modifiers for effect {effect.action}/{effect.target}")

        await self.__batch_call(parameters.to_batch())

    async def set_numbers(self, numbers: list[int]) -> None:
        await self.__rpc_call(object_path = self.ControllerObjectPath, function_name = "SetNumbers", Numbers = numbers)

    async def clear_numbers(self) -> None:
        await self.__rpc_call(object_path = self.ControllerObjectPath, function_name = "ClearNumbers")

    async def valid(self):
        await self.__rpc_call(object_path = self.ControllerObjectPath, function_name = "Valid")

    async def invalid(self):
        await self.__rpc_call(object_path = self.ControllerObjectPath, function_name = "Invalid")

    async def reinitialize(self):
        await self.__rpc_call(object_path = self.SystemObjectPath, function_name = "ReinitializeSystem")

    async def message(self, message: str) -> None:
        await self.__rpc_call(object_path = self.ControllerObjectPath, function_name = "Message", Message = message)

    async def reset(self) -> None:
        await self.__rpc_call(object_path = self.ControllerObjectPath, function_name = "Reset")

    async def __rpc_call(self, *, object_path: str, function_name: str, **kwargs) -> bool:
        if not self.__session:
            return False

        data: dict[str, Any] = {
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

    async def __batch_call(self, batch: list[dict]) -> bool:
        if not self.__session:
            return False

        # Can't use actual batch API as it crashes for some reason
        for entry in batch:
            async with self.__session.put(entry["URL"], json = entry["Body"]) as response:
                if not response.ok:
                    log.warning(f"Batch execution failed ({response.status}): {response.reason} {await response.text()}")
                    return False

        return True

    def apply_modifiers(self, parameters: SystemParameters, modifiers: list[ParameterModifier], strength: int):
        for modifier in modifiers:
            current_value = getattr(parameters, modifier.parameter)
            modifier_strength = 0.05 + ((strength - 2) / 10) * 0.95

            new_value = current_value
            if modifier.operation == "add":
                new_value = current_value + modifier.value * modifier_strength
            elif modifier.operation == "mul":
                new_value = current_value * (modifier.value * (1.0 + modifier_strength / 2))
            elif modifier.operation == "set":
                new_value = modifier.value * modifier_strength
            elif modifier.operation == "set_unscaled":
                new_value = modifier.value
            else:
                log.warning(f"Unknown modifier operation: {modifier.operation}")

            setattr(parameters, modifier.parameter, new_value)

    @staticmethod
    def toNiagara(source_type, value):
        if source_type == bool:
            return "SetNiagaraVariableBool", bool(value)
        elif source_type == int:
            return "SetNiagaraVariableInt", int(value)
        elif source_type == float:
            return "SetNiagaraVariableFloat", float(value)
        elif source_type == str:
            return "SetNiagaraVariableString", str(value)
        elif source_type == Color:
            return "SetNiagaraVariableLinearColor", {"R": value.r, "G": value.g, "B": value.b, "A": value.a if value.a is not None else 1.0}

        return None, None
