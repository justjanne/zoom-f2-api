import asyncio

import protocol
from api import F2Api

if __name__ == "__main__":
    async def main():
        api = F2Api("F2 MIDI 1")

        identity = await api.request_identity()
        if identity != protocol.DEVICE_FINGERPRINT:
            raise Exception("Unknown device: {0}".format(identity))

        print({
            "version_bootloader": await api.request_version(protocol.VersionKind.BOOT),
            "version_firmware": await api.request_version(protocol.VersionKind.MAIN),
            "ble_exists": await api.request_ble_exists(),
            "lowcut": await api.request_lowcut(),
            "headphone_volume": await api.request_headphone_volume(),
            "rec_format": await api.request_rec_format(),
            "rec_filename_type": await api.request_rec_filename_type(),
            "rec_filename_auto": await api.request_rec_filename_auto(),
            "rec_filename_user": await api.request_rec_filename_user(),
            "datetime": await api.request_datetime(),
            "battery_type": await api.request_battery_type(),
            "auto_poweroff": await api.request_auto_poweroff(),
            "bluetooth": await api.request_bluetooth(),
        })


    asyncio.run(main())
