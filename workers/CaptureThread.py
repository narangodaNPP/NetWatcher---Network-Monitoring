from scapy.arch.linux import get_if_raw_addr
from scapy.utils import hexdump
from scapy.sendrecv import sniff
import scapy.config
import scapy.interfaces
from threading import Thread
from util import get_filter
from scapy2dict import to_dict
from pprint import pprint
from datetime import datetime
from socket import gethostname

from util import bytes_to_string, send_capture


class CaptureThread(Thread):

    def __init__(self, destination, capture_info, snoop=False):
        super().__init__()
        print(
            f"CaptureThread: initializing thread object: destination={destination}, capture info={capture_info}"
        )
        self.interface = CaptureThread.get_interface(capture_info["ip"])
        if not self.interface:
            self.interface = capture_info["interface"]

        self.capture_filter = get_filter(
            capture_info["ip"], capture_info["protocol"], capture_info["port"]
        ).lower()
        print(f"CaptureThread: listening on interface: {self.interface}, filter: {self.capture_filter}")

        self.capture_time = capture_info["capture_time"]
        self.destination = destination
        self.snoop = snoop

    @staticmethod
    def get_interface(ip):

        route = scapy.config.conf.route.route(ip)
        if route:
            return route[0]

        else:
            if_list = scapy.interfaces.get_if_list()
            for interface in if_list:
                ip = get_if_raw_addr(interface)
                if ip and ip != "127.0.0.1":
                    return interface

        return None

    def process_packet(self, packet):

        print(f"CaptureThread: processing packet: {packet}")
        packet_dict = to_dict(packet, strict=True)
        if "Raw" in packet_dict:
            del packet_dict["Raw"]
        packet_dict["hexdump"] = hexdump(packet, dump=True)
        packet_dict_no_bytes = bytes_to_string(packet_dict)

        pprint(packet_dict_no_bytes)

        print(f"CaptureThread: sending capture: {packet_dict_no_bytes}")
        status_code = send_capture(
            gethostname(),
            self.destination,
            str(datetime.now())[:-1],
            [packet_dict_no_bytes],
            self.snoop
        )
        print(f"CaptureThread: capture sent, result={status_code}\n")

    def run(self):

        print(
            f"CaptureThread: starting capture: iface={self.interface}, filter={self.capture_filter}"
        )
        sniff(
            iface=self.interface,
            filter=self.capture_filter,
            timeout=self.capture_time,
            prn=self.process_packet,
        )

        print(f"\n\n-----> CaptureThread: completed capture")
