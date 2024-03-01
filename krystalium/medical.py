import logging
import dataclasses

import aiohttp
from pydantic import Field
from pydantic.dataclasses import dataclass

from .types import Color, ParameterModifier
from .effect_table import effect_table

log = logging.getLogger(__name__)


@dataclass(kw_only = True, frozen = True)
class Config:
    host: str = "localhost"
    port: int = 30010


@dataclass(kw_only = True)
class SystemParameters:
    base_spawn_rate: float = Field(title = "Base Spawn Rate", default = 10.0)
    base_movement_speed: float = Field(title = "Base Movement", default = 6.0)
    base_movement_jitter: float = Field(title = "Base Movement Jitter", default = 0.0)
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

    platelet_spawn_chance: float | None = Field(title = "Platelet Spawn Chance", default = 0.1)
    platelet_tint: Color = Field(title = "Platelet Tint", default = Color(r = 0.0, g = 0.0, b = 0.0, a = 0.0))
    platelet_scale: float = Field(title = "Platelet Scale", default = 1.0)
    platelet_movement_multiplier: float = Field(title = "Platelet Movement Multiplier", default = 0.75)
    platelet_movement_jitter: float = Field(title = "Platelet Movement Jitter", default = 0.0)

    strand_spawn_chance: float | None = Field(title = "Coagulated Strand Spawn Chance", default = 0.0)
    strand_tint: Color = Field(title = "Coagulated Strand Tint", default = Color(r = -0.2, g = -0.2, b = -0.2, a = 0.0))
    strand_scale: float = Field(title = "Coagulated Strand Scale", default = 1.0)
    strand_lifetime: float = Field(title = "Coagulated Strand Lifetime", default = 1000.0)
    strand_movement: float = Field(title = "Coagulated Strand Movement", default = 0.03)

    krystal_spawn_chance: float = Field(title = "Krystal Spawn Chance", default = 0.0)
    krystal_tint: Color = Field(title = "Krystal Tint", default = Color(r = -0.4, g = -0.3, b = 2.0, a = 0.0))
    krystal_scale: float = Field(title = "Krystal Scale", default = 1.0)
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


class UnrealCommunication:
    SystemObjectPath: str = "/Game/Medical/L_Medical.L_Medical:PersistentLevel.NiagaraActor_1.NiagaraComponent0"
    LevelObjectPath: str = "/Game/Medical/L_Medical.L_Medical:PersistentLevel.L_Medical_C_{}"

    def __init__(self, config: Config) -> None:
        self.__config = config
        self.__active = False
        self.__actual_level_object_path = ""

    @property
    def active(self) -> bool:
        return self.__active

    async def set_active(self, active: bool) -> None:
        if active == self.__active:
            return

        self.__active = active
        if self.__active:
            await self.play_startup()
        else:
            await self.play_stop()

    async def start(self):
        self.__session = aiohttp.ClientSession(f"http://{self.__config.host}:{self.__config.port}")

        # To call methods on the Level blueprint we need to get the instance of the blueprint.
        # Unfortunately the exact object path changes per build, so try and iterate until we
        # find it.
        for i in range(10):
            path = self.LevelObjectPath.format(i)
            async with self.__session.put("/remote/object/describe", json = {"objectPath": path}) as response:
                if response.ok:
                    self.__actual_level_object_path = path
                    break
        else:
            log.warning("Could not find level object path")

    async def stop(self):
        await self.play_stop()
        await self.__session.close()

    async def update_from_samples(self, blood_sample, krystal_sample):
        parameters = SystemParameters()

        blood_modifiers = effect_table.get(blood_sample.action, {}).get(blood_sample.target, [])
        if not blood_modifiers:
            log.warning(f"Unknown blood sample origin: {blood_sample.origin}")
        self.apply_modifiers(parameters, blood_modifiers, blood_sample.strength)

        primary_modifiers = effect_table.get(krystal_sample.primary_action, {}).get(krystal_sample.primary_target, [])
        if not primary_modifiers:
            log.warning(f"Unknown action/target combination: {krystal_sample.primary_action}/{krystal_sample.primary_target}")
        self.apply_modifiers(parameters, primary_modifiers, krystal_sample.purity_score)

        secondary_modifiers = effect_table.get(krystal_sample.secondary_action, {}).get(krystal_sample.secondary_target, [])
        if not secondary_modifiers:
            log.warning(f"Unknown action/target combination: {krystal_sample.secondary_action}/{krystal_sample.secondary_target}")
        self.apply_modifiers(parameters, secondary_modifiers, krystal_sample.purity_score)

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

    async def reset(self):
        await self.__rpc_call(object_path = self.__actual_level_object_path, function_name = "Reset")

    async def reinitialize(self):
        await self.__rpc_call(object_path = self.SystemObjectPath, function_name = "ReinitializeSystem")

    async def play_startup(self):
        await self.__rpc_call(object_path = self.__actual_level_object_path, function_name = "PlayStartup")

    async def play_stop(self):
        await self.__rpc_call(object_path = self.__actual_level_object_path, function_name = "PlayStop")

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

    def apply_modifiers(self, parameters: SystemParameters, modifiers: list[ParameterModifier], strength: int):
        for modifier in modifiers:
            current_value = getattr(parameters, modifier.parameter)
            modifier_strength = 1.0 + ((strength - 2) / 10) * 0.5

            new_value = current_value
            if modifier.operation == "add":
                new_value = current_value + modifier.value * modifier_strength
            elif modifier.operation == "mul":
                new_value = current_value * (modifier.value * modifier_strength)
            elif modifier.operation == "set":
                new_value = modifier.value * modifier_strength
            else:
                log.warning(f"Unknown modifier operation: {modifier.operation}")

            setattr(parameters, modifier.parameter, new_value)

    @staticmethod
    def __toNiagara(source_type, value):
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


