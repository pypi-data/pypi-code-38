# coding=utf-8
# Copyright (c) 2015 EMC Corporation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import unicode_literals

from storops.lib.common import text_var, yes_no_var
from storops.vnx.resource.cifs_share import CifsAccessControl

__author__ = 'Cedric Zhuang'


class NasCommand(object):
    @staticmethod
    def create_fs(fs_name, source_fs_name, pool_name, is_thin=False):
        cmd = ['/nas/bin/nas_fs']
        cmd += text_var('-name', fs_name)
        cmd += ['-type', 'uxfs', '-create']
        cmd.append('samesize={}'.format(source_fs_name))
        cmd.append('pool={}'.format(pool_name))
        cmd += ['storage=SINGLE', 'worm=off']
        cmd += yes_no_var('-thin', is_thin)
        cmd += ['-option', 'slice=y']
        return cmd

    @staticmethod
    def mount_fs(mover_name, fs_name, path=None):
        if path is None:
            path = '/{}'.format(fs_name)
        cmd = ['/nas/bin/server_mount', mover_name, '-option', 'ro']
        cmd += [fs_name, path]
        return cmd

    @staticmethod
    def copy_ckpt(snap_name, fs_name, connect_id, session_name=None):
        if session_name is None:
            session_name = '{}:{}'.format(fs_name, snap_name)
        cmd = ['/nas/bin/nas_copy']
        cmd += text_var('-name', session_name[0:63])
        cmd.append('-source')
        cmd += text_var('-ckpt', snap_name)
        cmd.append('-destination')
        cmd += text_var('-fs', fs_name)
        cmd += text_var('-interconnect', 'id={}'.format(connect_id))
        cmd += ['-overwrite_destination', '-full_copy']
        return cmd

    @staticmethod
    def umount(mover_name, name):
        cmd = text_var('/nas/bin/server_umount', mover_name)
        cmd += text_var('-perm', name)
        return cmd

    @staticmethod
    def mount(mover_name, name, rw='rw', path=None):
        if path is None:
            path = '/{}'.format(name)
        cmd = text_var('/nas/bin/server_mount', mover_name)
        cmd += text_var('rw', rw)
        cmd += [name, path]
        return cmd

    @staticmethod
    def delete_ckpt(ckpt_name):
        cmd = ['/nas/bin/nas_fs']
        cmd += text_var('-delete', ckpt_name)
        cmd.append('-Force')
        return cmd

    @staticmethod
    def nas_cel_list():
        return '/nas/bin/nas_cel -interconnect -l'.split()

    @staticmethod
    def get_dm_interfaces(name=None, is_vdm=True):
        cmd = ['/nas/bin/nas_server', '-i']
        if is_vdm:
            cmd.append('-vdm')

        if name is not None:
            cmd.append(name)
        else:
            cmd.append('-all')
        return cmd

    @staticmethod
    def attach_nfs_interface(if_name, vdm_name=None):
        cmd = ['/nas/bin/nas_server']
        if vdm_name is not None:
            cmd += text_var('-vdm', vdm_name)
        cmd += text_var('-attach', if_name)
        return cmd

    @staticmethod
    def detach_nfs_interface(if_name, vdm_name=None):
        cmd = ['/nas/bin/nas_server']
        if vdm_name is not None:
            cmd += text_var('-vdm', vdm_name)
        cmd += text_var('-detach', if_name)
        return cmd

    @staticmethod
    def _share_access_cmd_prefix(mover_name, share_name):
        cmd = text_var('/nas/bin/.server_config', mover_name)
        cmd.append('-v')
        cmd += text_var('sharesd', share_name)
        return cmd

    @classmethod
    def disable_cifs_share_access(cls, share_name, mover_name):
        cmd = cls._share_access_cmd_prefix(mover_name, share_name)
        cmd += ['set', 'noaccess']
        return cmd

    @classmethod
    def allow_cifs_share_access(cls, share_name, mover_name, user_name, domain,
                                access=CifsAccessControl.FULL):
        cmd = cls._share_access_cmd_prefix(mover_name, share_name)
        access_str = cls._access_str(access, domain, user_name)
        cmd += text_var('grant', access_str)
        return cmd

    @staticmethod
    def _access_str(access, domain, user_name):
        return '{}@{}={}'.format(user_name, domain, access)

    @classmethod
    def deny_cifs_share_access(cls, share_name, mover_name, user_name, domain,
                               access=CifsAccessControl.FULL):
        cmd = cls._share_access_cmd_prefix(mover_name, share_name)
        access_str = cls._access_str(access, domain, user_name)
        cmd += text_var('revoke', access_str)
        return cmd
