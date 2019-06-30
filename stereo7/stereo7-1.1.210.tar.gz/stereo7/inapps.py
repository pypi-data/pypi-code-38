import os
from google_sheets import GoogleSheets
import fileutils
from project import Project


consumable = 'consumable'
non_consumable = 'non-consumable'


class ID:
    en = 0
    ru = 1


class Localisation(object):
    """docstring for Localisation"""

    supported = ['en-US', 'ru']

    def __init__(self):
        super(Localisation, self).__init__()
        self.id = ''
        self.title = ''
        self.description = ''


class Inapp(object):
    """docstring for Inapp"""

    def __init__(self):
        super(Inapp, self).__init__()
        self.id = ''
        self.name = ''
        self.cost = 0
        self.tier = 0
        self.type = consumable
        self.localisations = []
        self.screenshot = None

    def calculate_cost(self):
        self.cost = min(1000, self.cost)
        table = [1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9], [10, 10], \
            [11, 11], [12, 12], [13, 13], [14, 14], [15, 15], [16, 16], [17, 17], [18, 18], [19, 19], \
            [20, 20], [21, 21], [22, 22], [23, 23], [24, 24], [25, 25], [26, 26], [27, 27], [28, 28], \
            [29, 29], [30, 30], [31, 31], [32, 32], [33, 33], [34, 34], [35, 35], [36, 36], [37, 37], \
            [38, 38], [39, 39], [40, 40], [41, 41], [42, 42], [43, 43], [44, 44], [45, 45], [46, 46], \
            [47, 47], [48, 48], [49, 49], [50, 50], [55, 51], [60, 52], [65, 53], [70, 54], [75, 55], \
            [80, 56], [85, 57], [90, 58], [95, 59], [100, 60], [110, 61], [120, 62], [125, 63], [130, 64], \
            [140, 65], [150, 66], [160, 67], [170, 68], [175, 69], [180, 70], [190, 71], [200, 72], [210, 73], \
            [220, 74], [230, 75], [240, 76], [250, 77], [300, 78], [350, 79], [400, 80], [450, 81], [500, 82], \
            [600, 83], [700, 84], [800, 85], [900, 86], [1000, 87]
        for pair in table:
            if self.cost <= pair[0]:
                self.tier = pair[1]
                return
        print 'Cannot define tier by cost [{}]'.format(self.cost)

    def validate(self):
        if not self.id:
            return False, 'id cannot by empty'
        if not self.name:
            return False, 'name cannot by empty'
        if self.cost == 0:
            return False, 'cost have to be 1+'
        if not self.localisations:
            return False, 'inapp have to have localisation'
        return True, 'Ok'


class App(object):
    """docstring for App"""

    def __init__(self, package, name, version):
        super(App, self).__init__()
        self.package = package
        self.ios_team = Project.instance.apple_team_id
        self.name = name
        self.version = version
        self.inapps = []

    def validate(self):
        result = True
        for iap in self.inapps:
            valid, msg = iap.validate()
            if not valid:
                print 'Inapp [{}] has issue: {}'.format(iap.id, msg)
                result = False

        i = 0
        while i < len(self.inapps) - 1:
            j = i + 1
            while j < len(self.inapps):
                if self.inapps[i].id == self.inapps[j].id:
                    print 'All ID\'s have to be unique. Please check inapps with id [{}]'.format(self.inapps[i].id)
                    result = False
                if self.inapps[i].name == self.inapps[j].name:
                    print 'All ID\'s have to be unique. Please check inapps with id [{}]'.format(self.inapps[i].id)
                    result = False
                j += 1
            i += 1
        return result


def get_param(name, header, row):
    if name in header:
        index = header.index(name)
        return row[index].strip()
    return None


def parse_google_doc(app, google_doc_id):
    gs = GoogleSheets(CLIENT_SECRET_FILE=Project.instance.gg_secret_file)
    gs.set_document(google_doc_id)
    raw = gs.read_range('inapps', 'A1', 'Z')
    header = raw[0]
    inapps = raw[1:]

    for row in inapps:
        iap = Inapp()
        iap.id = get_param('id', header, row)
        iap.name = get_param('Unical Name', header, row)
        iap.cost = int(get_param('Price (USA)', header, row))
        iap.type = consumable if get_param('Consumable', header, row).lower() == 'yes' else non_consumable
        iap.screenshot = get_param('image (optional)', header, row)
        if not iap.screenshot or not len(iap.screenshot):
            iap.screenshot = iap.id
        if not iap.screenshot.endswith('.png') and not iap.screenshot.endswith('.jpg'):
            iap.screenshot += '.jpg'
        for localisation in Localisation.supported:
            lang = Localisation()
            lang.title = get_param(localisation + ' (title)', header, row).encode('utf-8')
            lang.description = get_param(localisation + ' (description)', header, row).encode('utf-8')
            iap.localisations.append(lang)
        iap.calculate_cost()
        app.inapps.append(iap)


def create_itmsp(app, argparser):
    local_data = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
