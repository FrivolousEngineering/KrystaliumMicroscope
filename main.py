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
    rfid_first: krystalium.rfid.Config = pydantic.Field(default_factory = krystalium.rfid.Config)
    rfid_second: krystalium.rfid.Config = pydantic.Field(default_factory = krystalium.rfid.Config)


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
    rfid_first = krystalium.rfid.RfidController(config.rfid_first)
    rfid_second = krystalium.rfid.RfidController(config.rfid_second)

    await api.start()
    await unreal.start()
    await rfid_first.start()
    await rfid_second.start()

    try:
        while True:
            await asyncio.sleep(0.01)

            first_id = rfid_first.rfid_id
            second_id = rfid_second.rfid_id

            if first_id == "" or second_id == "":
                await unreal.set_active(False)
                continue

            if not unreal.active:
                blood_sample, krystal_sample = await api.get_samples(first_id, second_id)
                if not blood_sample or not krystal_sample:
                    continue

                await unreal.update_from_samples(blood_sample, krystal_sample)
                await unreal.reinitialize()
                await unreal.set_active(True)
    finally:
        await rfid_first.stop()
        await rfid_second.stop()
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
