
from common.pcap_processor import PCAPProcessor

pcap_filename = '100-packet-audio.pcap'
pcap_proc = PCAPProcessor(pcap_filename)
packet_list = pcap_proc.dump_all_packets()

for each_packet in packet_list:
    print(type(each_packet))