"""This module implements the Python bindings for the libg722.
It allows usage of the library through Python function calls.

Author: Noor Muhammad Malik
Date: January 11, 2022
"""
from typing import *
import ctypes
import os

g722_lib_path_prefix = 'swagger_server/controllers/common/codecs/g722'

if os.name == 'posix':
    g722_lib_path = g722_lib_path_prefix + "/libg722.so"
else:
    raise RuntimeError("Unknown OS")

class G722Coder:
    # 10 byte chunks to be processed at a time
    BUFFER_SIZE = 10
    def __init__(
        self,
        f_g722DecoderNew: Callable[[int, int], Any],
        f_g722Decode: Callable[[Any, Any, int, Any], None],
        input_size: int,
        output_size: int
    ) -> None:

        print("Going to create a decoder object")
        # use the initializer to get a new decoder
        self.decoder = f_g722DecoderNew(64000, 1)
        print("Created decoder object successfully.")
        if self.decoder == None:
            raise RuntimeError("G722 decoder function " + 
            f_g722DecoderNew.__name__ + " returned error!")
        
        # save the reference to the decode function
        self._f_g722Decode = f_g722Decode

        # save the input size
        self.input_size = input_size

        # save the output size
        self.output_size = output_size

    def decode(self, input: bytearray) -> bytearray:
        if len(input) != self.input_size:
            raise RuntimeError("Incorrect input size.")

        input_data = (ctypes.c_byte * len(input))(*input)
        input_data_size = ctypes.sizeof(input_data)
        output_data = (ctypes.c_byte * self.output_size)()
        print("type castings all done!")
        # call the library function to decode
        self._f_g722Decode(self.decoder,
            input_data, input_data_size,
            output_data)
        print("decoder running finished!")

        return bytearray(output_data)

class G722Decoder(G722Coder):
    def __init__(self) -> None:
        # load the library
        g722_lib = ctypes.CDLL(g722_lib_path)
        # initialize the decoder
        super().__init__(
            g722_lib.g722_decoder_new,
            g722_lib.g722_decode,
            self.BUFFER_SIZE,
            self.BUFFER_SIZE * 2
        )
        print("G722 Decoder constructor finished!")

# if runs as a script
if __name__ == '__main__':
    import sys
    if len(sys.argv) != 4 or (sys.argv[1] != 'encode' and sys.argv[1] != 'decode'):
        print('Usage: ./' + sys.argv[0] + ' encode/decode in_file out_file')
        exit(0)
    decoder = G722Decoder() if sys.argv[1] == 'decode' else None

    with open(sys.argv[2], 'rb') as infile, open(sys.argv[3], 'wb') as outfile:
        while True:
            buff = infile.read(decoder.input_size)
            if len(buff) < decoder.input_size:
                break
            outfile.write(decoder.decode(bytearray(buff)))

print('Done.')
