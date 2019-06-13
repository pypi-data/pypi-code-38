# Copyright (C) 2014 Bevbot LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Config file templates for the kegberry tool."""

from string import Template

# Required variables:
#  DATA_DIR: Kegbot data directory.
#  SERVER_VENV: Kegbot-server virtualenv base directory
#  PYCORE_VENV: Pycore virtualenv base directory.
#  HOME_DIR: Kegbot user home dir.
#  USER: Kegbot user.

MARIADB_CONF = Template("""
#
# These groups are read by MariaDB server.
# Use it for options that only the server (but not clients) should see
#
# See the examples of server my.cnf files in /usr/share/mysql/
#

# this is read by the standalone daemon and embedded servers
[server]

# this is only for the mysqld standalone daemon
[mysqld]

#
# * Basic Settings
#
user		= mysql
pid-file	= /var/run/mysqld/mysqld.pid
socket		= /var/run/mysqld/mysqld.sock
port		= 3306
basedir		= /usr
datadir		= /var/lib/mysql
tmpdir		= /tmp
lc-messages-dir	= /usr/share/mysql
skip-external-locking
skip-grant-tables

# Instead of skip-networking the default is now to listen only on
# localhost which is more compatible and is not less secure.
bind-address		= 127.0.0.1

#
# * Fine Tuning
#
key_buffer_size		= 16M
max_allowed_packet	= 16M
thread_stack		= 192K
thread_cache_size       = 8
# This replaces the startup script and checks MyISAM tables if needed
# the first time they are touched
myisam_recover_options  = BACKUP
#max_connections        = 100
#table_cache            = 64
#thread_concurrency     = 10

#
# * Query Cache Configuration
#
query_cache_limit	= 1M
query_cache_size        = 16M

#
# * Logging and Replication
#
# Both location gets rotated by the cronjob.
# Be aware that this log type is a performance killer.
# As of 5.1 you can enable the log at runtime!
#general_log_file        = /var/log/mysql/mysql.log
#general_log             = 1
#
# Error log - should be very few entries.
#
log_error = /var/log/mysql/error.log
#
# Enable the slow query log to see queries with especially long duration
#slow_query_log_file	= /var/log/mysql/mariadb-slow.log
#long_query_time = 10
#log_slow_rate_limit	= 1000
#log_slow_verbosity	= query_plan
#log-queries-not-using-indexes
#
# The following can be used as easy to replay backup logs or for replication.
# note: if you are setting up a replication slave, see README.Debian about
#       other settings you may need to change.
#server-id		= 1
#log_bin			= /var/log/mysql/mysql-bin.log
expire_logs_days	= 10
max_binlog_size   = 100M
#binlog_do_db		= include_database_name
#binlog_ignore_db	= exclude_database_name

#
# * InnoDB
#
# InnoDB is enabled by default with a 10MB datafile in /var/lib/mysql/.
# Read the manual for more InnoDB related options. There are many!

#
# * Security Features
#
# Read the manual, too, if you want chroot!
# chroot = /var/lib/mysql/
#
# For generating SSL certificates you can use for example the GUI tool "tinyca".
#
# ssl-ca=/etc/mysql/cacert.pem
# ssl-cert=/etc/mysql/server-cert.pem
# ssl-key=/etc/mysql/server-key.pem
#
# Accept only connections using the latest and most secure TLS protocol version.
# ..when MariaDB is compiled with OpenSSL:
# ssl-cipher=TLSv1.2
# ..when MariaDB is compiled with YaSSL (default in Debian):
# ssl=on

#
# * Character sets
#
# MySQL/MariaDB default is Latin1, but in Debian we rather default to the full
# utf8 4-byte character set. See also client.cnf
#
character-set-server  = utf8
collation-server      = utf8_general_ci

#
# * Unix socket authentication plugin is built-in since 10.0.22-6
#
# Needed so the root database user can authenticate without a password but
# only when running as the unix root user.
#
# Also available for other users if required.
# See https://mariadb.com/kb/en/unix_socket-authentication-plugin/

# this is only for embedded server
[embedded]

# This group is only read by MariaDB servers, not by MySQL.
# If you use the same .cnf file for MySQL and MariaDB,
# you can put MariaDB-only options here
[mariadb]

# This group is only read by MariaDB-10.1 servers.
# If you use the same .cnf file for MariaDB of different versions,
# use this group for options that older servers don't understand
[mariadb-10.1]
""")

