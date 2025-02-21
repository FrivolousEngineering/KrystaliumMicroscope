import logging
import argparse
import asyncio
import enum
import subprocess
import os
import signal

import yaml

import krystalium

from main import Config


class Main(krystalium.component.MainLoop):
    class Mode(enum.StrEnum):
        Sample = "sample"
        Enlisted = "enlisted"
        TestAll = "all"

    def __init__(self, args: argparse.Namespace):
        try:
            with open("config.yml", "r") as f:
                data = yaml.safe_load(f)
                self.__config = Config(**data)
        except FileNotFoundError:
            self.__config = Config()

        super().__init__(update_rate = self.__config.update_rate, interval = 0.01)
        self.__args = args

    async def start(self):
        self.__unreal = krystalium.unreal.UnrealCommunication(self.__config.unreal)
        self.children.append(self.__unreal)

        if self.__args.mode == self.Mode.Enlisted:
            self.__api = krystalium.api.Api(self.__config.api)
            self.children.append(self.__api)

        self.__process = None
        if self.__args.launch:
            self.__process = await asyncio.create_subprocess_exec("Linux/Krystalivm.sh", "-RCWebControlEnable", stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL, start_new_session = True)
            await asyncio.sleep(2)

        await super().start()

    async def stop(self):
        await super().stop()

        if self.__process:
            os.killpg(os.getpgid(self.__process.pid), signal.SIGTERM)
            await self.__process.wait()

    async def update(self, elapsed: float):
        if not self.__unreal.connected:
            raise RuntimeError("Not connected to Unreal")

        if self.__args.mode == self.Mode.Sample:
            await self.blood_sample_mode()
        elif self.__args.mode == self.Mode.Enlisted:
            await self.enlisted_mode()
        elif self.__args.mode == self.Mode.TestAll:
            await self.test_all_mode()

    async def blood_sample_mode(self):
        effect = krystalium.api.Effect(
            id = 0,
            name = "Test Effect",
            strength = self.__args.blood_strength,
            action = self.__args.blood_action,
            target = self.__args.blood_target,
        )

        blood = krystalium.api.BloodSample(
            id = 0,
            rfid_id = "",
            strength = self.__args.blood_strength,
            effect = effect,
        )

        sample = krystalium.api.RefinedSample(
            id = 0,
            rfid_id = "",
            strength = self.__args.purity,
            primary_action = self.__args.primary_action,
            primary_target = self.__args.primary_target,
            secondary_action = self.__args.secondary_action,
            secondary_target = self.__args.secondary_target,
        )

        logging.getLogger().debug("Showing sample result")

        await self.__unreal.update_from_samples(blood, sample)
        await self.__unreal.reinitialize()
        await self.__unreal.valid()
        await asyncio.sleep(30)

        logging.getLogger().debug("Done")

        self.stop_loop()

    async def enlisted_mode(self):
        for character in self.__args.enlisted_number:
            await self.__unreal.append_number(int(character))
            await asyncio.sleep(0.5)

        async with asyncio.TaskGroup() as tg:
            tg.create_task(asyncio.sleep(0.5))
            enlisted = tg.create_task(self.__api.get_enlisted_by_number(self.__args.enlisted_number))

        if enlisted.result() is not None:
            await self.__unreal.update_from_enlisted(enlisted.result())
            await self.__unreal.reinitialize()
            await self.__unreal.valid()
            await asyncio.sleep(30)
        else:
            await self.__unreal.invalid()
            await asyncio.sleep(5)

        self.stop_loop()

    async def test_all_mode(self):
        pass

# async def main(args):
#     try:
#         async with aiofiles.open("config.yml", "r") as f:
#             contents = await f.read()
#             data = yaml.safe_load(contents)
#             config = Config(**data)
#     except FileNotFoundError:
#         config = Config()
#
#     unreal = krystalium.unreal.UnrealCommunication(config.unreal)
#     await unreal.start()
#
#     blood = krystalium.api.BloodSample(id = 0, rfid_id = "", origin = "test", strength = 0, action = "None", target = "None")
#     if args.test_all:
#         for action, targets in krystalium.effect_table.effect_table.items():
#             for target, modifiers in targets.items():
#                 if not modifiers:
#                     continue
#
#                 sample = krystalium.api.RefinedSample(
#                     id = 0,
#                     rfid_id = "",
#                     primary_action = action,
#                     primary_target = target,
#                     secondary_action = "None",
#                     secondary_target = "None",
#                     purity = "",
#                     purity_score = 12
#                 )
#
#                 await unreal.set_active(False)
#                 await asyncio.sleep(5)
#                 await unreal.update_from_samples(blood, sample)
#                 await unreal.set_active(True)
#
#     else:
#         blood = krystalium.api.BloodSample(
#             id = 0,
#             rfid_id = "",
#             origin = "test",
#             strength = args.blood_strength,
#             action = args.blood_action,
#             target = args.blood_target,
#         )
#
#         sample = krystalium.api.RefinedSample(
#             id = 0,
#             rfid_id = "",
#             primary_action = args.primary_action,
#             primary_target = args.primary_target,
#             secondary_action = args.secondary_action,
#             secondary_target = args.secondary_target,
#             purity = "",
#             purity_score = args.purity,
#         )
#
#         await unreal.update_from_samples(blood, sample)
#         await unreal.reinitialize()
#         await unreal.set_active(True)
#         await asyncio.sleep(30)
#
#     await unreal.stop()


if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type = Main.Mode, required = True)
    parser.add_argument("--launch", action = "store_true")

    parser.add_argument("--blood-strength", type = int, default = 0)
    parser.add_argument("--blood-action", default = "None")
    parser.add_argument("--blood-target", default = "None")

    parser.add_argument("--purity", type = int, default = 12)
    parser.add_argument("--primary-action", default = "") # required = True)
    parser.add_argument("--primary-target", default = "") # required = True)
    parser.add_argument("--secondary-action", default = "None")
    parser.add_argument("--secondary-target", default = "None")

    parser.add_argument("--enlisted-number", default = "") # required = )

    # parser.add_argument("--blood-action", default = "None")
    # parser.add_argument("--blood-target", default = "None")
    # parser.add_argument("--blood-strength", default = 0)
    # parser.add_argument("--primary-action", required = True)
    # parser.add_argument("--primary-target", required = True)
    # parser.add_argument("--purity", default = 12)
    # parser.add_argument("--secondary-action", default = "None")
    # parser.add_argument("--secondary-target", default = "None")
    # parser.add_argument("--test-all", action = "store_true")
    args = parser.parse_args()

    main = Main(args)
    main.run()

    # loop = asyncio.get_event_loop()
    # main_task = asyncio.ensure_future(main(args))
    # for s in signal.SIGINT, signal.SIGTERM:
    #     loop.add_signal_handler(s, main_task.cancel)
    #
    # try:
    #     loop.run_until_complete(main_task)
    # finally:
    #     loop.close()