\t<key>adamId</key>
\t<real>{3}</real>
\t<key>addOnCount</key>
\t<real>0.0</real>
\t<key>bundleId</key>
\t<string>{0}</string>
\t<key>name</key>
\t<string>{1}</string>
\t<key>sku</key>
\t<string>{0}</string>
\t<key>type</key>
\t<string>iOS App</string>
\t<key>version</key>
\t<string>{2}</string>
</dict>
</plist>'''.format(app.package, app.name, app.version, Project.instance.apple_id)
    metadata = '''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://apple.com/itunes/importer" version="software5.2">
    <metadata_token>{2}</metadata_token>
    <provider>{0}</provider>
    <team_id>{0}</team_id>
    <software>
        <vendor_id>{1}</vendor_id>
        <software_metadata>
            <in_app_purchases>__inapps__
            </in_app_purchases>
        </software_metadata>
    </software>
</package>'''.format(app.ios_team, app.package, Project.instance.apple_inapps_token)
    pattern_inapp = '''
                <in_app_purchase>
                    <locales>
                        <locale name="en-US">
                            <title>{8}</title>
                            <description>{9}</description>
                        </locale>
                        <locale name="ru">
                            <title>{10}</title>
                            <description>{11}</description>
                        </locale>
                    </locales>
                    <review_screenshot>
                        <file_name>{4}</file_name>
                        <size>{5}</size>
                        <checksum type="md5">{6}</checksum>
                    </review_screenshot>
                    <product_id>{7}.{0}</product_id>
                    <reference_name>{1}</reference_name>
                    <type>{3}</type>
                    <products>
                        <product>
                            <cleared_for_sale>true</cleared_for_sale>
                            <intervals>
                                <interval>
                                    <start_date>2017-07-12</start_date>
                                    <wholesale_price_tier>{2}</wholesale_price_tier>
                                </interval>
                            </intervals>
                        </product>
                    </products>
                </in_app_purchase>'''
    inapps_str = ''
    # kind = '' if not Project.instance.with_pro_version else '.' + argparser.app_kind
    inapps_itmsp_folder = '%s.itmsp' % app.package
    for i in app.inapps:
        image = fileutils.root_dir + '/store/{}/{}'.format(inapps_itmsp_folder, i.screenshot)
        if not os.path.isfile(image):
            print 'Error: [{}] image [{}] not founded. Please check it'.format(i.id, image)
            exit(-1)
        image_size = fileutils.getSize(image)
        image_md5 = fileutils.getMd5File(image)
        inapps_str += pattern_inapp.format(i.id, i.name, i.tier, i.type, i.screenshot, image_size, image_md5,
                                           app.package,
                                           i.localisations[ID.en].title, i.localisations[ID.en].description,
                                           i.localisations[ID.ru].title, i.localisations[ID.ru].description,
                                           )

    metadata = metadata.replace('__inapps__', inapps_str)
    fileutils.write(fileutils.root_dir + '/store/%s/machine-local-data.xml' % inapps_itmsp_folder, local_data)
    fileutils.write(fileutils.root_dir + '/store/%s/metadata.xml' % inapps_itmsp_folder, metadata)


def download_ios_metadata(apple_app_id):
    cmd = '@{transport_home}iTMSTransporter -m lookupMetadata -u @{login} -p "@{password}" -destination @{path} \
    -apple_id @{apple_app_id}  -subitemtype InAppPurchase'

    cmd = cmd.replace('@{login}', Project.instance.apple_auth_user)
    cmd = cmd.replace('@{password}', Project.instance.apple_auth_password)
    cmd = cmd.replace('@{apple_app_id}', apple_app_id)
    cmd = cmd.replace('@{path}', fileutils.root_dir + '/store')
    cmd = cmd.replace('@{transport_home}', '/Applications/Xcode.app/Contents/Applications/Application\ Loader.app/Contents/itms/bin/')
    os.system(cmd)


def create_csv_android(app, argparser):
    csv = 'Product ID,Published State,Purchase Type,Auto Translate,Locale; Title; Description,Auto Fill Prices,Price,Pricing Template ID'
    pattern = '{0}.{1},published,managed_by_android,false,en_US; {3}; {4}; ru_RU; {5}; {6}, true,{2},'

    for i in app.inapps:
        rate = 60 * 1000 * 1000
        diff = 1000 * 1000
        inapps_str = pattern.format(app.package, i.id, i.cost * rate - diff,
                                    i.localisations[ID.en].title, i.localisations[ID.en].description,
                                    i.localisations[ID.ru].title, i.localisations[ID.ru].description
                                    )
        csv += '\n' + inapps_str
    kind = '' if not Project.instance.with_pro_version else '.' + argparser.app_kind
    fileutils.write(fileutils.root_dir + '/store/android_inapps%s.csv' % kind, csv)


def run(app_package, app_name, app_version, google_spreedsheet_id, argparser):
    app = App(app_package, app_name, app_version)
    parse_google_doc(app, google_spreedsheet_id)
    app.validate()
    create_itmsp(app, argparser)
    create_csv_android(app, argparser)
    print 'Finished'
