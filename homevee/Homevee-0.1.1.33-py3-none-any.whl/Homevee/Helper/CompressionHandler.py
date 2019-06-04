#!/usr/bin/python
# -*- coding: utf-8 -*-
import zlib

class CompressionHandler:
    def __init__(self):
        return

    def compress_string(self, data: str) -> str:
        """
        Compresses the given data string
        :param data: the data string
        :return: the compresses string
        """

        data = data.encode('utf-8')

        #deflate_compress = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
        zlib_compress = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS)
        #gzip_compress = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)

        #deflate_data = deflate_compress.compress(data) + deflate_compress.flush()
        zlib_data = zlib_compress.compress(data) + zlib_compress.flush()
        #gzip_data = gzip_compress.compress(data) + gzip_compress.flush()

        return zlib_data

    def decompress_string(self, data: str) -> str:
        """
        Decompresses the given compressed data string
        :param data: the compressed data string
        :return: the decompressed string
        """
        return zlib.decompress(data).decode('utf-8')

if __name__ == "__main__":
    compress_handler = CompressionHandler()

    plain_string = "hallo, mein name ist sascha."

    print("####PLAIN####")
    print(plain_string)

    compressed_string = compress_handler.compress_string(plain_string)

    print("####COMPRESSED####")
    print(compressed_string)

    decompressed_string = compress_handler.decompress_string(compressed_string)

    print("####DECOMPRESSED####")
    print(decompressed_string)
    print(plain_string)