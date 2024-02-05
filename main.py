import asyncio
import logging

import aiofiles
import yaml
import pydantic

import krystalium


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class Config:
    api: krystalium.api.Config = pydantic.Field(default_factory = krystalium.api.Config)
    unreal: krystalium.medical.Config = pydantic.Field(default_factory = krystalium.medical.Config)
    rfid: krystalium.rfid.Config = pydantic.Field(default_factory = krystalium.rfid.Config)


async def main():
    try:
        async with aiofiles.open("config.yml", "r") as f:
            contents = await f.read()
            data = yaml.safe_load(contents)
            config = Config(**data)
    except FileNotFoundError:
        config = Config()

    api = krystalium.api.Api(config.api)
    unreal = krystalium.medical.UnrealCommunication(config.unreal)
    rfid = krystalium.rfid.RfidController(config.rfid)

    await api.start()
    await unreal.start()
    await rfid.start()

    try:
        while True:
            id = await rfid.detect()

            if not id:
                await unreal.play_stop()
                continue

            sample = await api.get(id)

            await unreal.update(sample)
            await unreal.reinitialize()
            await unreal.play_startup()
    except Exception as e:
        logging.exception()

    await rfid.stop()
    await unreal.stop()
    await api.stop()


if __name__ == "__main__":
    logging.basicConfig(level = logging.WARNING)

    asyncio.run(main())
