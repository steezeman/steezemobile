import libioplus
import socket
from pynmeagps import NMEAReader
import geopy.distance as distance

if __name__ == '__main__':
    stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stream.connect(("192.168.50.1", 60660))
    nmr = NMEAReader(stream)
    ignition = False

    for (raw_data, parsed_data) in nmr:
        if parsed_data.msgID == "RMC":
            coords_1 = (30.2510318333, -97.763665)
            coords_2 = (parsed_data.lat, parsed_data.lon)

            distance_from_home = distance.distance(coords_1, coords_2).km
            accessory = not libioplus.getOptoCh(0, 1)

            print(f" {distance_from_home} km from home, accessory is {accessory}")
            if distance_from_home > 0.1 or accessory:
                libioplus.setRelayCh(0, 1, 1)
                print("Turning starlink on")
            else:
                libioplus.setRelayCh(0, 1, 0)
                print("Turning starlink off")

