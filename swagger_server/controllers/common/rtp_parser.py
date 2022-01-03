"""This module parses RTP packets by processing each layer from the
packets and identifying RTP packets. It also returns RTP payloads as raw bytes
that can then be processed by another CODEC system to generate audio.

Currently, supports processing of Ethernet, IP and UDP headers. Since these
are the only ones needed to fully correctly reach the RTP layer.

Author: Noor
Date: December 28, 2021
License: None"""
import struct
import socket
import binascii

raw_rtp_packet = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x45\x00" \
b"\x00\x21\xbf\x3a\x40\x00\x40\x11\x63\x74\x0a\x00\x02\x0f\x0a\x00" \
b"\x02\x0f\x6d\x26\x6d\x26\x00\x0d\x18\x3c\x54\x45\x53\x54\x00"

rtp_packet = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x45\x00" \
b"\x00\xc8\x0f\x8c\x40\x00\x40\x11\x12\x77\x0a\x00\x02\x0f\x0a\x00" \
b"\x02\x14\x6d\x26\x17\x70\x00\xb4\x18\xe8\x80\x80\x92\xdb\x00\x00" \
b"\x00\xa0\x34\x3d\xa9\x9b\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff" \
b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff" \
b"\xff\xff\xff\xff\xff\xff\x7f\xff\xff\x7f\xff\x7f\x7f\xff\xff\x7f" \
b"\x7f\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff" \
b"\xff\xff\xff\xfe\xff\xff\xfe\x7e\xfd\x7d\xfd\x7e\x75\xfc\x73\x75" \
b"\xfe\x71\x7b\x7e\x7a\xfc\xfd\xf9\xfb\xfb\xf6\xff\xf9\xf8\x7c\xfa" \
b"\xfd\x7d\xfc\xff\x7e\xfe\xfe\xfe\x7e\xfd\x7e\x7d\xfe\x7c\x7c\x7d" \
b"\x7a\x7b\x7b\x7c\x7d\x7f\xfd\xfb\xf8\xf5\xf4\xf1\xf0\xf1\xf0\xf2" \
b"\xf5\xf7\xfb\xff\x7a\x76\x71\x6e\x6d\x6b\x6b\x6b\x6b\x6c\x6e\x70" \
b"\x75\x7c\xf9\xf2\xeb\xe8\xe3\xdf\xde\xdb\xe3\xdf\xe4\x7e\xf4\x6f" \
b"\x62\x66\x5e\x5e\x5f\x60"

# CODEC conversion dictionary - These numbers are from the RFC 3551
# which lists the supported CODECs that are valid for being RTP
# payloads - See Section 6 of RFC 3551
# TODO: Complete this list to avoid index out of bound errors
codec_lookup = {
    0: "PCMU",
    4: "G723",
    8: "PCMA",
    9: "G722",
    320: "AMR",
    321: "AMR-WB",
    18: "G729",
    400: "Telephone-event",
    None: ""
}

