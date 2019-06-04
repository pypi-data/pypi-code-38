# -*- coding: utf-8 -*-
import os
import shutil
from functools import wraps


def split_file(function):
    r"""
    :param function:
    :return: None
    """
    @wraps(function)
    def _split_file(*args, **kwargs):
        cursor = function(*args, **kwargs)
        split_size = kwargs['split_size']
        output_file_dir = kwargs['output_file_dir']
        sql_file_name = kwargs['sql_file_name']
        batch_size = kwargs['batch_size']
        output_file_dir = os.path.join(output_file_dir, sql_file_name.replace('.sql', ''))
        print(output_file_dir)
        try:
            shutil.rmtree(output_file_dir)
        except Exception:
            print('does not exists')
        os.makedirs(output_file_dir, exist_ok=False)
        each_file_size = 0
        file_count = 0
        output_file = os.path.join(output_file_dir, sql_file_name.replace('.sql', '') + '_%04d' % file_count + '.csv')
        fp = open(output_file, 'w', encoding='utf8')
        while True:
            if each_file_size > split_size:
                fp.close()
                each_file_size = 0
                file_count += 1
                output_file = os.path.join(output_file_dir, sql_file_name.replace('.sql', '') + '_%04d' % file_count + '.csv')
                fp = open(output_file, 'w', encoding='utf8')
            data = cursor.fetchmany(batch_size)
            if data:
                for x in data:
                    fp.write(x[0].replace('\n', '').replace('\r\n', ''))
                    fp.write('\n')
                    each_file_size += 1
            else:
                fp.close()
                break

    return _split_file

