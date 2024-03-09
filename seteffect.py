import asyncio
import logging
import signal
import argparse

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


async def main(args):
    try:
        async with aiofiles.open("config.yml", "r") as f:
            contents = await f.read()
            data = yaml.safe_load(contents)
            config = Config(**data)
    except FileNotFoundError:
        config = Config()

    unreal = krystalium.medical.UnrealCommunication(config.unreal)
    await unreal.start()

    blood = krystalium.api.BloodSample(id = 0, rfid_id = "", origin = "test", strength = 0, action = "None", target = "None")
    if args.test_all:
        for action, targets in krystalium.effect_table.effect_table.items():
            for target, modifiers in targets.items():
                if not modifiers:
                    continue

                sample = krystalium.api.RefinedSample(
                    id = 0,
                    rfid_id = "",
                    primary_action = action,
                    primary_target = target,
                    secondary_action = "None",
                    secondary_target = "None",
                    purity = "",
                    purity_score = 12
                )

                await unreal.set_active(False)
                await asyncio.sleep(5)
                await unreal.update_from_samples(blood, sample)
                await unreal.set_active(True)

    else:
        blood = krystalium.api.BloodSample(
            id = 0,
            rfid_id = "",
            origin = "test",
            strength = args.blood_strength,
            action = args.blood_action,
            target = args.blood_target,
        )

        sample = krystalium.api.RefinedSample(
            id = 0,
            rfid_id = "",
            primary_action = args.primary_action,
            primary_target = args.primary_target,
            secondary_action = args.secondary_action,
            secondary_target = args.secondary_target,
            purity = "",
            purity_score = args.purity,
        )

        await unreal.update_from_samples(blood, sample)
        await unreal.reinitialize()
        await unreal.set_active(True)
        await asyncio.sleep(5)

    await unreal.stop()

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("--blood-action", default = "None")
    parser.add_argument("--blood-target", default = "None")
    parser.add_argument("--blood-strength", default = 0)
    parser.add_argument("--primary-action", required = True)
    parser.add_argument("--primary-target", required = True)
    parser.add_argument("--purity", default = 12)
    parser.add_argument("--secondary-action", default = "None")
    parser.add_argument("--secondary-target", default = "None")
    parser.add_argument("--test-all", action = "store_true")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    main_task = asyncio.ensure_future(main(args))
    for s in signal.SIGINT, signal.SIGTERM:
        loop.add_signal_handler(s, main_task.cancel)

    try:
        loop.run_until_complete(main_task)
    finally:
        loop.close()
