import sys; sys.path.append('..') # help python find cyton.py relative to scripts folder
from openbci import wifi as bci
import logging
# from openbci.plugins.streamer_osc import StreamerOSC
from yapsy.PluginManager import PluginManager

# trying to use plugin PluginManager
manager = PluginManager()


def printData(sample):
    print(sample.sample_number)
    print(sample.channel_data)

def sendData(sample):
    # print(sample)
    osc.plugin_object(sample)
    print(sample.sample_number)
    # print(sample.channel_data)


if __name__ == '__main__':
    shield_name = 'OpenBCI-E2B6'
    logging.basicConfig(filename="test.log",format='%(asctime)s - %(levelname)s : %(message)s',level=logging.DEBUG)
    logging.info('---------LOG START-------------')

    # yapsy
    plugins_paths = ["openbci/plugins"]
    # if args.plugins_path:
        # plugins_paths += args.plugins_path
    manager.setPluginPlaces(plugins_paths)
    manager.collectPlugins()

    print ("Found plugins:")
    for plugin in manager.getAllPlugins():
        print ("[ " + plugin.name + " ]")
    print("\n")

    osc = manager.getPluginByName("streamer_osc")


    osc.plugin_object.pre_activate(['localhost', 57120, "/obci0"], sample_rate=250, eeg_channels=8, aux_channels=3, imp_channels=0)
    # osc.plugin_object.ip='localhost'
    # osc.plugin_object.port=57120
    # osc.plugin_object.address="/obci0"

    print("osc.plugin_object.port", osc.plugin_object.port)

    # osc = StreamerOSC(ip='localhost', port = 57120, address="/obci0")
    # osc.activate();
    shield = bci.OpenBCIWiFi(shield_name=shield_name, log=True, high_speed=False)
    print("WiFi Shield Instantiated")
    # start streaming in a separate thread so we could always send commands in here

    # boardThread = threading.Thread(target=board.start_streaming, args=(fun, lapse))
    # boardThread.daemon = True # will stop on exit
    # try:
        # boardThread.start()
    # except:
            # raise

    # shield.start_streaming(printData)
    shield.start_streaming(sendData)

    shield.loop()
