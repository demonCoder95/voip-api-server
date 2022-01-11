"""This module processes Packet Capture Files. It extracts binary data of
packets individually, which allows performing processing on the packets.


Author: Noor
Date: December 28, 2021
License: None
"""
import logging
from scapy.utils import rdpcap
from math import floor

# For testing the reader
if __name__ != '__main__':
    from swagger_server.controllers.common.rtp_parser import RTPParser
else:
    from rtp_parser import RTPParser

import wave

# Create a module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler and set the formatter for it
file_handler = logging.FileHandler('logs/' + __name__ + '.log')
formatter = logging.Formatter(
    '%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

# Add the handler to the logger for this module
logger.addHandler(file_handler)

class PCAPProcessor():
    """This class provides the functionality for reading a Packet Capture
    (PCAP) file and extract Packet Records from it. Each 'packet' object
    returned can be treated as a raw binary stream which can then be parsed
    by other modules in the package like 'RTPParser'.
    """
    def __init__(self, filename):
        """This class constructor"""
        # Name of the PCAP file that is to be read
        self.filename = filename

    def dump_all_packets(self):
        """Return all packet binary data in bytes format in a list."""
        packet_list = list()

        logger.info(f"Reading packets from {self.filename}")
        packets = rdpcap(self.filename)
        for packet in packets:
            packet_list.append(bytes(packet))

        logger.info(f"Finished reading {len(packet_list)} packets from {self.filename}")
        return packet_list

def test_function():
    p = PCAPProcessor('g729a-only.pcap')
    packets = p.dump_all_packets()

    with open('g729a.data', 'wb') as f:
        total_payload = b''
        for each_packet in packets:    
            parser = RTPParser(each_packet)
            rtp_payload, rtp_header = parser.parse()
            total_payload += rtp_payload

        f.write(total_payload)
        

    logger.info(f"Finished writing audio for {len(packets)} packets!")

# If called as a script, run the test function
if __name__ == '__main__':
    test_function()

# Otherwise, do nothing.