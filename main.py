import libioplus
import socket
from pynmeagps import NMEAReader
import geopy.distance as distance
import home

class Steezemobile:
    def __init__(self):
        self.base_charger_relay_channel = 1
        self.iso2_charger_relay_channel = 3
        self.non2_charger_relay_channel = 4
        self.compressor_relay_channel = 2
        self.inverter_relay_channel = 7
        self.battery_heater_relay_channel = 8

        self.lighting_od_channel = 1
        self.ac_compressor_od_channel = 1
        self.charger_cooling_od_channel_1 = 2
        self.charger_cooling_od_channel_2 = 3

        self.accessory_opto_channel = 5

    def Run(self):
        # Connect to the PepLink router and get position updates
        stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        stream.connect(("192.168.50.1", 60660))
        nmr = NMEAReader(stream)

        # This loop will not return unless there is a fault in the router
        for (raw_data, parsed_data) in nmr:
            if parsed_data.msgID == "RMC":
                # Home address is git ignored in home.py. Drop a tuple in that file with home address.
                # Currently, geofence is a simple circle with 1km radius around home.
                coords_1 = home.home
                coords_2 = (parsed_data.lat, parsed_data.lon)

                distance_from_home = distance.distance(coords_1, coords_2).km
                accessory = self.GetAccessoryState()

                if distance_from_home > 1.0 or accessory:
                    self.EnableInverter(True)
                else:
                    self.EnableInverter(False)

                if accessory:
                    self.EnableCharge(True, True, True)
                    self.EnableCompressor(True)
                else:
                    self.EnableCharge(False, False, False)
                    self.EnableCompressor(False)


    def EnableInverter(self, on):
        libioplus.setRelayCh(0, self.inverter_relay_channel, on)

    def EnableCompressor(self, on):
        libioplus.setRelayCh(0, self.compressor_relay_channel, on)

    def EnableCharge(self, base, iso, non):
        # Chargers ISO1 and NON1 are paired, drawing 60A from the alternator. The Tacoma can handle this load under all
        # conditions
        # Chargers ISO2 and NON2 can be toggled on and off using this function, pulling another 120A from the alternator
        # We will want ISO2 and/or NON2 to be enabled only when the truck can support them
        libioplus.setRelayCh(0, self.base_charger_relay_channel, base)
        libioplus.setRelayCh(0, self.iso2_charger_relay_channel, iso)
        libioplus.setRelayCh(0, self.non2_charger_relay_channel, non)

        # Enable the cooling fans if any chargers are on. The chargers are mounted like this:
        #  ISO1  ISO2
        #  NON2  NON1
        #   ^^    ^^
        #  FAN1  FAN2
        # The fans are on a single control circuit, so if any chargers are on, the fans should be on.
        if base or iso or non:
            libioplus.setOdPwm(0, self.charger_cooling_od_channel_1, 10000)
            libioplus.setOdPwm(0, self.charger_cooling_od_channel_2, 10000)
        else:
            libioplus.setOdPwm(0, self.charger_cooling_od_channel_1, 0)
            libioplus.setOdPwm(0, self.charger_cooling_od_channel_2, 0)

        # If we are pulling 90A or 120A from the truck, command the engine to idle higher
        # We implement this on the Tacoma as if the A/C compressor was always on
        number_of_chargers = base * 2 + iso + non
        if number_of_chargers > 2:
            libioplus.setOdPwm(0, self.ac_compressor_od_channel, 10000)
        else:
            libioplus.setOdPwm(0, self.ac_compressor_od_channel, 0)

    def GetAccessoryState(self):
        return libioplus.getOptoCh(0, self.accessory_opto_channel)

if __name__ == "__main__":
    steezemobile = Steezemobile()
    steezemobile.Run()

    print("Steezemobile exit")
