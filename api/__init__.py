import asyncio
from typing import Callable

import mido
import mido.ports

from protocol import *


class F2Api:
    futures: dict[MessageId, Callable[[mido.Message], None]]

    def __init__(self, port_name: str):
        self.futures = {}
        self.port = mido.open_ioport(name=port_name, callback=self.__receive_message)

    def __request(self, message: Message):
        if message.id in self.futures:
            return self.futures[message.id()]
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.futures[message.id()] = lambda msg: loop.call_soon_threadsafe(future.set_result, msg)
        self.port.send(mido.Message('sysex', data=serialize(message)))
        return future

    def __request_parameter(self, param: Parameter):
        return self.__request(Message(
            ManufacturerId.ZOOM,
            DeviceId.F2,
            MessageType.PARAMETER,
            [param.value]
        ))

    def __receive_message(self, message: mido.Message):
        message = deserialize(message.data)
        if message is not None and message.id() in self.futures:
            self.futures[message.id()](message)
            del self.futures[message.id()]
        else:
            print("received unknown message: {0}".format(message))

    async def request_identity(self):
        message = await self.__request(Message(
            ManufacturerId.UNIVERSAL, DeviceId.UNIVERSAL, MessageType.IDENTITY, []
        ))
        return message.data

    async def request_version(self, kind: VersionKind):
        message = await self.__request(Message(
            ManufacturerId.ZOOM, DeviceId.F2, MessageType.FIRMWARE_VERSION, [kind.value]
        ))
        return message.data[1:]

    async def request_ble_exists(self):
        message = await self.__request_parameter(Parameter.BLE_DEVICE_EXISTS)
        return bool(message.data[1])

    async def request_lowcut(self):
        message = await self.__request_parameter(Parameter.LOWCUT)
        return bool(message.data[1])

    async def request_headphone_volume(self):
        message = await self.__request_parameter(Parameter.HP_VOL)
        return message.data[1]

    async def request_rec_format(self):
        message = await self.__request_parameter(Parameter.REC_FORMAT)
        return message.data[1]

    async def request_rec_filename_type(self):
        message = await self.__request_parameter(Parameter.REC_FILENAME_TYPE)
        return message.data[1]

    async def request_rec_filename_auto(self):
        message = await self.__request_parameter(Parameter.REC_FILENAME_AUTO)
        return bytes(message.data[1:]).decode("utf-8").rstrip('\0')

    async def request_rec_filename_user(self):
        message = await self.__request_parameter(Parameter.REC_FILENAME_USER)
        return bytes(message.data[1:]).decode("utf-8").rstrip('\0')

    async def request_datetime(self):
        message = await self.__request_parameter(Parameter.DATETIME)
        return message.data[1]

    async def request_battery_type(self):
        message = await self.__request_parameter(Parameter.BATTERY_TYPE)
        return message.data[1]

    async def request_auto_poweroff(self):
        message = await self.__request_parameter(Parameter.AUTO_POWEROFF)
        return message.data[1]

    async def request_bluetooth(self):
        message = await self.__request_parameter(Parameter.BLUETOOTH_FUNCTION)
        return message.data[1]