NGINX_CONF = Template("""
### Kegbot nginx.conf file -- Kegberry edition.

upstream kegbot {
  server 127.0.0.1:8000;
}

server {
  listen 80;
  tcp_nopush on;
  tcp_nodelay on;

  gzip on;
  gzip_disable "msie6";
  gzip_types text/plain text/css application/x-javascript text/xml application/xml application/xml+rss text/javascript;
  gzip_vary on;

  keepalive_timeout 0;
  client_max_body_size 10m;

  location / {
    proxy_redirect      off;
    proxy_set_header    Host                    $$host;
    proxy_set_header    X-Real-IP               $$remote_addr;
    proxy_set_header    X-Forwarded-For         $$proxy_add_x_forwarded_for;
    proxy_set_header    X-Forwarded-Protocol    $$scheme;
    proxy_pass          http://kegbot;
    proxy_connect_timeout 60s;
    proxy_read_timeout 120s;

  }

  location /media/ {
    alias           $DATA_DIR/media/;
    access_log      off;
    log_not_found   off;
    expires         7d;
    add_header      pragma public;
    add_header      cache-control "public";
  }

  location /static/ {
    alias           $DATA_DIR/static/;
    access_log      off;
    log_not_found   off;
    expires         7d;
    add_header      pragma public;
    add_header      cache-control "public";
  }

  location /robots.txt {
    root            $DATA_DIR/static/;
    access_log      off;
    log_not_found   off;
  }

  location /favicon.ico {
    root            $DATA_DIR/static/;
    access_log      off;
    log_not_found   off;
  }
}
""")

SUPERVISOR_CONF = Template("""
### Supervisor.conf for Kegbot -- Kegberry edition.

[group:kegbot]
programs=gunicorn,celery,kegbot_core,kegboard_daemon

[program:gunicorn]
command=su -l $USER -c '$SERVER_VENV/bin/gunicorn pykeg.web.wsgi:application --timeout=120 -w 2'
directory=$HOME_DIR
autostart=true
autorestart=true
redirect_stderr=true
startsecs=30

[program:celery]
command=su -l $USER -c 'sleep 10; $SERVER_VENV/bin/kegbot run_workers'
directory=$HOME_DIR
autostart=true
autorestart=true
redirect_stderr=true
startsecs=40

[program:kegbot_core]
command=su -l $USER -c 'sleep 15; $PYCORE_VENV/bin/kegbot_core.py --flagfile=$HOME_DIR/.kegbot/pycore-flags.txt'
directory=$HOME_DIR
autostart=true
autorestart=true
redirect_stderr=true
startsecs=45

[program:kegboard_daemon]
command=su -l $USER -c 'sleep 20; $PYCORE_VENV/bin/kegboard_daemon.py'
directory=$HOME_DIR
autostart=true
autorestart=true
redirect_stderr=true
startsecs=50

""")

SUPERVISOR_CONF_NO_PYCORE = Template("""
### Supervisor.conf for Kegbot -- Kegberry edition.

[group:kegbot]
programs=gunicorn,celery

[program:gunicorn]
command=su -l $USER -c '$SERVER_VENV/bin/kegbot run_gunicorn --settings=pykeg.settings --timeout=120 -w 2'
directory=$HOME_DIR
autostart=true
autorestart=true
redirect_stderr=true
startsecs=30

[program:celery]
command=su -l $USER -c 'sleep 10; $SERVER_VENV/bin/kegbot run_workers'
directory=$HOME_DIR
autostart=true
autorestart=true
redirect_stderr=true
startsecs=40

""")
