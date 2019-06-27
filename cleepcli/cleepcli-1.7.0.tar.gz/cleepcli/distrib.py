#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from .console import EndlessConsole
import logging
import time
from . import config

class Distrib():
    """
    Cleep distribution helper
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__endless_command_running = False
        self.__endless_command_return_code = 0

    def __console_callback(self, stdout, stderr):
        self.logger.info((stdout if stdout is not None else '') + (stderr if stderr is not None else ''))

    def __console_end_callback(self, return_code, killed):
        self.__endless_command_running = False
        self.__endless_comand_return_code = return_code

    def build_cleep(self):
        """
        Build cleep debian package
        """
        self.logger.info('Building Cleep package...')
        cmd = """
SENTRY_DSN=`printenv SENTRY_DSN`

if [ -z "$SENTRY_DSN" ]; then
    echo 
    echo "ERROR: sentry DSN not defined, please set an environment variable called SENTRY_DSN with valid data"
    echo
    exit 1
fi

#clean all files
clean() {
    echo `pwd`
    rm -rf build
    rm -rf debian/raspiot
    rm -rf debian/*debhelper*
    rm -rf ../raspiot_*_armhf.*
    rm -rf tmp
}

#jump in cleep root directory
cd "%s"

#clean previous build
clean

#check python version
VERSION=`head -n 1 debian/changelog | awk '{ gsub("[\(\)]","",$2); print $2 }'`
PYTHON_VERSION=`cat raspiot/__init__.py | grep $VERSION | wc -l`
if [ "$PYTHON_VERSION" -ne "1" ]
then
    echo
    echo "ERROR: python version is not the same than debian version, please update raspiot/__init__.py __version__ to $VERSION"
    echo
    exit 1
fi

#generate /etc/default/raspiot.conf
mkdir tmp
touch tmp/raspiot.conf
echo "SENTRY_DSN=$SENTRY_DSN" >> tmp/raspiot.conf

#build raspiot application
debuild -us -uc

#clean python stuff
rm -rf raspiot.egg-info
rm -rf pyraspiot.egg-info/
rm -rf tmp/

#jump in build output
cd ".."

#collect variables
DEB=`ls -A1 raspiot* | grep \.deb`
ARCHIVE=raspiot_$VERSION.zip
SHA256=raspiot_$VERSION.sha256
PREINST=cleep/scripts/preinst.sh
POSTINST=cleep/scripts/postinst.sh

#build zip archive
rm -f *.zip
rm -f *.sha256
cp -a $DEB raspiot.deb
cp -a $PREINST .
cp -a $POSTINST .
zip $ARCHIVE raspiot.deb `basename $PREINST` `basename $POSTINST`
rm -f `basename $PREINST`
rm -f `basename $POSTINST`
rm -f raspiot.deb
sha256sum $ARCHIVE > $SHA256
        """ % (config.REPO_DIR)
        self.__endless_command_running = True
        c = EndlessConsole(cmd, self.__console_callback, self.__console_end_callback)
        c.start()

        while self.__endless_command_running:
            time.sleep(0.25)

        self.logger.debug('Return code: %s' % self.__endless_command_return_code)
        if self.__endless_command_return_code!=0:
            return False

        return True

    def publish_cleep(self):
        """
        Publish cleep version on github
        """
        cmd = """
GITHUB_OWNER=tangb
GITHUB_REPO=cleep
GITHUB_ACCESS_TOKEN=`printenv GITHUB_ACCESS_TOKEN`

if [ -z "$GITHUB_ACCESS_TOKEN" ]; then
    echo 
    echo "ERROR: github access token not defined, please set an environment variable called GITHUB_ACCESS_TOKEN with a valid token"
    echo
    exit 1
fi

#generate github release data
# param1: version
# param2: description file path
github_release_data() {
    cat <<EOF
{
  "tag_name": "v$1",
  "target_commitish": "master",
  "name": "$1",
  "body": "`sed -E ':a;N;$!ba;s/\r{0,1}\n/\\\\n/g' $2`",
  "draft": false,
  "prerelease": true
}
EOF
}

#clean all files
clean() {
    echo `pwd`
    rm -rf build
    rm -rf debian/raspiot
    rm -rf debian/*debhelper*
    rm -rf ../raspiot_*_armhf.*
    rm -rf tmp
}

#jump in cleep root directory
cd "%s"

VERSION=`head -n 1 debian/changelog | awk '{ gsub("[\(\)]","",$2); print $2 }'`

#jump in build output
cd "%s/.."

#collect variables
#DEB=`ls -A1 raspiot* | grep \.deb`
CHANGES=`ls -A1 raspiot* | grep \.changes`
ARCHIVE=raspiot_$VERSION.zip
SHA256=raspiot_$VERSION.sha256
#PREINST=raspiot/scripts/preinst.sh
#POSTINST=raspiot/scripts/postinst.sh

#build zip archive
#rm -f *.zip
#rm -f *.sha256
#cp -a $DEB raspiot.deb
#cp -a $PREINST .
#cp -a $POSTINST .
#zip $ARCHIVE raspiot.deb `basename $PREINST` `basename $POSTINST`
#rm -f `basename $PREINST`
#rm -f `basename $POSTINST`
#rm -f raspiot.deb
#sha256sum $ARCHIVE > $SHA256

#get description
sed -n "/raspiot ($VERSION)/,/Checksums-Sha1:/{/raspiot ($VERSION)/b;/Checksums-Sha1:/b;p}" $CHANGES | tail -n +2 > sed.out

#display changes
echo "Files \"$ARCHIVE\" and \"$SHA256\" are ready to be uploaded in https://github.com/$GITHUB_OWNER/$GITHUB_REPO/releases with following informations:"
echo "  - tag version \"v$VERSION\""
echo "  - release title \"$VERSION\""
echo "  - description:"
cat sed.out

#upload to github
if [ -z "$NO_PUBLISH" ]; then
    echo
    echo "Uploading release to github..."
    #https://www.barrykooij.com/create-github-releases-via-command-line/
    curl --silent --output curl.out --data "$(github_release_data "$VERSION" "sed.out")" https://api.github.com/repos/$GITHUB_OWNER/$GITHUB_REPO/releases?access_token=$GITHUB_ACCESS_TOKEN
    ID=`cat curl.out | grep "\"id\":" | head -n 1 | awk '{ gsub(",","",$2); print $2 }'`
    if [ -z "$ID" ]; then
        echo 
        echo "ERROR: problem when creating gihub release. Please check curl.out file content."
        echo
        exit 1
    fi
    #https://gist.github.com/stefanbuck/ce788fee19ab6eb0b4447a85fc99f447
    echo " - Uploading archive"
    curl --output curl.out --progress-bar --data-binary @"$ARCHIVE" -H "Authorization: token $GITHUB_ACCESS_TOKEN" -H "Content-Type: application/octet-stream" "https://uploads.github.com/repos/$GITHUB_OWNER/$GITHUB_REPO/releases/$ID/assets?name=$(basename $ARCHIVE)"
    echo " - Uploading checksum"
    curl --output curl.out --progress-bar --data-binary @"$SHA256" -H "Authorization: token $GITHUB_ACCESS_TOKEN" -H "Content-Type: application/octet-stream" "https://uploads.github.com/repos/$GITHUB_OWNER/$GITHUB_REPO/releases/$ID/assets?name=$(basename $SHA256)"
    rm curl.out
    rm sed.out
    echo "Done."
fi

#clean install
cd -
clean
        """ % (config.REPO_DIR)
        self.__endless_command_running = True
        c = EndlessConsole(cmd, self.__console_callback, self.__console_end_callback)
        c.start()

        while self.__endless_command_running:
            time.sleep(0.25)

        self.logger.debug('Return code: %s' % self.__endless_command_return_code)
        if self.__endless_command_return_code!=0:
            return False

        return True

