# -*- coding: utf-8 -*-
import os
from pathlib import Path
import subprocess
import tempfile

from loguru import logger
import shutil

from cjk_commons.settings import SettingsError, get_attribute, get_path_attribute, get_settings
from diff_1c.__about__ import APP_AUTHOR, APP_NAME
from parse_1c_build import Parser


class Processor:
    def __init__(self, **kwargs):
        settings_file_path = get_path_attribute(
            kwargs, 'settings_file_path', default_path=Path('settings.yaml'), is_dir=False, check_if_exists=False)
        self.settings = get_settings(settings_file_path, app_name=APP_NAME, app_author=APP_AUTHOR)

        self.tool = get_attribute(kwargs, 'tool', self.settings, 'default_tool', 'kdiff3').lower()
        if self.tool not in self.settings['tools']:
            raise SettingsError('Tool Incorrect')

        self.tool_path = Path(self.settings['tools'][self.tool])
        if not self.tool_path.is_file():
            raise SettingsError('Tool Not Exists')

        self.exclude_file_names = get_attribute(kwargs, 'exclude_file_names', self.settings, 'exclude_file_names', [])
        self.name_format = get_attribute(kwargs, 'name_format', self.settings, 'name_format', 'tortoisegit').lower()

    def run(self, base_file_fullpath: Path, mine_file_fullpath: Path, bname: str = '', yname: str = '') -> None:
        # base
        base_is_excluded = False
        if bname:
            if self.name_format == 'tortoisegit':
                bname_file_fullpath = Path(bname.split(':')[0])
            else:
                bname_file_fullpath = Path(bname.split(':')[0])
        else:
            bname_file_fullpath = Path.cwd()
        base_source_dir_fullpath = None
        if bname_file_fullpath.name not in self.exclude_file_names:
            base_file_fullpath_suffix = base_file_fullpath.suffix
            base_temp_file, base_temp_file_fullname = tempfile.mkstemp(base_file_fullpath_suffix)
            os.close(base_temp_file)
            shutil.copyfile(str(base_file_fullpath), base_temp_file_fullname)
            base_source_dir_fullpath = Path(tempfile.mkdtemp())
            Parser().run(Path(base_temp_file_fullname), base_source_dir_fullpath)
            Path(base_temp_file_fullname).unlink()
        else:
            base_is_excluded = True

        # mine
        mine_is_excluded = False
        if yname:
            if self.name_format == 'tortoisegit':
                yname_file_fullpath = Path(yname.split(':')[0])
            else:
                yname_file_fullpath = Path(yname.split(':')[0])
        else:
            yname_file_fullpath = Path.cwd()
        mine_source_dir_fullpath = None
        if yname_file_fullpath.name not in self.exclude_file_names:
            mine_file_fullpath_suffix = mine_file_fullpath.suffix
            mine_temp_file, mine_temp_file_fullname = tempfile.mkstemp(mine_file_fullpath_suffix)
            os.close(mine_temp_file)
            shutil.copyfile(str(mine_file_fullpath), mine_temp_file_fullname)
            mine_source_dir_fullpath = Path(tempfile.mkdtemp())
            Parser().run(Path(mine_temp_file_fullname), mine_source_dir_fullpath)
            Path(mine_temp_file_fullname).unlink()
        else:
            mine_is_excluded = True

        tool_args = [str(self.tool_path)]
        if self.tool == 'kdiff3':
            # base
            if base_is_excluded:
                tool_args += ['--cs', 'EncodingForA=UTF-8', str(base_file_fullpath)]
            else:
                tool_args += ['--cs', 'EncodingForA=windows-1251', str(base_source_dir_fullpath)]
            if bname is not None:
                tool_args += ['--L1', bname]

            # mine
            if mine_is_excluded:
                tool_args += ['--cs', 'EncodingForB=UTF-8', str(mine_file_fullpath)]
            else:
                tool_args += ['--cs', 'EncodingForB=windows-1251', str(mine_source_dir_fullpath)]
            if yname is not None:
                tool_args += ['--L2', yname]
        exit_code = subprocess.check_call(tool_args)
        if not exit_code == 0:
            raise Exception('Diff files \'{0}\' and \'{1}\' failed'.format(base_file_fullpath, mine_file_fullpath))


def run(args) -> None:
    try:
        processor = Processor(name_format=args.name_format, tool=args.tool)

        base_file_fullpath = Path(args.base)
        mine_file_fullpath = Path(args.mine)
        bname = args.bname
        yname = args.yname

        processor.run(base_file_fullpath, mine_file_fullpath, bname, yname)
    except Exception as e:
        logger.exception(e)
