import sys;
# sys.path.append('..') # help python find cyton.py relative to scripts folder
# sys.path.append('.')
from signal import *
import os

# openbci
from openbci import wifi as bci
import logging

# requires python-osc
from pythonosc import osc_message_builder
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server

from threading import Thread
import argparse
# for timestapms
import time
# trying to use plugin PluginManager
# manager = PluginManager()


def printData(sample):
    print(sample.sample_number)
    print(sample.channel_data)

def sendData(sample):
    # print(sample)
    # osc.plugin_object(sample)
    # osc_sender_main(sample)
    osc_sender_main.send_message(args.address, sample.channel_data)
    # print(sample.sample_number)
    # print(sample.channel_data)


if __name__ == '__main__':
    # shield_name = 'OpenBCI-W222'
    # shield_name = 'OpenBCI-5381'
    # shield_name = None
    print ("------------ openbci-wifi osc bridge for supercollider -------------")
    parser = argparse.ArgumentParser()

    parser.add_argument('--host', type=str, default='localhost', help="Host to send OSC messages to.")
    parser.add_argument('-p', '--port', type=int, default=57120, help="Port to send OSC messages to.")
    parser.add_argument('-a', '--address', type=str, default='/obci', help="OSC address for messages sent.")
    parser.add_argument('--log', dest='log', default=False, action='store_true', help="Log program")

    args = parser.parse_args()
    for arg in vars(args):
        print(arg, getattr(args, arg))


    if args.log:
        print ("Logging Enabled: " + str(args.log))
        logging.basicConfig(filename="obci_wifi_osc_%s.log" % (time.strftime("%y%m%d_%H%M%S")), format='%(asctime)s - %(levelname)s : %(message)s', level=logging.DEBUG)
        # logging.basicConfig(filename="obci_wifi_osc.log", format='%(asctime)s - %(levelname)s : %(message)s', level=logging.DEBUG)
        logging.info('---------LOG START-------------')
        logging.info(args)
    else:
        print ("Logging Disabled.")

    # addr will be appended to args.address
    def send_main(addr='', *msg):
        print("sending:", msg)
        # osc_sender_main.send_message(args.address + addr, list(msg))
        osc_sender_main.send_message(args.address + addr, msg)

    def send_my_port(addr):
        print("semd_my_port callback, addr:", addr)
        send_main('/receivePort', osc_receiver.server_address[1])

    def start_osc_receiver():
        osc_receiver.serve_forever()

    def stop_osc_receiver():
        osc_server.running = False
        # time.sleep(0.1)
        osc_receiver.close()


    def clean(*args):
        # stop_everything('')
        try:
            obci_wifi.disconnect()
        except:
            pass
        osc_receiver.shutdown()
        print("clean!")
        # sys.exit(0)
        os._exit(0)

    for sig in (SIGINT, SIGTERM):
        signal(sig, clean)



    # setup client first
    osc_sender_main = udp_client.SimpleUDPClient(args.host, args.port)
    print("Sending OSC messages to %s:%i" % (args.host, args.port))

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/receivePort", send_my_port)
    dispatcher.map("/quit", clean)
    # dispatcher.map("/volume", print_volume_handler, "Volume")
    # dispatcher.map("/logvolume", print_compute_handler, "Log volume", math.log)

    osc_receiver = osc_server.ThreadingOSCUDPServer(('0.0.0.0', 0), dispatcher)
    print("Serving on {}".format(osc_receiver.server_address))
    # osc_receiver.serve_forever()
    receiver_thread = Thread(target = start_osc_receiver)
    receiver_thread.daemon = True # will stop on exit
    try:
        receiver_thread.start()
    except Exception as e:
        raise

    # print("am i here?")

    def process_found_shields(ip_address, name, description):
        print("In stream_data... Found WiFi Shield %s with IP Address %s" % (name, ip_address))


    # osc = StreamerOSC(ip='localhost', port = 57120, address="/obci0")
    # osc.activate();

    # obci_wifi = bci.OpenBCIWiFi(shield_name=None, log=True, high_speed=False, shield_found_cb=process_found_shields)
    # shield = bci.OpenBCIWiFi(shield_name=shield_name, log=True, high_speed=False)
    obci_wifi = bci.OpenBCIWiFi(log=True, high_speed=False)
    # shield = bci.OpenBCIWiFi(ip_address='10.45.0.113', log=True, high_speed=False)
    # print("shield.local_wifi_server:", shield.local_wifi_server)
    if obci_wifi.local_wifi_server is not None:
        print("WiFi Shield Instantiated")
        # shield.start_streaming(printData)
        obci_wifi.start_streaming(sendData)
        # try:
        obci_wifi.loop()
        # except KeyboardInterrupt:
            # print("Got ^C")
        #     stop_osc_receiver();
            # print("Closing on KeyboardInterrupt")
