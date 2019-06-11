import base64


def encode_ssr_file_to_b64(tobe_encode_file, output_file):
    with open(tobe_encode_file, 'rb') as fin:
        ba_en = base64.b64encode(fin.read())
        with open(output_file, 'wb') as ba_en_f:
            ba_en_f.write(ba_en)
    return 0


if __name__ == '__main__':
    encode_ssr_file_to_b64('ssr.txt', 'ssr.encode')
