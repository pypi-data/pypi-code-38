import png
import binascii


TEXT_CHUNK_FLAG = b'tEXt'


# 根据png chunk数据格式生成字符串的二进制数据chunk
def generate_text_chunk(str_info):
    bin_data = bytes(str_info, 'utf-8')
    data_len = len(bin_data)
    len_size = 4
    buf = bytearray(data_len.to_bytes(len_size, 'big'))
    # print(buf)
    type_flag = TEXT_CHUNK_FLAG
    buf.extend(bytes(type_flag, 'utf-8'))
    buf.extend(bin_data)
    # print(buf)
    crc_size = 4
    crc_data = binascii.crc32(buf[len_size:]).to_bytes(crc_size, 'big')
    buf.extend(crc_data)
    # print(buf)
    # print(len(buf))

    return buf


# 生成pypng 内部使用的chunk 项
def generate_chunk_tuple(type_flag, content):
    return tuple([type_flag, content])


# 生成pypng 内部使用的text chunk 项
def generate_text_chunk_tuple(str_info):
    type_flag = TEXT_CHUNK_FLAG
    return generate_chunk_tuple(type_flag, bytes(str_info, 'utf-8'))


# 获取pypng 内部读取的指定索引chunk 项
def get_chunk(src, index):
    reader = png.Reader(filename=src)
    chunks = reader.chunks()
    chunk_list = list(chunks)
    max_index = len(chunk_list) - 1
    if index > max_index or index < -(max_index+1):
        print('The index value {} out the range [{}, {}]!'.format(index, -(max_index+1), max_index))
        return None

    return chunk_list[index]


def get_text_chunk_data(src, index):
    item = get_chunk(src, index)
    if item[0] == TEXT_CHUNK_FLAG:
        data = item[1].decode()
        return data
    else:
        # print('Not the text chunk type!')
        return None


# 插入text chunk 到png文件中，默认插入到第一个chunk 后面
def insert_text_chunk(target, text, index=1):
    reader = png.Reader(filename=target)
    chunks = reader.chunks()
    chunk_list = list(chunks)
    # print(chunk_list[0])
    # print(chunk_list[1])
    # print(chunk_list[2])
    chunk_item = generate_text_chunk_tuple(text)
    chunk_list.insert(index, chunk_item)

    with open(target, 'wb') as dst_file:
        png.write_chunks(dst_file, chunk_list)


def _generate_text_chunk_test():
    generate_text_chunk('what are you doing?')


def _read_write_whole_test():
    src = r'E:\temp\png\register.png'
    dst = r'E:\temp\png\register_01.png'
    reader = png.Reader(filename=src)
    whole_data = reader.read()
    print(whole_data)
    params = whole_data[3]
    params['width'] = whole_data[0]
    params['height'] = whole_data[1]
    writer = png.Writer(**params)
    with open(dst, 'wb') as dst_file:
        writer.write(dst_file, whole_data[2])


def _read_write_chunks_test():
    src = r'E:\temp\png\register_02.png'
    dst = r'E:\temp\png\register_03.png'
    reader = png.Reader(filename=src)
    chunks = reader.chunks()
    chunk_list = list(chunks)
    print(chunk_list[0])
    print(chunk_list[1])
    print(chunk_list[2])
    chunk_item = generate_text_chunk_tuple('what are you doing?')
    chunk_list.insert(1, chunk_item)

    with open(dst, 'wb') as dst_file:
        png.write_chunks(dst_file, chunk_list)
        print('from {} generated new png file {}.'.format(src, dst))


def _insert_text_chunk_to_png_test():
    src = r'E:\temp\png\register_04.png'
    insert_text_chunk(src, 'just for test!')


def _get_text_chunk_data_test():
    src = r'E:\temp\png\register_04.png'
    data = get_text_chunk_data(src, 1)
    print(data)


def main():
    # _read_write_whole_test()
    # _generate_text_chunk_test()
    # _read_write_chunks_test()
#     _insert_text_chunk_to_png_test()
    _get_text_chunk_data_test()


if __name__ == '__main__':
    main()
