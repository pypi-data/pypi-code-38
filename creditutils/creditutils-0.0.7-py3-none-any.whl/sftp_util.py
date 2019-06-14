# -*- coding:UTF-8 -*-

import paramiko
import creditutils.file_util as file_util
import os
import stat


def sftp_connect(host, port, username, password):
    print("BEGIN SFTP CONNECT")
    result_arr = [1, ""]
    try:
        handle = paramiko.Transport((host, int(port)))
        handle.connect(username=username, password=password)
        sftp_cli = paramiko.SFTPClient.from_transport(handle)
        result_arr = [1, "CONNECT SUCCESS", sftp_cli]
    except Exception as e:
        result_arr = [-1, "CONNECT FAILED, REASON: {0}".format(e)]

    return result_arr


def sftp_upload(sftp_cli, sftp_path, local_path):
    handle_result = [1, ""]
    try:
        sftp_path = file_util.normal_unix_path(sftp_path)
        local_path = file_util.normalpath(local_path)

        if os.path.isdir(local_path):
            rs = sftp_upload_dir(sftp_cli, sftp_path, local_path)
        else:
            rs = sftp_upload_file(sftp_cli, sftp_path, local_path)

        if rs[0] == -1:
            handle_result[0] = -1
        handle_result[1] = handle_result[1] + rs[1]

    except Exception as e:
        result = [-1, "UPLOAD FAILED, REASON:{0}".format(e)]

    return handle_result


def sftp_upload_dir(sftp_cli, sftp_dir_path, local_dir_path):
    handle_result = [1, ""]

    try:
        for root, dirs, files in os.walk(local_dir_path):
            if len(files) > 0:
                for filename in files:
                    local_file_path = os.path.join(root, filename)
                    if root != local_dir_path:
                        relative_path = root[len(local_dir_path):]
                        target_sftp_dir = file_util.normal_unix_path(file_util.join_unix_path(sftp_dir_path, relative_path))
                    else:
                        target_sftp_dir = sftp_dir_path

                    rs = sftp_upload_file(sftp_cli, target_sftp_dir, local_file_path)
                    if rs[0] == -1:
                        handle_result[0] = -1
                    if handle_result[1]:
                        handle_result[1] = handle_result[1] + "\n" + rs[1]
                    else:
                        handle_result[1] = rs[1]

            break

    except Exception as e:
        handle_result = [-1, "UPLOAD FAILED, REASON:{}".format(e)]

    return handle_result


def sftp_upload_file(sftp_cli, sftp_dir_path, local_file_path):
    handle_result = [1, ""]
    try:
        sftp_dir_path = file_util.normal_unix_path(sftp_dir_path)
        try:
            sftp_cli.chdir(sftp_dir_path)
        except:
            sftp_dir_path_arr = sftp_dir_path.split(file_util.unix_sep)
            temp_path = ''

            for item in sftp_dir_path_arr:
                if item:
                    if temp_path:
                        temp_path = file_util.join_unix_path(temp_path, item)
                    else:
                        temp_path = file_util.unix_sep + item

                    try:
                        sftp_cli.chdir(temp_path)
                    except:
                        sftp_cli.mkdir(temp_path)

        filename = os.path.basename(local_file_path)
        sftp_file_path = file_util.join_unix_path(sftp_dir_path, filename)
        sftp_cli.put(local_file_path, sftp_file_path)

        handle_result = [1, "UPLOAD " + filename + " SUCCESS"]

    except Exception as e:
        handle_result = [-1, "UPLOAD FAILED, REASON: {}".format(e)]

    return handle_result


def sftp_download(sftp_cli, sftp_file_path, local_dir_path):
    handle_result = [1, ""]
    try:
        sftp_file_path = file_util.normal_unix_path(sftp_file_path)
        local_dir_path = file_util.normalpath(local_dir_path)

        # download file
        if stat.S_ISREG(sftp_cli.stat(sftp_file_path).st_mode):
            sftp_file_name = os.path.basename(sftp_file_path)
            local_dir_path = os.path.join(local_dir_path, sftp_file_name)

            local_dir = os.path.split(local_dir_path)[0]
            local_dir = file_util.normalpath(local_dir)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)

            sftp_cli.get(sftp_file_path, local_dir_path)

            handle_result = [1, "DOWNLOAD " + sftp_file_name + " SUCCESS"]

        # download dir
        else:
            for filename in sftp_cli.listdir(sftp_file_path):
                sftp_file_name = file_util.join_unix_path(sftp_file_path, filename)
                if is_dir(sftp_cli, sftp_file_name):
                    lad = os.path.join(local_dir_path, filename)
                else:
                    lad = local_dir_path

                rs = sftp_download(sftp_cli, sftp_file_name, lad)

                handle_result[1] = handle_result[1] + rs[1]
                if rs[0] == -1:
                    handle_result[0] = -1
                else:
                    if handle_result[0] != -1:
                        handle_result[0] = 1

    except Exception as e:
        handle_result = [-1, "download fail, reason:{0}".format(e)]

    return handle_result


def is_dir(sftp_cli, path):
    try:
        sftp_cli.chdir(path)
        return True
    except:
        return False


if __name__ == '__main__':
    pass
