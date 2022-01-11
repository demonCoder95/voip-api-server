"""This module implements CODEC processing capabilities for various CODECs
for VoIP audio.

Author: Noor
Date: December 28, 2021
License: None"""

# for the logging plumbing
import logging

# for audio generation
import wave

# for some math
from math import ceil

# Abstract class implementation for CODEC
import abc

if __name__ != '__main__':
    from swagger_server.controllers.common.rtp_parser import codec_lookup
    from swagger_server.controllers.common.errors import UnsupportedPayload
    from swagger_server.controllers.common.codecs.g729.g729a import G729Adecoder
else:
    from rtp_parser import codec_lookup
    from errors import UnsupportedPayload
    from codecs.g729.g729a import G729Adecoder

# Create a module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler for the logger
file_handler = logging.FileHandler('logs/' + __name__ + '.log')
formatter = logging.Formatter(
    '%(asctime)s : %(levelname)s : %(name)s : %(message)s'
)
file_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(file_handler)

# A sample G.711 encoded payload
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

# List of supported payloads by this CODEC processor. This list is
# constructed from the string values from the 'rtp_parser' module.
supported_payloads = ["PCMU", "G723", "PCMA", "G722", "G729", "AMR", "AMR-WB"]

# CODEC specification information - this is from ITU-T G.* documents
# The information is needed to construct the WAVeform audio file. The
# elements of the information are:
#   1. sampling_rate => sampling frequency in Hertz (samples/sec)
#   2. n_channels => number of channels in the audio
#   3. sample_width => size of each sample in bits
codec_spec = {
    "PCMU": {
        "sampling_rate": 8000,
        "n_channels": 1,
        "sample_width": 8
    },
    "PCMA": {
        "sampling_rate": 8000,
        "n_channels": 1,
        "sample_width": 8
    },
    "G.722": {
        "sampling_rate": 16000,
        "n_channels": 1,
        "sample_width": 14
    },
    "G.729": {
        "sampling_rate": 8000,
        "n_channels": 1,
        "sample_width": 16
    }
}

class CODECProcessor():
    """
    This class is the primary class of the module and takes an RTP payload
    and payload type as input. It then performs decoding of the payload
    and returns a generated WAV audio file.
    """
    def __init__(self, rtp_payload, payload_type, filename):
        self.payload = rtp_payload
        # convert the PT field value into str
        self.payload_type = codec_lookup[payload_type]
        self.filename = filename

        # check for payload support in the constructor
        if self.payload_type not in supported_payloads:
            raise UnsupportedPayload(
                f"{self.payload_type} is not a supported CODEC!" + 
                "\nSupported CODECs are " + 
                ",".join(supported_payloads))

    def decode_payload(self):
        """This is the primary method of this class and serves as the blanket
        method to put all pieces together."""
        # instantiate the appropriate CODEC object
        decoded_audio = None
        if self.payload_type == "PCMU":
            decoded_audio = PCMUCODEC(self.payload).decode()
        elif self.payload_type == "G723":
            decoded_audio = G723CODEC(self.payload).decode()
        elif self.payload_type == "PCMA":
            decoded_audio = PCMACODEC(self.payload).decode()
        elif self.payload_type == "G722":
            decoded_audio = G722CODEC(self.payload).decode()
        elif self.payload_type == "G729":
            decoded_audio = G729CODEC(self.payload).decode()
        elif self.payload_type == "AMR":
            decoded_audio = AMRCODEC(self.payload).decode()
        elif self.payload_type == "AMR-WB":
            decoded_audio = AMRWBCODEC(self.payload).decode()
        else:
            # a safety net to catch any anamolies
            raise UnsupportedPayload("Payload not supported!")

        # generate the WAVeform audio file from the raw audio
        self.generate_wav(decoded_audio, self.filename, self.payload_type)

    def generate_wav(self, raw_audio, filename, payload_type):
        """This method generates a WAVeform audio (.wav) file for the
        provided raw audio. The parameters are:
        raw_audio: the audio data in 'bytes' format.
        filename: the filename for the WAV file
        payload_type: the payload type in """ + ",".join(supported_payloads)
        specs = codec_spec[payload_type]

        with wave.open(filename, "wb") as f:
            f.setframerate(specs["sampling_rate"])
            f.setnchannels(specs["n_channels"])
            # Need to convert bits to bytes, with upper integer value
            # to minimize data loss.
            f.setsamplewidth(ceil(specs["sample_width"]/8.0))
            f.writeframesraw(raw_audio)        

