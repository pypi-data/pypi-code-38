import os.path as path

Configs = {
    "root_path": "/",  # 所有路径其实路径，相当于linux 的 '/',后面的所有目录基于这个目录推算得出的
    "data_disk": "SurfingDataDisk",  # 数据存放根节点目录名
    "ftp_data_uploads": "ftp_data_uploads",  # 数据存放根节点目录名
    "ftp_data_tmp": "ftp_data_tmp",  # ftp 数据临时处理目录
    "data_sync_backup": "data_sync_backup",  # ftp 数据处理完后打包存放目录
}


def root_path():
    return Configs.get("root_path")


def data_disk_path():
    return path.join(root_path(), Configs.get("data_disk"))


def ftp_data_uploads_path():
    return path.join(data_disk_path(), Configs.get("ftp_data_uploads"))


def ftp_data_tmp_path():
    return path.join(data_disk_path(), Configs.get("ftp_data_tmp"))


def data_sync_backup_path():
    return path.join(data_disk_path(), Configs.get("data_sync_backup"))


if __name__ == '__main__':
    pass
    print(data_disk_path())
    print(ftp_data_uploads_path())
    print(ftp_data_tmp_path())
    print(data_sync_backup_path())
