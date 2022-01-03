"""This module processes Packet Capture Files. It extracts binary data of
packets individually, which allows performing processing on the packets.


Author: Noor
Date: December 28, 2021
License: None
"""
from scapy.utils import rdpcap
from common.codec_processor import G711UProcessor
from common.rtp_parser import RTPParser
import wave

class PCAPProcessor():
    def __init__(self, filename):
        self.filename = filename

    def dump_all_packets(self):
        packet_list = list()
        """Return all packet binary data in bytes format in a list."""
        packets = rdpcap(self.filename)
        for packet in packets:
            packet_list.append(bytes(packet))
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

    print(f"Finished writing audio for {len(packets)} packets!")

