import codecs


def remove_utf8_bom(file_path, is_write_clean_con=False):
    """
     检测并处理文件的Bom
    :param file_path: 文件路径
    :param is_write_clean_con: 清除Bom后的内容是否写入文件 默认不会写入
    :return:
    """
    has_bom = False
    with open(file_path, "rb+") as file:
        file_contents = file.read()
        if file_contents[:3] == codecs.BOM_UTF8:
            has_bom = True
            # 写入无bom内容到文件
            if is_write_clean_con:
                file.seek(0)
                file.truncate()
                file.write(file_contents[3:])
    return has_bom
