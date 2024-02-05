import os
import logging
from pathlib import Path

import aiofiles
import pydantic


log = logging.getLogger(__name__)


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class Config:
    device_path: str = "rfid"
    use_pipe: bool = True


class RfidController:
    def __init__(self, config: Config) -> None:
        self.__config = config

    async def start(self) -> None:
        if self.__config.use_pipe:
            path = Path() / self.__config.device_path
            os.mkfifo(path)
            self.__fd = os.open(path, os.O_RDONLY)
            log.info(f"Created FIFO at {path}")
        else:
            self.__fd = os.open(self.__config.device_path, os.O_RDONLY)

    async def stop(self) -> None:
        os.close(self.__fd)
        if self.__config.use_pipe:
            os.unlink(Path() / self.__config.device_path)

    async def detect(self) -> str | None:
        async with aiofiles.open(self.__fd, closefd = False) as f:
            line = await f.readline()

            if line.startswith("Tag found:"):
                tag_id = line.replace("Tag found: ", "").strip()
                log.debug(f"Found tag {tag_id}")
                return tag_id
            elif line.startswith("Tag lost:"):
                log.debug("Lost tag")
                return ""

            return None
