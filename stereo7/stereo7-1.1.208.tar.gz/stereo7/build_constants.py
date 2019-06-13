win_cmd_build = 'msbuild "@{ROOT}/../../SyndicateBase/proj.win32/SyndicateBase.sln" /p:Configuration=@{CONFIGURATION} /p:Platform=win32 /m'
android_cmd_build = 'gradle @{CONFIGURATION} -p @{ROOT}/proj.android@{APP_KIND_SUFFIX}'
android_cmd_upload_apk = 'gradle publishApkRelease -p @{ROOT}/proj.android@{APP_KIND_SUFFIX}'

ios_cmd_build = 'xcodebuild -workspace @{ROOT}/proj.ios/@{XCODEPROJECT}.xcworkspace archive -archivePath @{XCODEPROJECT}.xcarchive -scheme @{SCHEME} -allowProvisioningUpdates'
ios_cmd_export = 'xcodebuild -exportArchive -archivePath ./@{XCODEPROJECT}.xcarchive -exportPath ./ipa -exportOptionsPlist export.plist -allowProvisioningUpdates'
ios_cmd_upload_inapps = '/Applications/Xcode.app/Contents/Applications/Application\ Loader.app/Contents/itms/bin/iTMSTransporter -m upload -f @{ROOT}/store/inapps.itmsp -u @{APPLE_USER} -p @{APPLE_PASSWORD} -v detailed'

ios_export_plist = '''cat <<EOM > export.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
        <key>teamID</key>
        <string>@{APPLE_TEAM_ID}</string>
        <key>method</key>
        <string>app-store</string>
        <key>uploadSymbols</key>
        <true/>
</dict>
</plist>
EOM
'''

ios_upload_shell = '''
set -ex

# This scripts allows you to upload a binary to the iTunes Connect Store and do it for a specific app_id
# Because when you have multiple apps in status for download, xcodebuild upload will complain that multiple apps are in wait status

# Requires application loader to be installed
# See https://developer.apple.com/library/ios/documentation/LanguagesUtilities/Conceptual/iTunesConnect_Guide/Chapters/SubmittingTheApp.html


IPA_FILE="ipa/@{SCHEME}.ipa"
IPA_FILENAME=$(basename $IPA_FILE)
MD5=$(md5 -q $IPA_FILE)
BYTESIZE=$(stat -f "%z" $IPA_FILE)

TEMPDIR=itsmp
# Remove previous temp
test -d ${TEMPDIR} && rm -rf ${TEMPDIR}
mkdir ${TEMPDIR}
mkdir ${TEMPDIR}/mybundle.itmsp
cp $IPA_FILE ${TEMPDIR}/mybundle.itmsp/$IPA_FILENAME

cat <<EOM > ${TEMPDIR}/mybundle.itmsp/metadata.xml
<?xml version="1.0" encoding="UTF-8"?>
<package version="software4.7" xmlns="http://apple.com/itunes/importer">
<software_assets apple_id="@{APPLE_APP_ID}">
<asset type="bundle">
<data_file>
<file_name>$IPA_FILENAME</file_name>
<checksum type="md5">$MD5</checksum>
<size>$BYTESIZE</size>
</data_file>
</asset>
</software_assets>
</package>
EOM

cp ${IPA_FILE} $TEMPDIR/mybundle.itsmp

USER=@{APPLE_USER}
PASS=@{APPLE_PASSWORD}
/Applications/Xcode.app/Contents/Applications/Application\ Loader.app/Contents/itms/bin/iTMSTransporter -m upload -f ${TEMPDIR} -u "$USER" -p "$PASS" -v detailed
'''
