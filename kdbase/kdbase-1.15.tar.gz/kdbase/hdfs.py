#!/usr/bin/env python
#-*-coding: utf-8 -*-

import os
import sys
import json
import math
import traceback
import urllib2
from pyhdfs import HdfsClient

from log import logger
import service_config as config

class Hdfs(object):
    def __init__(self, hadoop_namenode1, hadoop_namenode2, hadoop_home, timeout=20, max_tries=2, retry_delay=5):
        self.__hadoop_home = hadoop_home
        self.client = HdfsClient(
                hosts='%s:50070,%s:50070'%(hadoop_namenode1, hadoop_namenode2),
                user_name='hadoop', timeout=timeout, max_tries=max_tries, retry_delay=retry_delay)
    
    def listdir(self, hdfs_path):
        return self.client.listdir(hdfs_path)
        
    def mkdirs(self, hdfs_path): 
        return self.client.mkdirs(hdfs_path)

    def exists(self, hdfs_path):
        return self.client.exists(hdfs_path)
    
    def create_file(self, hdfs_path, data, overwrite=True):
        self.client.create(path=hdfs_path, data=data, overwrite=overwrite)
        return True
    
    def append(self, hdfs_path, data):
        self.client.append(hdfs_path, data)
        return True
        
    def get_file_checksum(self, hdfs_path):
        return self.client.get_file_checksum(hdfs_path).bytes[:-8]
        
    def delete(self, hdfs_path):
        res = False
        if self.exists(hdfs_path):
            res = self.client.delete(hdfs_path, recursive=True)
        else:
            logger().info('del target file[%s] not exists' % hdfs_path)
            return True
        return res
        
    def set_xattr(self, path, xattr_name, xattr_value, flag):
        self.client.set_xattr(path, xattr_name, xattr_value, flag)
        return True
        
    def get_xattr(self, path, xattr_name):
        return self.client.get_xattrs(path, xattr_name)
        
    def list_xattrs(self, path):
        return self.client.list_xattrs(path)
        
    def get_active_namenode(self, ):
        return self.client.get_active_namenode()
        
    def get_file_status(self, hdfs_path):
        file_status = self.client.get_file_status(hdfs_path)
        time = file_status.modificationTime
        return (hdfs_path, time)
        
    def get_content_sum(self, hdfs_path):
        '''
        return ContentSummary
        spaceQuota（int） - 磁盘空间配额
        fileCount（int） - 文件数
        quota（int） - 此目录的命名空间配额
        directoryCount（int） - 目录数
        spaceConsumed（int） - 内容占用的磁盘空间
        length（int） - 内容使用的字节数
        
        '''
        cs = self.client.get_content_summary(hdfs_path)
        content = {}
        content['spaceQuota'] = cs.spaceQuota
        content['fileCount'] = cs.fileCount
        content['quota'] = cs.quota
        content['directoryCount'] = cs.directoryCount
        content['spaceConsumed'] = cs.spaceConsumed
        content['length'] = cs.length
        
        return content
    
    def download_native(self, hdfs_path, local_path):
        cmd = '%s/bin/hadoop fs -get -f %s %s' % (
                self.__hadoop_home, hdfs_path, local_path)
        code = os.system(cmd)
        return code == 0
    
    def download_py(self, hdfs_path, local_path):
        self.client.copy_to_local(hdfs_path, local_path)
        hdfs_file_size = self.get_content_sum(hdfs_path)['length']
        local_file_size = os.path.getsize(local_path)
        logger().info('hdfs_file_size[%s] vs local_file_size[%s]', 
                hdfs_file_size, local_file_size)
        assert hdfs_file_size == local_file_size, 'file sizes different'
        return True
    
    def download(self, hdfs_path, local_path, retry_time=3):
        if not self.exists(hdfs_path):
            logger().error('hdfs_path:%s not exists' % (hdfs_path))
            return False
        file_name = hdfs_path.split('/')[-1]
        local_file_path = '%s/%s_test'%(local_path, file_name)
        logger().info('download hdfs_path[%s], local_path[%s]',
                hdfs_path, local_file_path)
        try:
            #i = 1/ 0
            return self.download_py(hdfs_path, local_file_path)
        except Exception, e:
            if retry_time == -1:
                return False
            error_msg = traceback.format_exc()
            logger().error('download faill error:%s' % (error_msg))
            res = self.download_native(hdfs_path, local_file_path)
            if res:
                logger().info('native download success')
                return True
            return self.download(hdfs_path, local_path, retry_time - 1)

    def download_dir(self, hdfs_path, local_path):
        if not self.client.exists(hdfs_path):
            logger().error('hdfs_path:%s not exists'%(hdfs_path))
            return False
        if hdfs_path[-1] == os.sep:
            hdfs_path = hdfs_path[:-1]
        if local_path[-1] == os.sep:
            local_path = local_path[:-1]
        target_dir = hdfs_path.split(os.sep)[-1]
        dir_tree = self.client.walk(hdfs_path)
        for root, dirs, files in dir_tree:
            for file in files:
                path_element = root.split(os.sep)
                append_path = target_dir
                if path_element[-1] != target_dir:
                    index = path_element.index(target_dir)
                    append_path = os.sep.join(path_element[index:])
                local_path_tmp = local_path +os.sep + append_path
                if not os.path.exists(local_path_tmp):
                    os.makedirs(local_path_tmp)
                hdfs_file_path = root + os.sep + file
                res = self.download(hdfs_file_path, local_path_tmp)
                if not res:
                    self.delete(local_path)
                    del_path = local_path + os.sep + target_dir
                    for root, dirs, files in os.walk(del_path):
                        for file in files:
                            os.remove(os.path.join(root, file))
                        for dir in dirs:
                            os.rmdir(os.path.join(root, file))
                    return False
        return True
    
    def upload(self, local_path, hdfs_path, retry_time=3):
        if not os.path.exists(local_path):                                                                                            
            logger().error('local_path:%s not exists'%(local_path))
            return False
        file_name = local_path.split('/')[-1]
        hdfs_path = '%s/%s'%(hdfs_path, file_name)
        logger().info('local_path:%s, hdfs_path:%s'%(local_path, hdfs_path))
        if not self.delete(hdfs_path):
            return False
        try:
            self.client.copy_from_local(local_path, hdfs_path)
            return True
        except Exception as e:
            if retry_time == -1:
                return False
            error_msg = traceback.format_exc()
            logger().error('uplaod faill error:%s'%(error_msg))
            return self.upload(local_path, hdfs_path, retry_time - 1)
        
    def upload_dir(self, local_path, hdfs_path):
        if not os.path.exists(local_path):
            logger().error('local_path:%s not exists'%(local_path))
            return False
        if hdfs_path[-1] == os.sep:
            hdfs_path = hdfs_path[:-1]
        if local_path[-1] == os.sep:
            local_path = local_path[:-1]
        target_dir = local_path.split(os.sep)[-1]
        dir_tree = os.walk(local_path)
        for root, dirs, files in dir_tree:
            for file in files:
                path_element = root.split(os.sep)
                append_path = target_dir
                if path_element[-1] != target_dir:
                    index = path_element.index(target_dir)
                    append_path = os.sep.join(path_element[index:])
                hdfs_path_tmp = hdfs_path +os.sep + append_path
                if not self.client.exists(hdfs_path_tmp):
                    self.client.mkdirs(hdfs_path_tmp)
                local_file_path = root + os.sep + file
                res = self.upload(local_file_path, hdfs_path_tmp)
                if not res:
                    self.delete(local_path)
                    return False
        return True
    
    def get_job_id(self, job_name):
        def filter_app(x):
            target_name = x['name']
            return target_name == job_name
        apps_url = config.GET_CONF('hadoop', 'yarn_apps_url')
        if job_name.split('-')[-1] == 'class':
            apps_url = config.GET_CONF('hadoop', 'yarn_apps_url2')
        response = urllib2.urlopen(apps_url)
        data = response.read()
        data = json.loads(data)
        if not data['apps']:
            return None
        apps = data['apps']['app']
        target_apps = filter(filter_app, apps)
        if not target_apps:
            return None
        target_apps = sorted(target_apps, key=lambda x:x['startedTime'], reverse=True)
        target_app = target_apps[0]
        job_id = 'job' + target_app['id'].split('application')[1]
        return job_id
    
    def get_job_progress(self, job_name):
        def filter_app(x):
            target_name = x['name']
            return target_name == job_name
        apps_url = config.GET_CONF('hadoop', 'yarn_apps_url')
        if job_name.split('-')[-1] == 'class':
            apps_url = config.GET_CONF('hadoop', 'yarn_apps_url2')
        response = urllib2.urlopen(apps_url)
        data = response.read()
        data = json.loads(data)
        if not data['apps']:
            return 0
        apps = data['apps']['app']
        target_apps = filter(filter_app, apps)
        progress = 0
        if target_apps:
            target_apps = sorted(target_apps, key=lambda x:x['startedTime'], reverse=True)
            target_app = target_apps[0]
            progress = int(target_app['progress'])
        logger().info('mr_job_name: %s, mr_progress:%s' % (job_name, progress))
        return progress


