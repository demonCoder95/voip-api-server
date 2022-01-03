"""This module implements CODEC processing capabilities for various CODECs
for VoIP audio.

Author: Noor
Date: December 28, 2021
License: None"""
import g711
import wave

g711u_payload = b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff" \
b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff" \
b"\x7f\xff\xff\x7f\xff\x7f\x7f\xff\xff\x7f\x7f\xff\x7f\xff\xff\xff" \
b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfe\xff\xff" \
b"\xfe\x7e\xfd\x7d\xfd\x7e\x75\xfc\x73\x75\xfe\x71\x7b\x7e\x7a\xfc" \
b"\xfd\xf9\xfb\xfb\xf6\xff\xf9\xf8\x7c\xfa\xfd\x7d\xfc\xff\x7e\xfe" \
b"\xfe\xfe\x7e\xfd\x7e\x7d\xfe\x7c\x7c\x7d\x7a\x7b\x7b\x7c\x7d\x7f" \
b"\xfd\xfb\xf8\xf5\xf4\xf1\xf0\xf1\xf0\xf2\xf5\xf7\xfb\xff\x7a\x76" \
b"\x71\x6e\x6d\x6b\x6b\x6b\x6b\x6c\x6e\x70\x75\x7c\xf9\xf2\xeb\xe8" \
b"\xe3\xdf\xde\xdb\xe3\xdf\xe4\x7e\xf4\x6f\x62\x66\x5e\x5e\x5f\x60"


class G711UProcessor():
    """
    The 'decode' function returns the raw audio bytes that have been
    decoded from the ITU-T G.711 u-Law CODEC encoding.
    """
    def __init__(self, payload):
        self.payload = payload

    def decode(self):
        # decode the encoded u-Law bytes
        decoded_bytes = g711.decode_ulaw(self.payload)
        return decoded_bytes

class G711AProcessor():
    """
    The 'decode' function returns the raw audio bytes that have been
    decoded from the ITU-T G.711 a-Law CODEC encoding.
    """
    def __init__(self, payload):
        self.payload = payload

    def decode(self):
        # decode the encoded a-Law bytes
        decoded_bytes = g711.decode_alaw(self.payload)
        return decoded_bytes

def test_function():
    u_law_proc = G711UProcessor(g711u_payload)
    res = u_law_proc.decode()
    
    
    # write the audio data in WAV object
    with wave.open('test.wav', 'wb') as f:
        f.setframerate(8000)
        f.setnchannels(1)
        f.setsampwidth(1)
        f.writeframes(res)
    
    print(res)

# test_function()