class CODEC(metaclass=abc.ABCMeta):
    """This is the abstract class that provides the functional footprint of a
    CODEC processing class. It provides abstract methods that are to be
    implemented by each CODEC implementation that has to follow."""
    # the class has no constructor since it's an abstract class and
    # it must not be instantiated
    
    # the decoder method for the particular CODEC
    @abc.abstractmethod
    def decode(self):
        pass

    # the encoder method for the particular CODEC
    @abc.abstractmethod
    def encode(self):
        pass

class PCMUCODEC(CODEC):
    """
    This class implements the ITU-T G.711 CODEC processor. It is a wrapper
    written on top of the 3rd party module 'g711'.

    The 'decode' function returns the raw audio bytes that have been
    decoded from the ITU-T G.711 u-Law encoding.
    """
    def __init__(self, payload):
        """The class constructor."""
        self.payload = payload

    def decode(self):
        # decode the encoded u-Law bytes
        # logger.debug(f'Received {len(self.payload)} bytes of G.711 u-Law payload!')
        # decoded_bytes = g711.decode_ulaw(self.payload)
        # logger.debug(f'Decoded {len(decoded_bytes)} bytes of G.711 u-Law payload!')
        # return decoded_bytes
        pass
    
    # Written to satisfy the abstract class "CODEC". Not implemented yet.
    def encode(self):
        return None

class G723CODEC(CODEC):
    """CODEC implementation for ITU-T G.723 CODEC."""
    def __init__(self, payload):
        self.payload = payload

    def encode(self):
        pass

    def decode(self):
        pass

class PCMACODEC(CODEC):
    """
    This class implements the ITU-T G.711 CODEC processor. It is a wrapper
    written on top of the 3rd party module 'g711'.

    The 'decode' function returns the raw audio bytes that have been
    decoded from the ITU-T G.711 a-Law CODEC encoding.
    """
    def __init__(self, payload):
        self.payload = payload

    def decode(self):
        # decode the encoded a-Law bytes
        # logger.debug(f'Received {len(self.payload)} bytes of G.711 a-Law payload!')
        # decoded_bytes = g711.decode_alaw(self.payload)
        # logger.debug(f'Decoded {len(decoded_bytes)} bytes of G.711 a-Law payload!')
        # return decoded_bytes
        pass

    # Written to satisfy the abstract class "CODEC". Not implemented yet.
    def encode(self):
        return None

class G722CODEC(CODEC):
    """CODEC implementation for ITU-T G.722 CODEC."""
    def __init__(self, payload):
        self.payload = payload

    def encode(self):
        pass

    def decode(self):
        pass

class G729CODEC(CODEC):
    """CODEC implementation for ITU-T G.729a CODEC."""
    def __init__(self, payload):
        self.payload = payload

    def encode(self):
        pass

    def decode(self):
        decoder = G729Adecoder()
        return decoder.process(bytearray(self.payload))

class AMRCODEC(CODEC):
    """CODEC implementation for ITU-T G.722.1 CODEC."""
    def __init__(self, payload):
        self.payload = payload

    def encode(self):
        pass

    def decode(self):
        pass

class AMRWBCODEC(CODEC):
    """CODEC implementation for ITU-T G.722.2 CODEC."""
    def __init__(self, payload):
        self.payload = payload

    def encode(self):
        pass

    def decode(self):
        pass

def test_function():
    u_law_proc = PCMUCODEC(g711u_payload)
    res = u_law_proc.decode()
    
    # write the audio data in WAV object
    with wave.open('test.wav', 'wb') as f:
        f.setframerate(8000)
        f.setnchannels(1)
        f.setsampwidth(4)
        f.writeframes(res)


# If run as a script, run the test function
if __name__ == '__main__':
    test_function()

# Otherwise, do nothing.