if __name__ == '__main__':
    #print upload_dir('./base','/tmp')
    #print upload('./log.py','/tmp')
    #print delete('/tmp/t.txt')
    #client.copy_from_local('/tmp/t.txt', '/tmp/t.txt')
    hadoop_namenode1 = config.GET_CONF('hadoop', 'hadoop_namenode1')
    hadoop_namenode2 = config.GET_CONF('hadoop', 'hadoop_namenode2') 
    hadoop_home = config.GET_CONF('hadoop', 'hadoop_home')
    hdfs = Hdfs(hadoop_namenode1, hadoop_namenode2, hadoop_home)
    print hdfs.download('/user/hwl/par.jar','./')
    #print listdir('/production/version1/auto/input')
    #print download_dir('/tmp/output/protocol','./')
    #print mkdirs('/tmp/a/s/d')
    #print upload_dir_v2('./base','/tmp')
    #print download_dir_v2('/tmp/input','./')
    #create_file('/tmp/6688.txt','tom', False)
    #res =  append('/tmp/6688.txti', 'tom\n')
    #print res
    #print get_file_checksum('/user/hwl/input/test4')
    #print get_file_status('/user/hwl/input/test4')
    #print type(res)
    #print download('/user/hwl/input/track_test', './')
    #print get_content_sum('/production/service-storage/step2/streaming_output/201581884_1_kss-upload-mapreduce_null_214367501')['length']
    #print get_content_sum('/production/service-storage/step2/streaming_output/400106787_1_kss-upload-mapreduce_null_6758929')
    #print get_job_id('element_400051160_1-class')
    #print get_xattr('/user/hwl/input/test4', 'user.atime')
    #print set_xattr('/user/hwl/input/test4', 'user.addr', 'bj', 'REPLACE')
    #print download_dir('/user/hwl/copy_data_result','/home/hadoop/hwl/model/123')
    #print get_active_namenode()


