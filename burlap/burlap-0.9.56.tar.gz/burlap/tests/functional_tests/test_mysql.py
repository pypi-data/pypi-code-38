from __future__ import print_function

from burlap.constants import *
from burlap.mysql import MySQLSatchel, MYSQLD_SAFE
from burlap.tests.functional_tests.base import TestCase
from burlap.system import distrib_id, distrib_release

MYSQL_ROOT_PASSWORD = 's3cr3t'

class MySQLTests(TestCase):

    def test_set_root_password_mysqld_safe(self):
        mysql = MySQLSatchel()
        try:
            mysql.verbose = True

            # https://docs.travis-ci.com/user/ci-environment/
            # Travis-CI uses Ubuntu 14.04, which has some odd default MySQL packages that we need to remove
            # before we can install the correct ones.
            # http://askubuntu.com/a/489817/13217
    #         os_ver = mysql.os_version
    #         if os_ver.distro == UBUNTU and os_ver.release == '14.04':
    #             mysql.sudo('DEBIAN_FRONTEND=noninteractive apt-get -yq purge mysql*')
    #             mysql.sudo('DEBIAN_FRONTEND=noninteractive apt-get -yq autoremove')
    #             mysql.sudo('DEBIAN_FRONTEND=noninteractive apt-get -yq autoclean')
    #             mysql.sudo('DEBIAN_FRONTEND=noninteractive apt-get -yq update')
    #             mysql.sudo('DEBIAN_FRONTEND=noninteractive apt-get -yq install mysql-client-core-5.5')

            mysql.install_packages()
            mysql.env.root_username = 'root'
            mysql.env.root_password = mysql.env.db_root_password = MYSQL_ROOT_PASSWORD
            mysql.set_root_password(method=MYSQLD_SAFE)
            ret = mysql.execute('SHOW DATABASES;', use_sudo=True)
            print('ret:', ret)
        finally:
            mysql.purge_packages()

    #TODO:reproduce "Row size too large" error and fix by enabling Barracuda
    def _test_barracuda(self):
        d_id = distrib_id()
        print('d_id:', d_id)
        d_release = distrib_release()
        print('d_release:', d_release)
        mysql = MySQLSatchel()
        mysql.install_packages()
        try:
            mysql_version = mysql.get_mysql_version()
            mysql_conf_path = mysql.conf_path
            print('mysql_version:', mysql_version)
            if d_id == UBUNTU:
                if d_release == '14.04':
                    assert mysql_version == '5.6'
                    assert mysql_conf_path == '/etc/mysql/my.cnf'
                elif d_release == '16.04':
                    assert mysql_version == '5.7'
                    assert mysql_conf_path == '/etc/mysql/mysql.conf.d/mysqld.cnf'

            # Reproduce "Row size too large" error.
            # https://bugs.mysql.com/bug.php?id=69336
            mysql.write_to_file(
                content='''
#!/bin/bash

n=$1
: ${n:=228}

cat<<GO > m2b.sql
CREATE DATABASE IF NOT EXISTS test;
use test;
set global innodb_file_format=Barracuda;
set global innodb_file_format_max=Barracuda;
set global innodb_file_per_table=1;

drop table if exists foo;
create table foo (
id int auto_increment primary key,
v varchar(32)
GO

for i in `seq 1 $n` ; do
   echo ", col$i text"
done >> m2b.sql
echo ") ENGINE=MyISAM;" >> m2b.sql

echo "alter table foo engine=innodb row_format=dynamic;" >> m2b.sql
''',
                fn='/tmp/create.sh')
            mysql.run('cd /tmp; bash /tmp/create.sh')
            mysql.sudo('cd /tmp; mysql < m2b.sql')


        finally:
            #mysql.purge_packages()
            pass
