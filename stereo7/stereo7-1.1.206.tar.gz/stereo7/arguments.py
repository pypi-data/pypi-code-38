

class Parser(object):
    """docstring for Parser"""

    def __init__(self, argv):
        super(Parser, self).__init__()
        self.command = 'help'
        self.args = {}
        self._parse(argv)
        self.root = self.get('-r', '--root', default='.')
        self.platform = self.get('-p', '--platform')
        self.configuration = self.get('-c', '--configuration')
        self.build_version = self.get('--build_version')
        self.scheme = self.get('--scheme', None, 'Syndicate')
        self.s = self.get('-s', None, default='128000')
        self.app_kind = self.get('--app_kind', None, default='lite')
        self.xcodeproj = self.get('--xcodeproj', None, default='Syndicate')

        if self.command == 'help':
            self.help()
            exit(0)

    def _parse(self, argv):
        if len(argv) > 1:
            self.command = argv[1]
            if self.command in ['-h', '--help']:
                self.command = 'help'
        i = 2
        while i < len(argv):
            arg = argv[i]
            if arg.startswith('-') and i + 1 < len(argv):
                value = argv[i + 1]
                self._add_arg(arg, value)
                i += 2
            else:
                self._add_arg(arg)
                i += 1

    def _add_arg(self, name, value=None):
        self.args[name] = value

    def get(self, arg, syn=None, default=None):
        if arg in self.args:
            return self.args[arg]
        if syn is not None and syn in self.args:
            return self.args[arg]
        return default if default is not None else ''

    def help(self):
        print ''
        print 'using: $ stereo7 command -r path_to_project [arguments]'
        print ''
        print '  -r (--root) path_to_project (Optional, default is current directory)'
        print ''
        print 'commands:'
        print ''
        print '  help: show help'
        print '    -h: show hiden options'
        print ''
        print '  sublime: install sublime project and build system'
        print '    no arguments'
        print ''
        print '  inapps: build inapps from google spreedsheet'
        print '    --app_kind kind:          Optional, use pro/lite versions.'
        print ''
        print '  inapps_download:            Download itms ios metadata.'
        print ''
        print '  validate: validate Resources, configs and other static'
        print '    no arguments'
        print ''
        print '  compress: remove all extra info from jpg, png images'
        print '    -s: minimal size for optimize (KB).'
        print ''
        print '  build: build and upload (upload only "release" configuration)'
        print '    -p, --platform:           platform (ios, android, windows. In future: osx, steam)'
        print '    -c, --configuration:      configuration_name (debug, release. In future: pre-release)'
        print '    --build_version:          version (Optional, number of build version)'
        print '    --scheme scheme:          Optional, use only on ios platform. (name of scheme to build. Default is "Syndicate")'
        print '    --app_kind kind:          Optional, use pro/lite versions.'
        print '    --xcodeproj path:         Optional, name of XCode project.'
        print ''
        print '  upload: use only ios and android. Uploading binaries to store'
        print '    no arguments'
        print ''
        print '  gen-android: generate AndroidStudio project'
        print '    --app_kind kind:          Optional, use pro/lite versions.'
        print ''
        print '  gen-ios: generate ios xcode project'
        print '    no arguments'
        print ''
        print '  upload_inapps: use only ios and android. Uploading inapps to store'
        print '    no arguments'
        print ''
        print '  analytics: '
        print '     an_purchases csv_file'
        print '     an_interstitial csv_file'
        print '     an_levels csv_file'
        print '     an_video csv_file'
        print '     an_gems csv_file'
        print ''
        print '  locales: download localisation from google doc. need parameter into project.json [google_spreedsheet_localisation_id]'
        print '    no arguments'
        print ''
        print '  create_locales_table: print generated table of locales'
        print '    no arguments'
        print ''
        print '  hockeyapp_upload: upload apk to hockey app'
        print '    -p, -platform              platform (Android only)'
        print ''
        if self.get('-h', None, 'n')[0] == 'y':
            print ''
            print 'No hiden options'
