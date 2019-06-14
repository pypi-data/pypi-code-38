import xml.etree.ElementTree as ET
import game
import os
import fileutils
from project import Project
from validate_units import get_unit_type

logs = []


def log(msg):
    logs.append(msg)


def get_maps():
    result = []
    for i in xrange(100):
        file = fileutils.root_dir + '/Resources/ini/maps/map%d.xml' % i
        if os.path.isfile(file):
            result.append(file)
        for ii in xrange(100):
            file = fileutils.root_dir + '/Resources/ini/maps/map%d_%d.xml' % (i, ii)
            if os.path.isfile(file):
                result.append(file)
    return result


def check_unused_creeps(creeps):
    if not creeps:
        return

    units = game.get_units_path()
    files = []
    for unit, path in units.items():
        files.append(path)
    files.extend(get_maps())

    for file in files:
        data = open(file).read()

        index = 0
        while index < len(creeps):
            unit = creeps[index]
            position = data.find(unit)
            if position != -1:
                creeps.remove(unit)
            else:
                index += 1

        if not creeps:
            break

    for creep in creeps:
        print '  - Warning: detect unused creep [%s]'%creep


def validate_maps_content():
    units = game.get_units_list()
    unused_creeps = []
    for unit in units:
        if get_unit_type(unit) == 'creep':
            unused_creeps.append(unit)

    def use_unit(unit):
        if unit in unused_creeps:
            unused_creeps.remove(unit)

    files = get_maps()
    for file in files:
        root = ET.parse(file).getroot()

        waves = root.find('waves')
        if waves is None:
            waves = root.find('waves_hard')
        if waves is None:
            waves = root.find('waves_survival')
        if waves is None:
            waves = root.find('waves_tournament')
        if waves is None:
            log('Cannot find wave node in xml {}'.format(file))
            raise SystemError('Cannot find wave node in xml {}'.format(file))

        routes = root.find('routes')
        units_on_map = {}

        def validate_route(routeindex):
            try:
                int(routeindex)
            except:
                log('Route with index [{}] not is digit. {}'.format(routeindex, file))
                return False
            for route in routes:
                if route.attrib['name'] == routeindex:
                    return True
            log('Route with index [{}] not found in {}'.format(routeindex, file))
            return False

        def validate_routesubtype(rst):
            if rst not in ['main', 'left', 'right', 'random']:
                log('Unknow value of routesubtype [{}] in {}'.format(rst, file))

        for wave in waves:
            if 'defaultname' in wave.attrib:
                unit = wave.attrib['defaultname']
                if unit not in units:
                    log('Invalid name of unit [{}] in {}'.format(unit, file))
                units_on_map[unit] = 1
                use_unit(unit)
            if 'defaultrouteindex' in wave.attrib:
                validate_route(wave.attrib['defaultrouteindex'])
            if 'defaultroutesubtype' in wave.attrib:
                validate_routesubtype(wave.attrib['defaultroutesubtype'])
            for unitxml in wave:
                unit = unitxml.attrib['name'] if 'name' in unitxml.attrib else ''
                units_on_map[unit] = 1
                if unit and unit not in units:
                    log('Invalid name of unit [{}] in{}'.format(unit, file))
                if 'routeindex' in unitxml.attrib:
                    validate_route(unitxml.attrib['routeindex'])
                if 'routesubtype' in unitxml.attrib:
                    validate_routesubtype(unitxml.attrib['routesubtype'])
                use_unit(unit)
        if 'max_creeps_on_level' in Project.instance.validate:
            max_count = Project.instance.validate['max_creeps_on_level']
        else:
            max_count = 8
        if len(units_on_map) > max_count:
            log('Many creeps in {} ({}>{})'.format(file, len(units_on_map), max_count))

        for route in routes:
            main_points = len(route.find('main'))
            left_points = len(route.find('left'))
            right_points = len(route.find('right'))
            if main_points != left_points or main_points != right_points or left_points != right_points:
                log('Different count points in route. Map: {})'.format(file))
    check_unused_creeps(unused_creeps)


def validate_count():
    count_xml = 0
    count_rewards = 0
    count_locations = 0

    maps = get_maps()
    count_xml = len(maps)

    file = fileutils.root_dir + '/Resources/ini/maps/levels.xml'
    if not os.path.isfile(file):
        return
    rewards = ET.parse(fileutils.root_dir + '/Resources/ini/maps/levels.xml').getroot()
    for child in rewards:
        if child.tag.startswith('level_'):
            count_rewards += 1

    location_xml = ET.parse(fileutils.root_dir + '/Resources/ini/map/maplayer.xml')
    locations = location_xml.getroot().find('locations')
    if locations is None or len(locations) == 0:
        location_xml = ET.parse(fileutils.root_dir + '/Resources/ini/map/locations.xml')
        locations = location_xml.getroot().find('locations')
    for _ in locations:
        count_locations += 1
    for index in xrange(100):
        node = 'locations_%d' % index
        locations = location_xml.getroot().find(node)
        if locations is not None and len(locations):
            for _ in locations:
                count_locations += 1

    valid = count_locations == count_xml and count_locations == count_rewards
    if not valid:
        log('Count of levels is difference: \n\tlocations: {}\n\trewards: {}\n\txmls: {}'.
            format(count_locations, count_rewards, count_xml))


def validate():
    # try:
    validate_maps_content()
    validate_count()
    # except Exception as e:
    #     print(e)
    #     exit(-1)
