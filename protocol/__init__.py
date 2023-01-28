from enum import IntEnum, Enum
from typing import NamedTuple, Optional


class DeviceId(IntEnum):
    F2 = 116
    UNIVERSAL = 6


class ManufacturerId(IntEnum):
    UNIVERSAL = 126
    ZOOM = 82


DEVICE_FINGERPRINT = bytes([ManufacturerId.ZOOM.value, DeviceId.F2.value, 0, 1, 0])


class BatteryType(IntEnum):
    ALKALINE = 0
    NIMH = 1
    LITHIUM = 2


class AutoPowerOff(IntEnum):
    OFF = 0
    MINUTES_5 = 1
    MINUTES_10 = 2
    MINUTES_30 = 3
    MINUTES_60 = 4


class BluetoothFunction(IntEnum):
    CONTROL = 0
    TIMECODE = 1


class MessageType(Enum):
    RESPONSE = (None, 0)
    IDENTITY = (1, 2)
    FIRMWARE_VERSION = (16, 17)
    EDIT_BUFFER_DUMP = (40, None)
    START_PC_APP = (82, None)
    STOP_PC_APP = (83, None)
    CARD_UNMOUNT = (105, None)
    PARAMETER = (70, 69)
    PARAMETER_CHANGE = (49, None)
    FORMAT_SDCARD = (102, None)
    FACTORY_RESET = (103, None)
    FORGET_TIMECODE = (104, None)
    UNMOUNT_SDCARD = (105, None)
    ENTER_JIG_MODE = (126, None)
    JIG_MESSAGE = (127, None)

    def request_id(self) -> Optional[int]:
        return self.value[0]

    def response_id(self) -> Optional[int]:
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


class Parameter(Enum):
    BLE_DEVICE_EXISTS = (0, None)
    LOWCUT = (1, 16)
    HP_VOL = (2, 17)
    REC_FORMAT = (3, 18)
    REC_FILENAME_TYPE = (4, 19)
    REC_FILENAME_AUTO = (5, None)
    REC_FILENAME_USER = (6, 21)
    DATETIME = (7, 22)
    BATTERY_TYPE = (8, 23)
    AUTO_POWEROFF = (9, 24)
    BLUETOOTH_FUNCTION = (10, 25)

    def request_id(self) -> Optional[int]:
        return self.value[0]

    def response_id(self) -> Optional[int]:
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


class ResponseType(IntEnum):
    LOWCUT = 16
    HP_VOL = 17
    REC_FORMAT = 18
    REC_FILENAME_TYPE = 19
    # FUNC_2_5 = 20  # 32
    REC_FILENAME_USER = 21
    DATETIME = 22
    BATTERY_TYPE = 23
    AUTO_POWEROFF = 24
    BLUETOOTH_FUNCTION = 25
    FORGET_TIMECODE = 29
    FORMAT_SDCARD_1_A = 26
    FORMAT_SDCARD_1_B = 27
    FORMAT_SDCARD_2 = 37
    FACTORY_RESET = 28
    CLOSE = 35
    UNMOUNT = 36


class VersionKind(IntEnum):
    BOOT = 0
    MAIN = 1


class ZoomMessage(NamedTuple):
    manufacturer: ManufacturerId
    device: DeviceId
    type: MessageType
    data: bytes


class ZoomMessageId(NamedTuple):
    manufacturer: ManufacturerId
    device: DeviceId
    type: MessageType
    prefix: bytes

    def matches(self, message: ZoomMessage):
        return message.manufacturer == self.manufacturer and \
            message.device == self.device and \
            message.type == self.type and \
            message.data.startswith(self.prefix)


def serialize(message: ZoomMessage) -> bytes:
    return bytes([
        message.manufacturer.value,
        0,
        message.device.value,
        message.type.value[0],
        *message.data
    ])


def deserialize(message: bytes) -> Optional[ZoomMessage]:
    message_type = MessageType.by_response_id(message[3])
    if message_type is None:
        return None
    return ZoomMessage(
        manufacturer=ManufacturerId(message[0]),
        device=DeviceId(message[2]),
        type=message_type,
        data=bytes(message[4:])
    )
