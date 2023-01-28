import asyncio
import typing
from asyncio import Future
from typing import Callable, Iterable

import mido
import mido.ports

from protocol import *


class F2Api:
    futures: dict[ZoomMessageId, Callable[[ZoomMessage], typing.Any]]

    def __init__(self, port_name: str):
        self.futures = {}
        self.port = mido.open_ioport(name=port_name, callback=self.__receive_message)

    def __request(self, message_id: ZoomMessageId, message: ZoomMessage):
        if message_id in self.futures:
            return self.futures[message_id]
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.futures[message_id] = lambda msg: loop.call_soon_threadsafe(future.set_result, msg)
        self.port.send(mido.Message('sysex', data=serialize(message)))
        return future

    def __request_parameter(self, param: Parameter):
        message = ZoomMessage(ManufacturerId.ZOOM, DeviceId.F2, MessageType.PARAMETER, bytes([param.request_id()]))
        return self.__request(
            ZoomMessageId(message.manufacturer, message.device, message.type, bytes([param.request_id()])), message)

    def __receive_message(self, message: mido.Message):
        data = deserialize(message.data)
        if data is not None:
            for message_id in self.futures:
                if message_id.matches(data):
                    self.futures[message_id](data)
                    del self.futures[message_id]
                    return
        print(self.futures.keys())
        print("received unknown message: {0} {1}".format(message, data))

    async def request_identity(self):
        message = ZoomMessage(ManufacturerId.UNIVERSAL, DeviceId.UNIVERSAL, MessageType.IDENTITY, bytes([]))
        response = await self.__request(
            ZoomMessageId(message.manufacturer, message.device, message.type, bytes()),
            message
        )
        return response.data

    async def request_version(self, kind: VersionKind):
        message = ZoomMessage(ManufacturerId.ZOOM, DeviceId.F2, MessageType.FIRMWARE_VERSION, bytes([kind.value]))
        response = await self.__request(
            ZoomMessageId(message.manufacturer, message.device, message.type, bytes()),
            message
        )
        return response.data[1:]

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

    def __change_parameter(self, param: Parameter, data: Iterable[int]) -> Future[ZoomMessage]:
        message = ZoomMessage(
            ManufacturerId.ZOOM,
            DeviceId.F2,
            MessageType.PARAMETER_CHANGE,
            bytes([param.request_id(), *data])
        )
        return self.__request(
            ZoomMessageId(message.manufacturer, message.device, MessageType.RESPONSE, bytes([param.response_id()])),
            message
        )

    async def change_headphone_volume(self, volume: int) -> None:
        await self.__change_parameter(Parameter.HP_VOL, [volume, 0])

    async def change_lowcut(self, enabled: bool) -> None:
        await self.__change_parameter(Parameter.LOWCUT, [1 if enabled else 0, 0])

    async def change_rec_format(self, format: int) -> None:
        await self.__change_parameter(Parameter.REC_FORMAT, [format, 0])

    async def change_rec_filename_type(self, type: int) -> None:
        await self.__change_parameter(Parameter.REC_FILENAME_TYPE, [type, 0])

    async def change_battery_type(self, type: BatteryType) -> None:
        await self.__change_parameter(Parameter.BATTERY_TYPE, [type.value, 0])

    async def change_bluetooth_function(self, function: BluetoothFunction) -> None:
        await self.__change_parameter(Parameter.BLUETOOTH_FUNCTION, [function.value, 0])

    async def send_filename(self, name: str) -> None:
        await self.__change_parameter(Parameter.REC_FILENAME_USER, name.encode("utf-8")[0:6].ljust(50, b'\0'))
