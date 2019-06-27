from __future__ import print_function

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

class PostfixSatchel(ServiceSatchel):

    name = 'postfix'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: [
                'postfix',
                'mailutils',
                'libsasl2-2',
                'ca-certificates',
                'libsasl2-modules',
                'nano',
            ],
        }

    def set_defaults(self):
        self.env.service_commands = {
            START:{
                UBUNTU: 'service postfix start',
            },
            STOP:{
                UBUNTU: 'service postfix stop',
            },
            DISABLE:{
                UBUNTU: 'chkconfig postfix off',
            },
            ENABLE:{
                UBUNTU: 'chkconfig postfix on',
            },
            RESTART:{
                UBUNTU: 'service postfix restart; sleep 5',
            },
            STATUS:{
                UBUNTU: 'service postfix status',
            },
        }
        self.env.domain = '?'
        self.env.enabled = False
        self.env.mailrc_fn = '~/.mailrc'

    @task(precursors=['packager', 'user'])
    def configure(self):
        r = self.local_renderer

        if self.env.enabled:

            # Ensure any previous mail setups are wiped clean.
            # Note, this configuration is not compatible with mailx or sendmail.
            r.sudo('if [ -e "{mailrc_fn}" ]; then rm "{mailrc_fn}"; fi')
            r.sudo('DEBIAN_FRONTEND=noninteractive apt-get -yq purge postfix mailutils mailx sendmail')

            r.sudo('debconf-set-selections <<< "postfix postfix/mailname string {domain}"')
            r.sudo('debconf-set-selections <<< "postfix postfix/main_mailer_type string \'Internet Site\'"')
            r.sudo('DEBIAN_FRONTEND=noninteractive apt-get -yq install postfix mailutils libsasl2-2 ca-certificates libsasl2-modules nano')

            remote_path = r.put(
                local_path='etc_postfix_main.cf',
                remote_path='/etc/postfix/main.cf', use_sudo=True)

            r.sudo('cat /etc/ssl/certs/Thawte_Premium_Server_CA.pem | tee -a /etc/postfix/cacert.pem')

            # Note, ensure Gmail account is using 2-step verification: https://accounts.google.com/SmsAuthConfig
            # Note, ensure Gmail account is using an app password: https://security.google.com/settings/security/apppasswords?pli=1
            remote_path = r.put(
                local_path='etc_postfix_sasl_sasl_passwd',
                remote_path='/etc/postfix/sasl/sasl_passwd', use_sudo=True)

            r.sudo('chmod 400 /etc/postfix/sasl/sasl_passwd')
            r.sudo('chown -R root:root /etc/postfix/sasl')
            r.sudo('postmap /etc/postfix/sasl/sasl_passwd')
            r.sudo('update-rc.d postfix defaults')
            r.sudo('service postfix start')
            r.sudo('/usr/sbin/postfix reload')

            # Test with:
            #echo "Test mail from postfix" | mail -s "Test Postfix" user@domain

        else:
            self.disable()
            self.stop()

PostfixSatchel()
