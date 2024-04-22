import libioplus
import socket
from pynmeagps import NMEAReader
import geopy.distance as distance
import home
import time

if __name__ == '__main__':
    stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stream.connect(("192.168.50.1", 60660))
    nmr = NMEAReader(stream)
    ignition = False

    # Set the engine idle high (10000) or low (0)
    libioplus.setOdPwm(0, 1, 0)

    for (raw_data, parsed_data) in nmr:
        if parsed_data.msgID == "RMC":
            coords_1 = home.home
            coords_2 = (parsed_data.lat, parsed_data.lon)

            distance_from_home = distance.distance(coords_1, coords_2).km
            # channel 5 is accessory, labeled backwards on the site
            accessory = libioplus.getOptoCh(0, 5)
            # swc1 is aux, swc2 is arrow pad
            swc1 = libioplus.getAdcV(0, 1)
            swc2 = libioplus.getAdcV(0, 2)

            print(f" {distance_from_home} km from home, accessory is {accessory}, volts swc1: {swc1} swc2: {swc2}")
            if distance_from_home > 0.1 or accessory:
                libioplus.setRelayCh(0, 7, 1)
                print("Turning starlink on")
            else:
                libioplus.setRelayCh(0, 7, 0)
                print("Turning starlink off")

            if accessory:
                # Enable the compressor
                libioplus.setRelayCh(0, 3, 1)
                libioplus.setRelayCh(0, 4, 1)

                # Make the truck idle higher
                # Todo: add behavior to make this only happen when charging at >50% of max rate
                libioplus.setOdPwm(0, 1, 10000)
            else:
                # Disable the compressor
                libioplus.setRelayCh(0, 3, 0)
                libioplus.setRelayCh(0, 4, 0)

                # Make the truck idle higher
                libioplus.setOdPwm(0, 1, 0)