class RTPParser():
    """
    The core of the class if the 'parse' function which processes packet
    bytes and returns the RTP header as a dict alongside the RTP payload 
    of a packet as raw bytes.
    
    TODO: add support for receiving lists of packets (buffers) and then
    return the entire RTP paylaod as one unit.
    """
    def __init__(self, packet_bytes):
        self.packet_bytes = packet_bytes

    def parse(self):
        # Parse the Ethernet Layer
        payload, is_ip = self._check_eth_data(self.packet_bytes)
        
        # only proceed with parsing if the packet is an IP packet
        if not is_ip:
            print("Not an IP Packet!")
            return None
        
        # Parse the Internet Protocol Layer
        ip_header = dict()
        payload, ip_header = self._check_ip_data(payload, ip_header)

        # only proceed with parsing if packet is a UDP packet
        if not ip_header["protocol"] == 17:
            print("Not a UDP Packet!")
            return None
        
        # Parse the User Datagram Protocol Layer
        udp_header = dict()
        payload, udp_header = self._check_udp_data(payload, udp_header)

        rtp_header = dict()
        payload, rtp_header = self._check_rtp_data(payload, rtp_header)

        return payload, rtp_header
    
    # this function processes the ethernet header from packet_bytes
    def _check_eth_data(self, data):
        # extract the ethernet header from the packet - 14 bytes long
        # it is in the form of a binary 'stucture' 
        # ! is the 'network-endianness'
        # 6s - 6-bytes char - of dest MAC
        # 6s - 6-bytes char - of src MAC
        # H  - 2-bytes unsigned short - ipv4 - 0x0800 in 2-byte protocol number field, next layer protocol
        eth_hdr = struct.unpack('!6s6sH', data[:14])

        # convert binary data to hex representation
        dest_mac = binascii.hexlify(eth_hdr[0])
        src_mac  = binascii.hexlify(eth_hdr[1])
        protocol = eth_hdr[2]

        # print the eth layer data
        print("Ethernet Header Data:")
        print("Dest MAC: {0}\tSrc MAC: {1}\tProtocol: 0x{2:04x}".format(dest_mac, src_mac, protocol))

        is_ip = False
        if protocol == 0x0800:
            is_ip = True

        # slice off the eth_header
        payload = data[14:]
        return payload, is_ip

    # this function processes the IP header - RFC791
    def _check_ip_data(self, data, ip_header):
        # header length is 20 bytes
        # H - 2 byte chunk of binary data - contains Ver, IHL, TOS fields
        # H - 2 byte total length field
        # H - 2 byte IP identifier
        ip_hdr = struct.unpack('!HHHHHH4s4s', data[:20])

        # PROCESSING FIRST 2 OCTETS
        # left 4 bits are version, so SHR by 12 bits to extract that
        ver = ip_hdr[0] >> 12
        # middle 4 bits are Internet Header Length, SHR by 8 and AND to get rightmost 4 bits
        ihl = (ip_hdr[0] >> 8) & 0x0f
        # last 8 bits are TOS, simply AND with 0xff
        tos = ip_hdr[0] & 0xff

        # PROCESSING NEXT 2 OCTETS
        # 2 bytes of packet length
        total_length = ip_hdr[1]

        # 2 bytes of IP identifier
        id = ip_hdr[2]
        # 3 bits of flags
        flags = ip_hdr[3] >> 13
        # 13 bits of frag_offset
        frag_offset = ip_hdr[3] & 0x1fff
        # 8 bits of TTL
        ttl = ip_hdr[4] >> 8
        # 8 bits of protocol number
        protocol = ip_hdr[4] & 0xff
        # 16 bits of internet checksum
        checksum = ip_hdr[5]
        # 4 bytes of src and dest ip addresses
        src_ip = socket.inet_ntoa(ip_hdr[6])
        dest_ip = socket.inet_ntoa(ip_hdr[7])

        print("\nIP Header Data:")
        print("Version: 0x{0:1x}\tIHL: 0x{1:1x}\t\tTOS: 0x{2:02x}\t\tTotal Length: 0x{3:04x}".format(ver, ihl, tos, total_length))
        print("Id: 0x{0:04x}\tFlags: {1:03b} R D M\tFrag Offset: 0x{2:04x}\tTTL: 0x{3:02x}".format(id, flags & 0b111, frag_offset, ttl))
        print("Protocol: 0x{0:02x}\tHeader Checksum: 0x{1:04x}".format(protocol, checksum))
        print("Source IP: {0}\t\tDest IP: {1}".format(src_ip, dest_ip))

        # modify the given dict() object to return the header information to the caller
        ip_header['src_ip'] = src_ip
        ip_header['dest_ip'] = dest_ip
        ip_header['protocol'] = protocol
        ip_header['total_length'] = total_length

        # strip off the ip header
        data = data[20:]
        return data, ip_header

    # this function processes the UDP header - rfc 768
    def _check_udp_data(self, data, udp_header):
        udp_hdr = struct.unpack('!HHHH',data[:8] )
        src_port = udp_hdr[0]
        dest_port = udp_hdr[1]
        length = udp_hdr[2]
        checksum = udp_hdr[3]

        print("\nUDP Header Data:")
        print("Source Port: {0:>5}\tDest Port: {1:>5}".format(src_port, dest_port))
        print("Length: {0:>10}\tChecksum: 0x{1:04x}".format(length, checksum))

        udp_header['src_port'] = src_port
        udp_header['dest_port'] = dest_port
        udp_header['length'] = length

        data = data[8:]
        print("Payload:     {0} Bytes\n{1}".format(len(data), binascii.hexlify(data)))
        
        return data, udp_header

    def _check_rtp_data(self, data, rtp_header):
        rtp_hdr = struct.unpack('!BBHII', data[:12])
        # The RTP header works as follows:

        # ===================================================
        # 1 BYTE - B (unsigned char)
        # ===================================================
        # 2 bits - version number
        # 1 bit - padding flag
        # 1 bit - extension flag
        # 4 bits - contributing source CSRC count(CC)
        # ===================================================
        print("RTP Header Data:")
        rtp_header["ver"] = rtp_hdr[0] >> 6 # SHR by 6 bits to get left 2 bits
        rtp_header["pad_flag"] = (rtp_hdr[0] >> 5) & 0b001 # extract 3rd bit from left
        rtp_header["ext_flag"] = (rtp_hdr[0] >> 4) & 0b0001   # extract 4th bit from left
        rtp_header["csrc_count"] = rtp_hdr[0] & 0b00001111 # extract right 4
        print(f'Version: {rtp_header["ver"]}, Padding: {rtp_header["pad_flag"]}, Extension: {rtp_header["ext_flag"]}, CC: {rtp_header["csrc_count"]}')
        # ===================================================
        # 1 BYTE - B (unsigned char)
        # ===================================================        
        # 1 bit - mark flag
        # 7 bits - payload type identifier (RFC 3351)
        # ===================================================
        rtp_header["mark"] = rtp_hdr[1] >> 7
        rtp_header["payload_type"] = rtp_hdr[1] & 0b01111111
        print(f'Mark: {rtp_header["mark"]}, Payload Type: {rtp_header["payload_type"]} ({codec_lookup[rtp_header["payload_type"]]})')
        # ===================================================
        # 2 BYTES - H (unsigned short)
        # ===================================================
        # 16 bits - Sequence Number
        # ===================================================
        rtp_header["seq_num"] = rtp_hdr[2]
        print(f'Sequence Number: {rtp_header["seq_num"]}')
        # ===================================================
        # 4 BYTES - I (unsigned int)
        # ===================================================
        # 32 bits - timestamp
        # ===================================================
        rtp_header["timestamp"] = rtp_hdr[3]
        print(f'Timestamp: {rtp_header["timestamp"]}')

        # ===================================================
        # 4 BYTES - I (unsigned int)
        # ===================================================
        # 32 bites - synchronization source identifier (SSRC)
        rtp_header["ssrc_id"] = rtp_hdr[4]
        print(f'SSRC Identifier: 0x{rtp_header["ssrc_id"]:x}')

        # If there is only one Contributing Source, then the
        # header length is 12 bytes.
        if rtp_header["csrc_count"] == 0:
            return data[12:], rtp_header
        # In case of multiple Contributing Sources, the RTP
        # payload returned is None.
        # TODO: add capability for handling extended header
        # size when multiple contributing sources are there
        else:
            return None, rtp_header

# test driving function
def test_class():
    rtp_parser = RTPParser(rtp_packet)

    rtp_payload, rtp_header = rtp_parser.parse()

    # print(f"RTP Payload: {rtp_payload}")
    
# test_class()