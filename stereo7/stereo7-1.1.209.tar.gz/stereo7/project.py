import json
import fileutils
import os


class Services:

    def __init__(self):
        self.appodeal_id = ''
        self.flurry_id = ''
        self.facebook_id = ''
        self.gsm_sender_id = ''
        self.hockeyapp_id = ''


class Project(object):

    instance = None

    def __init__(self, arg_parser, empty=False):
        super(Project, self).__init__()
        self.with_pro_version = False
        self.services = None
        self.arg_parser = arg_parser
        if not empty:
            self._parse()

    def create(self):
        data = {}
        data['name'] = ''
        data['app_package'] = ''
        data['app_name'] = ''
        data['app_bundle_name'] = ''
        data['app_version'] = ''
        data['google_spreedsheet_inapps_id'] = ''
        data['google_api_secret_path'] = ''
        data['apple_auth_user'] = ''
        data['apple_auth_password'] = ''
        data['apple_id'] = ''
        data['apple_inapps_token'] = ''
        data['apple_team_id'] = ''

        # services
        data['services'] = {}
        data['services']['ios'] = {}
        data['services']['android'] = {}
        data['services']['ios']['flurry_id'] = ''
        data['services']['ios']['appodeal_id'] = ''
        data['services']['ios']['facebook_id'] = ''
        data['services']['ios']['gsm_sender_id'] = ''
        data['services']['ios']['hockeyapp_id'] = ''
        data['services']['android']['flurry_id'] = ''
        data['services']['android']['appodeal_id'] = ''
        data['services']['android']['facebook_id'] = ''
        data['services']['android']['gsm_sender_id'] = ''
        data['services']['android']['hockeyapp_id'] = ''

        path = fileutils.root_dir + '/project.json'
        open(path, 'w').write(json.dumps(data, sort_keys=True, indent=4))
        fileutils.createDir(fileutils.root_dir + '/store')
        fileutils.createDir(fileutils.root_dir + '/store/inapps.itmsp')
        fileutils.write(fileutils.root_dir + '/store/inapps.itmsp/machine-local-data.xml', '<root/>')
        fileutils.write(fileutils.root_dir + '/store/inapps.itmsp/metadata.xml', '<root/>')
        fileutils.write(fileutils.root_dir + '/store/android_inapps.csv',
                        'Product ID,Published State,Purchase Type,Auto Translate,Locale; Title; Description,Auto Fill Prices,Price,Pricing Template ID')

    def _parse(self):
        path = fileutils.root_dir + '/project.json'
        if not os.path.isfile(path):
            print 'Cannot find project file [project.json]'
            exit(-1)
        data_file = open(path)
        data = json.load(data_file)
        self.json_data = data
        self.project_name = data['name'] if 'name' in data else None
        self.package = data['app_package']
        self.version = data['app_version']
        self.gg_secret_file = fileutils.root_dir + '/' + data['google_api_secret_path']
        self.apple_auth_user = data['apple_auth_user']
        self.apple_auth_password = data['apple_auth_password']
        self.apple_team_id = data['apple_team_id']
        self.validate = data['validator_properties'] if 'validator_properties' in data else {}
        if self.project_name is None:
            k = self.package.rfind('.')
            self.project_name = self.package[k + 1:]

        def read_services(platform, kind):
            if 'lite' in data and 'pro' in data:
                js = data[kind]['services'][platform]
                self.with_pro_version = True
                self.services[platform][kind] = Services()
                self.services[platform][kind].flurry_id = js['flurry_id']
                self.services[platform][kind].appodeal_id = js['appodeal_id']
                self.services[platform][kind].facebook_id = js['facebook_id']
                self.services[platform][kind].gsm_sender_id = js['gsm_sender_id']
                self.services[platform][kind].hockeyapp_id = js['hockeyapp_id'] if 'hockeyapp_id' in js else ''
            else:
                js = data['services'][platform]
                self.with_pro_version = False
                self.services[platform] = Services()
                self.services[platform].flurry_id = js['flurry_id']
                self.services[platform].appodeal_id = js['appodeal_id']
                self.services[platform].facebook_id = js['facebook_id']
                self.services[platform].gsm_sender_id = js['gsm_sender_id']
                self.services[platform].hockeyapp_id = js['hockeyapp_id'] if 'hockeyapp_id' in js else ''

        def read_variable(kind, parameter):
            if kind in data and parameter in data[kind]:
                return data[kind][parameter]
            return data[parameter] if parameter in data else ''

        self.services = {}
        self.services['ios'] = {}
        self.services['android'] = {}
        read_services('ios', 'lite')
        read_services('ios', 'pro')
        read_services('android', 'lite')
        read_services('android', 'pro')

        self.name = read_variable(self.arg_parser.app_kind, 'app_name')
        self.app_bundle_name = read_variable(self.arg_parser.app_kind, 'app_bundle_name')
        self.apple_id = read_variable(self.arg_parser.app_kind, 'apple_id')
        self.apple_inapps_token = read_variable(self.arg_parser.app_kind, 'apple_inapps_token')
        self.gg_inapps = read_variable(self.arg_parser.app_kind, 'google_spreedsheet_inapps_id')
        self.gg_locales = read_variable(self.arg_parser.app_kind, 'google_spreedsheet_localisation_id')

        if self.with_pro_version and self.arg_parser.app_kind != 'lite':
            self.package += '.' + self.arg_parser.app_kind

        if self.arg_parser.platform:
            self.check_custom_package(self.arg_parser.platform)

    def check_custom_package(self, platform):
        # custom properties:
        if 'services' in self.json_data and 'app_package' in self.json_data['services'][platform]:
            self.package = self.json_data['services'][platform]['app_package']
            print 'Use app package name:', self.package
