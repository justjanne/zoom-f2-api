from enum import IntEnum, Enum
from typing import NamedTuple, Optional


class DeviceId(IntEnum):
    F2 = 116
    UNIVERSAL = 6


class ManufacturerId(IntEnum):
    UNIVERSAL = 126
    ZOOM = 82


DEVICE_FINGERPRINT = (ManufacturerId.ZOOM.value, DeviceId.F2.value, 0, 1, 0)


class MessageType(Enum):
    IDENTITY = (1, 2)
    APP_START = (82, 0)
    APP_STOP = (83, 0)
    CARD_UNMOUNT = (105, 0)
    FIRMWARE_VERSION = (16, 17)
    PARAMETER = (70, 69)

    def request_id(self):
        return self.value[0]

    def response_id(self):
        return self.value[1]

    @staticmethod
    def by_request_id(request_id: int):
        for message_type in MessageType:
            if message_type.request_id() == request_id:
                return message_type
        return None

    @staticmethod
    def by_response_id(response_id: int):
        for message_type in MessageType:
            if message_type.response_id() == response_id:
                return message_type
        return None


class Parameter(IntEnum):
    BLE_DEVICE_EXISTS = 0
    LOWCUT = 1
    HP_VOL = 2
    REC_FORMAT = 3
    REC_FILENAME_TYPE = 4
    REC_FILENAME_AUTO = 5
    REC_FILENAME_USER = 6
    DATETIME = 7
    BATTERY_TYPE = 8
    AUTO_POWEROFF = 9
    BLUETOOTH_FUNCTION = 10


class VersionKind(IntEnum):
    BOOT = 0
    MAIN = 1


class MessageId(NamedTuple):
    manufacturer: ManufacturerId
    device: DeviceId
    type: MessageType


class Message(NamedTuple):
    manufacturer: ManufacturerId
    device: DeviceId
    type: MessageType
    data: list[int]

    def id(self):
        return MessageId(self.manufacturer, self.device, self.type)


def serialize(message: Message) -> list[int]:
    return [
        message.manufacturer.value,
        0,
        message.device.value,
        message.type.value[0],
        *message.data
    ]


def deserialize(message: list[int]) -> Optional[Message]:
    message_type = MessageType.by_response_id(message[3])
    if message_type is None:
        return None
    return Message(
        manufacturer=ManufacturerId(message[0]),
        device=DeviceId(message[2]),
        type=message_type,
        data=message[4:]
    )
