import libioplus
import socket
from pynmeagps import NMEAReader
import geopy.distance as distance
import home
from threading import Thread
import time


def EnableStarlink(on):
    libioplus.setRelayCh(0, 7, on)


def EnableCompressor(on):
    libioplus.setRelayCh(0, 1, on)
    libioplus.setRelayCh(0, 2, on)

def EnableHighPowerCharge(iso, non):
    # Disable the chargers
    libioplus.setRelayCh(0, 3, iso)
    libioplus.setRelayCh(0, 4, non)

    if iso or non:
        libioplus.setOdPwm(0, 1, 10000)
    else:
        libioplus.setOdPwm(0, 1, 0)

    if iso or non:
        libioplus.setOdPwm(0,2,10000)
        libioplus.setOdPwm(0,3,10000)
    else:
        libioplus.setOdPwm(0,2,0)
        libioplus.setOdPwm(0,3,0)


def GetAccessoryState():
    return libioplus.getOptoCh(0, 5)

def GetSwcState():
    testkey = ["",""]
    confidentkey = ["",""]
    oldkey = ["",""]

    while(1):
        swc = (libioplus.getAdcV(0, 1), libioplus.getAdcV(0, 2))

        oldkey[0] = testkey[0]

        if swc[0] < 0.03:
            testkey[0] = "MODE"
        elif swc[0] < 0.1:
            testkey[0] = "HANG UP"
        elif swc[0] < 0.3:
            testkey[0] = "ANSWER"
        elif swc[0] < 0.7:
            testkey[0] = "SIRI"
        else:
            testkey[0] = ""
            confidentkey[0] = ""

        oldkey[1] = testkey[1]

        if swc[1] < 0.03:
            testkey[1] = "UP"
        elif swc[1] < 0.1:
            testkey[1] = "DOWN"
        elif swc[1] < 0.3:
            testkey[1] = "VOL+"
        elif swc[1] < 0.7:
            testkey[1] = "VOL-"
        else:
            testkey[1] = ""
            confidentkey[1] = ""

        if oldkey[0] == testkey[0] and confidentkey[0] == "" and testkey[0] != "":
            confidentkey[0] = testkey[0]
            print(confidentkey[0])

        if oldkey[1] == testkey[1] and confidentkey[1] == "" and testkey[1] != "":
            confidentkey[1] = testkey[1]
            print(confidentkey[1])

        if confidentkey[0] != "" or confidentkey[0] != "":
            # Do some HID stuff
            pass

        time.sleep(0.01)



if __name__ == '__main__':
    thread = Thread(target=GetSwcState)
    thread.start()

    stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stream.connect(("192.168.50.1", 60660))
    nmr = NMEAReader(stream)

    # Set the engine idle high (10000) or low (0)
    libioplus.setOdPwm(0, 1, 0)

    EnableCompressor(True)

    for (raw_data, parsed_data) in nmr:
        if parsed_data.msgID == "RMC":
            coords_1 = home.home
            coords_2 = (parsed_data.lat, parsed_data.lon)

            distance_from_home = distance.distance(coords_1, coords_2).km
            accessory = GetAccessoryState()

            print(f" {distance_from_home} km from home, accessory is {accessory}")
            if distance_from_home > 1.0 or accessory:
                EnableStarlink(True)
            else:
                EnableStarlink(False)

            if accessory:
                EnableHighPowerCharge(True, False)
            else:
                EnableHighPowerCharge(False, False)



            # if alternator_current > 50:
            #     EnableHighPowerCharge(True, True)


    thread.join()
