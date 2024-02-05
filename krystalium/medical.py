import logging

import aiohttp
import pydantic


logger = logging.getLogger(__name__)


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class Config:
    host: str = "localhost"
    port: int = 30010

class UnrealCommunication:
    SystemObjectPath: str = "/Game/Medical/L_Medical.L_Medical:PersistentLevel.NiagaraActor_1.NiagaraComponent0"
    LevelObjectPath: str = "/Game/Medical/L_Medical.L_Medical:PersistentLevel.L_Medical_C_0"


    def __init__(self, config: Config) -> None:
        self.__config = config

    async def start(self):
        self.__session = aiohttp.ClientSession(f"http://{self.__config.host}:{self.__config.port}")

    async def stop(self):
        self.__session.close()

    async def update_from_sample(self, sample):
        batch = []

        # batch.append(self.create_request())

        async with self.__session.put("/remote/batch", json = batch) as response:
            if response.status != 200:
                logger.warning("Failed to execute update batch")

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
            if response.status != 200:
                logger.warning(f"Remote object call failed ({response.status}): {response.reason}")
                return False
            else:
                return True
