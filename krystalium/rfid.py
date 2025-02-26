import logging

from .api import BloodSample, RefinedSample, Effect
from .component import Component


log = logging.getLogger(__name__)


def purity_to_int(purity: str) -> int:
    match purity.upper():
        case "POLLUTED": return 2
        case "TARNISHED": return 3
        case "DIRTY": return 4
        case "BLEMISHED": return 5
        case "IMPURE": return 6
        case "UNBLEMISHED": return 7
        case "LUCID": return 8
        case "STAINLESS": return 9
        case "PRISTINE": return 10
        case "IMMACULATE": return 11
        case "PERFECT": return 12
        case _: raise RuntimeError(f"Unknown purity {purity}")


class Rfid(Component):
    def __init__(self) -> None:
        super().__init__()
        self.__blood_sample: BloodSample | None = None
        self.__refined_sample: RefinedSample | None = None

    @property
    def rfid_id(self):
        return self.__rfid_id

    @property
    def blood_sample(self) -> BloodSample | None:
        return self.__blood_sample

    @property
    def refined_sample(self) -> RefinedSample | None:
        return self.__refined_sample

    def add_device(self, device) -> None:
        device.set_callback(self.__process)
        log.info(f"Added serial device {device.name}")

    def remove_device(self, device) -> None:
        device.set_callback(None)

    def __process(self, line):
        if line.startswith("tag found:"):
            self.__handle_tag(line.replace("tag found: ", ""))
        elif line.startswith("tag lost:"):
            log.debug(f"Lost tag {self.__rfid_id}")
            if self.__blood_sample and self.__blood_sample.rfid_id == self.__rfid_id:
                self.__blood_sample = None
            if self.__refined_sample and self.__refined_sample.rfid_id == self.__rfid_id:
                self.__refined_sample = None
            self.__rfid_id = ""
        elif line.startswith("traits: "):
            self.__handle_tag(line.replace("traits: ", ""))

    def __handle_tag(self, line: str):
        parts = line.split(" ")
        if len(parts) <= 2:
            return

        self.__rfid_id = parts[0]

        match parts[1]:
            case "raw":
                log.warning("Raw samples are not supported")
            case "refined":
                self.__handle_refined_sample(parts[2:])
            case "blood":
                self.__handle_blood_sample(parts[2:])
            case _:
                log.warning(f"Unrecognised sample {parts[1]} detected")

    def __handle_refined_sample(self, parts: list[str]) -> None:
        if len(parts) < 6:
            log.debug("Insufficient parts for refined sample")
            return

        self.__refined_sample = RefinedSample(
            id = -1,
            rfid_id = self.__rfid_id,
            strength = purity_to_int(parts[5]),
            primary_action = parts[0],
            primary_target = parts[1],
            secondary_action = parts[2],
            secondary_target = parts[3],
        )

        log.debug(f"Found tag with refined sample: {self.__refined_sample}")

    def __handle_blood_sample(self, parts: list[str]) -> None:
        if len(parts) < 6:
            log.debug("Insufficient parts for blood sample")
            return

        self.__blood_sample = BloodSample(
            id = -1,
            rfid_id = self.__rfid_id,
            # strength = int(parts[2]),
            strength = purity_to_int(parts[5]),
            effect = Effect(
                id = -1,
                name = "Blood Sample Effect",
                strength = -1,
                action = parts[0],
                target = parts[1],
            )
        )

        log.debug(f"Found tag with blood sample: {self.__blood_sample}")
