# -*- coding: utf-8 -*-
import os
import logging
import traceback
import subprocess

import coloredlogs
from get_args import get_args, Arguments

LINE_FORMAT = '%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
LINE_SPLIT = '-' * 10 + ' %s ' + '-' * 10

logger = logging.getLogger('nf')
logger.propagate = False


def config_logger(logger, handler_class, level, formatter_class, format):
    handler = handler_class()
    handler.setLevel(level)
    handler.setFormatter(formatter_class(format))
    logger.addHandler(handler)


class NfAcct:

    CHAIN_IN = 'nfacct_in_by_nf'
    CHAIN_OUT = 'nfacct_out_by_nf'

    TYPE_IN = 0b0001
    TYPE_OUT = 0b0010

    def __init__(self, args: Arguments):
        self.args = args

        style_level = coloredlogs.DEFAULT_LEVEL_STYLES
        style_level['info']['color'] = 'cyan'
        style_level['warning']['color'] = 'red'
        coloredlogs.install(args.level or 'INFO', logger=logger, fmt=LINE_FORMAT, milliseconds=True)

    def create_ip_chain(self):
        _in, _out = self.is_ip_chain_created()

        cmds = []
        if not _in:
            cmds.extend([
                f'iptables -t filter -N {self.CHAIN_IN}',
                f'iptables -t filter -I INPUT -j {self.CHAIN_IN}'
            ])
        if not _out:
            cmds.extend([
                f'iptables -t filter -N {self.CHAIN_OUT}',
                f'iptables -t filter -I OUTPUT -j {self.CHAIN_OUT}'
            ])

        return cmds

    def delete_ip_chain(self):
        return [
            f'iptables -t filter -D INPUT -j {self.CHAIN_IN}',
            f'iptables -t filter -F {self.CHAIN_IN}',
            f'iptables -t filter -X {self.CHAIN_IN}',
            f'iptables -t filter -D OUTPUT -j {self.CHAIN_OUT}',
            f'iptables -t filter -F {self.CHAIN_OUT}',
            f'iptables -t filter -X {self.CHAIN_OUT}',
        ]

    def get_cmd_ouput(self, cmd, exc=False):
        try:
            return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        except subprocess.CalledProcessError:
            if exc:
                raise
            else:
                return ''

    def is_ip_chain_created(self):
        # in
        _in = False
        output = self.get_cmd_ouput(f'iptables-save | grep {self.CHAIN_IN}')
        logger.debug('get chain_in: ' + output)
        if len(output) != 0:
            _in = True

        _out = False
        output = self.get_cmd_ouput(f'iptables-save | grep {self.CHAIN_OUT}')
        logger.debug('get chain_out: ' + output)
        if len(output) != 0:
            _out = True

        return _in, _out

    def get_nfacct_list(self):
        output = self.get_cmd_ouput("nfacct list | awk '{print $10}'")

        nfaccts = []

        for line in output.split('\n'):
            line = line.strip('; ')
            if line.endswith('_in') or line.endswith('_out'):
                nfaccts.append(line)

        return nfaccts

    def add(self):
        cmds = []
        cmds.extend(self.create_ip_chain())

        name = self.args.name

        if name in self.db:
            logger.critical(f'`{name}` exists.')
            exit(-1)
            return

        if self.args['in'] and self.args['out']:
            logger.critical('--in/--out must be chosen once, otherwise lease it blank.')
            exit(-1)
            return
        nf_type = self.TYPE_OUT if self.args['out'] else self.TYPE_IN

        if self.args.proto is None and self.args.user is None:
            logger.critical('`--proto` and `--user` must supplied once at least.')
            exit(-1)
            return

        ip_args = []
        port_args = []

        if self.args.proto:
            ip_args.append(f'-p {self.args.proto}')

        srcs = self.args.src_addr or []
        for src in srcs:
            ip_args.append(f'-s {src}')
        dsts = self.args.dst_addr or []
        for dst in dsts:
            ip_args.append(f'-d {dst}')

        # -m multiport / --dport / --sport can be use once
        if self.args.proto in ('udp', 'tcp'):
            # sport
            sports = self.args.sport or []
            ms = set()
            for sport in sports:
                if ':' in sport:
                    port_args.append(f'--sport {sport}')
                else:
                    ms.add(sport)
            ms = list(ms)
            if len(ms) == 1:
                port_args.append(f'--sport {ms[0]}')
            elif len(ms) > 1:
                port_args.append(f"-m multiport --source-port {','.join(ms)}")

            # dport
            dports = self.args.dport or []
            ms = set()
            for dport in dports:
                if ':' in dport:
                    port_args.append(f'--dport {dport}')
                else:
                    ms.add(dport)
            ms = list(ms)
            if len(ms) == 1:
                port_args.append(f'--dport {ms[0]}')
            elif len(ms) > 1:
                port_args.append(f"-m multiport --destination-port {','.join(ms)}")

        if self.args.user is not None:
            ip_args.append(f'-m owner --uid-owner {self.args.user}')

        if self.args.ip_args:
            ip_args.append(self.args.ip_args)

        proto = self.args.proto
        if proto == 'icmp':
            if len(port_args) != 0:
                logger.critical('`-p icmp` cannot specify any port args')
                exit(-1)
                return

        fullname = name + ('_in' if nf_type == self.TYPE_IN else '_out')
        fullchain = self.CHAIN_IN if nf_type == self.TYPE_IN else self.CHAIN_OUT

        if len(port_args) == 0:
            port_args = ['']

        cmds.append(f'nfacct add {fullname}')
        for port_arg in port_args:
            c = f'iptables -t filter -I {fullchain} ' + ' '.join(ip_args) + ' ' + port_arg
            c += f' -m nfacct --nfacct-name {fullname}'
            cmds.append(c)

        if not self.args.noreverse:
            fullname = name + ('_in' if nf_type != self.TYPE_IN else '_out')
            cmds.append(f'nfacct add {fullname}')
            for port_arg in port_args:
                c = f'iptables -t filter -I {fullchain} ' + ' '.join(ip_args) + ' ' + port_arg
                c += f' -m nfacct --nfacct-name {fullname}'
                cmds.append(self.reverse_cmd(c))

        return cmds

    def reverse_cmd(self, cmd, maps=None):
        if maps is None:
            maps = {
                '-s': '-d',
                '-d': '-s',
                '--destination-port': '--source-port',
                '--source-port': '--destination-port',
                '--sport': '--dport',
                '--dport': '--sport',
                self.CHAIN_IN: self.CHAIN_OUT,
                self.CHAIN_OUT: self.CHAIN_IN,
            }

        args = cmd.split(' ')
        for i, arg in enumerate(args):
            if arg in maps:
                args[i] = maps[arg]

        return ' '.join(args)

    def delete(self):
        cmds = []
        name = self.args.name

        # in
        output = self.get_cmd_ouput(f'iptables-save -t filter | grep {name}_in')

        for cmd in output.split('\n'):
            if not cmd.endswith(f'{name}_in'):
                continue

            del_cmd = 'iptables ' + cmd.replace('-A', '-D')
            cmds.append(del_cmd)
        cmds.append(f'nfacct delete {name}_in')

        # out
        output = self.get_cmd_ouput(f'iptables-save -t filter | grep {name}_out')

        for cmd in output.split('\n'):
            if not cmd.endswith(f'{name}_out'):
                continue

            del_cmd = 'iptables ' + cmd.replace('-A', '-D')
            cmds.append(del_cmd)
        cmds.append(f'nfacct delete {name}_out')

        return cmds

    def list(self):
        names = self.get_nfacct_list()
        print('\n'.join(names))

    @staticmethod
    def cmd_exists(cmd):
        return subprocess.call('type ' + cmd, shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

    def check(self):
        cmds = [
            'iptables',
            'iptables-save',
            'nfacct',
            'grep'
        ]
        for cmd in cmds:
            if not self.cmd_exists(cmd):
                logger.critical(f'command `{cmd}` not exists')

    def init(self):
        return self.create_ip_chain()

    def clear(self):
        cmds = []
        for name in self.get_nfacct_list():
            cmds.append(f'nfacct delete {name}')
        cmds.extend(self.delete_ip_chain())

        return cmds

    def run(self):
        if self.args.action == 'del':
            self.args.action = 'delete'

        if self.args.action in ('add', 'delete') and self.args.name is None:
            logger.critical('name must be supplied to add or del name')
            exit(-1)

        cmds = getattr(self, self.args.action)()

        if not cmds:
            return

        if self.args.dry_run:
            print('\n'.join(cmds))
        else:
            for cmd in cmds:
                output = self.get_cmd_ouput(cmd)
                logger.debug(f'cmd: {cmd}: ' + output)


def main():
    args = get_args(os.path.join(os.path.dirname(__file__), 'get_args.yml'))

    nf = NfAcct(args)
    nf.run()


if __name__ == '__main__':
    main()
