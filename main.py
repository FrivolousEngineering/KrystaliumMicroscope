import asyncio
import logging
import signal

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
            rfid_id = await rfid.detect()

            if rfid_id is None:
                continue

            if rfid_id == "":
                await unreal.play_stop()
                continue

            sample = await api.get(rfid_id)
            if not sample:
                continue

            await unreal.update_from_sample(sample)
            await unreal.reinitialize()
            await unreal.play_startup()
    finally:
        await rfid.stop()
        await unreal.stop()
        await api.stop()


if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)

    loop = asyncio.get_event_loop()
    main_task = asyncio.ensure_future(main())
    for s in signal.SIGINT, signal.SIGTERM:
        loop.add_signal_handler(s, main_task.cancel)

    try:
        loop.run_until_complete(main_task)
    finally:
        loop.close()
