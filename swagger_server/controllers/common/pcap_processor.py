"""This module processes Packet Capture Files. It extracts binary data of
packets individually, which allows performing processing on the packets.


Author: Noor
Date: December 28, 2021
License: None
"""
import logging
from scapy.utils import rdpcap

# For testing the reader
from codec_processor import G711UProcessor
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

        logger.info(f"Finished reading {len(packet_list)}packets from {self.filename}")
        return packet_list

def test_function():
    p = PCAPProcessor('ulaw-only.pcap')
    packets = p.dump_all_packets()

    # write the audio data in WAV object
    with wave.open('test.wav', 'wb') as f:
        f.setframerate(8000)
        f.setnchannels(1)
        f.setsampwidth(4)
        for each_packet in packets:    
            parser = RTPParser(each_packet)
            rtp_payload, rtp_header = parser.parse()
            codec_proc = G711UProcessor(rtp_payload)
            f.writeframesraw(codec_proc.decode())

    logger.info(f"Finished writing audio for {len(packets)} packets!")

# If called as a script, run the test function
if __name__ == '__main__':
    test_function()

# Otherwise, do nothing.