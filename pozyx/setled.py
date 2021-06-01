#!/usr/bin/python3
import sys
from pypozyx import (PozyxSerial, PozyxConstants, version,
                     SingleRegister, DeviceRange, POZYX_SUCCESS, POZYX_FAILURE, get_first_pozyx_serial_port)

from pypozyx.tools.version_check import perform_latest_version_check



if __name__ == "__main__":

    code = int(sys.argv[1])
    ledStatus = True if code == 1 else False

    print("set leds to ", ledStatus)

    # the easier way
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()

    pozyx = PozyxSerial(serial_port)
    while True:
        pozyx.setLed(4, ledStatus)
        pozyx.setLed(3, ledStatus)
        pozyx.setLed(2, ledStatus)
        pozyx.setLed(1, ledStatus)
