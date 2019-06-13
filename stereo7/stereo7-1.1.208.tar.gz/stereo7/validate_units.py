import xml.etree.ElementTree as ET
import game
import re
import os
import fileutils
from project import Project

logs = []
UNITS = {}


def log(msg):
    logs.append(msg)


def validate_unit_events():

    valid_events = [
        [re.compile(r'on_create'), []],
        [re.compile(r'on_see.+'), []],
        [re.compile(r'on_lose.+'), []],
        [re.compile(r'show_.+'), []],
        [re.compile(r'on_shoot_critical'), []],
        [re.compile(r'on_shoot_critical_byangle\d+'), []],
        [re.compile(r'on_shoot'), []],
        [re.compile(r'on_shoot\d+'), []],
        [re.compile(r'on_shoot_byangle\d+'), []],
        [re.compile(r'on_shoot\d+_byangle\d+'), []],
        [re.compile(r'on_sleep'), []],
        [re.compile(r'on_cocking'), []],
        [re.compile(r'on_relaxation'), []],
        [re.compile(r'on_readyfire'), []],
        [re.compile(r'on_charging'), []],
        [re.compile(r'on_charging_\d+'), []],
        [re.compile(r'on_waittarget'), []],
        [re.compile(r'on_waittarget_\d+'), []],
        [re.compile(r'on_waittarget_finish'), []],
        [re.compile(r'on_waittarget_finish_\d+'), []],
        [re.compile(r'on_move'), []],
        [re.compile(r'on_stop'), []],
        [re.compile(r'on_die'), []],
        [re.compile(r'on_die\d+'), []],
        [re.compile(r'on_die_finish'), []],
        [re.compile(r'on_enter'), []],
        [re.compile(r'on_enter_finish'), []],
        [re.compile(r'on_damaged'), ['tower', 'hero', 'creep']],
        [re.compile(r'on_damage'), ['bullet', 'skill']],
        [re.compile(r'turn_\d+'), []],
        [re.compile(r'on_rotate\d+'), []],
        [re.compile(r'on_spawn'), []],
        [re.compile(r'on_spawn_unit_\d+'), []],
        [re.compile(r'on_healing'), []],
        [re.compile(r'crit_area_\d+'), ['hero']],
        [re.compile(r'crit_longrange_\d+'), ['hero']],
        [re.compile(r'crit_area'), ['hero']],
        [re.compile(r'crit_longrange'), ['hero']],
        [re.compile(r'on_select'), ['hero']],
        [re.compile(r'on_deselect'), ['hero']],

        # custom events
        [re.compile(r'spawn:\d'), ['desant']],
        [re.compile(r'on_jumping_\d'), ['creep']],
        [re.compile(r'on_on_ground'), ['creep']],
        [re.compile(r'on_rage_initiator_rand\d+'), ['creep']],
        [re.compile(r'kill_teleport'), ['hero']],
        [re.compile(r'kill_teleport_back'), ['hero']],
        [re.compile(r'teleport'), ['hero']],
        [re.compile(r'create_rocket_l'), ['hero']],
        [re.compile(r'create_rocket_r'), ['hero']],

        # robot
        [re.compile(r'on_builded'), ['hero']],
        [re.compile(r'on_skill_activated_robot_skill_ballista'), ['hero']],
        [re.compile(r'on_skill_activated_robot_skill_minigun'), ['hero']],
        [re.compile(r'on_skill_activated_robot_skill_rocket'), ['hero']],
        [re.compile(r'on_skill_activated_robot_skill_sniper'), ['hero']],
        [re.compile(r'on_skill_activated_robot_skill_tesla'), ['hero']],
        [re.compile(r'on_skill_prepare_robot_skill_ballista'), ['hero']],
        [re.compile(r'on_skill_prepare_robot_skill_minigun'), ['hero']],
        [re.compile(r'on_skill_prepare_robot_skill_rocket'), ['hero']],
        [re.compile(r'on_skill_prepare_robot_skill_sniper'), ['hero']],
        [re.compile(r'on_skill_prepare_robot_skill_tesla'), ['hero']],
        [re.compile(r'on_skill_top'), ['hero']],
        [re.compile(r'on_skill_down'), ['hero']],
        [re.compile(r'prepare_gun'), ['hero']],
        [re.compile(r'prepare_turret'), ['hero']],
        [re.compile(r'skill_gun'), ['hero']],
        [re.compile(r'skill_turret'), ['hero']],
    ]

    mandatory_events = [
        []
    ]

    for unit, path in UNITS.items():
        type = get_unit_type(unit)
        if type is None:
            continue
        events = get_all_unit_events(unit)
        for event in events:
            valid = False
            for pattern_info in valid_events:
                pattern = pattern_info[0]
                types = pattern_info[1]
                match = re.match(pattern, event)
                if match is not None:
                    valid = not types or type in types
                    break
            if not valid:
                log('Unknown unit event [%s:%s][%s]' % (unit, type, event))


def get_unit_type(unit):
    global UNITS
    if not UNITS:
        UNITS = game.get_units_path()

    path = UNITS[unit]
    while True:
        if not os.path.isfile(path):
            log('Template not exist [%s]'%path)
            break
        root = ET.parse(path).getroot()
        if 'unittype' in root.attrib:
            return root.attrib['unittype']
        if 'template' in root.attrib:
            path = fileutils.root_dir + '/Resources/' + root.attrib['template']
        else:
            return None


def get_all_unit_events(unit):
    global UNITS
    if not UNITS:
        UNITS = game.get_units_path()

    result = []
    path = UNITS[unit]
    while True:
        root = ET.parse(path).getroot()

        events_xml_range = root.findall('events')
        for events_xml in events_xml_range:
            for child in events_xml:
                name = child.attrib['name']
                result.append(name)

        if 'template' in root.attrib:
            path = fileutils.root_dir + '/Resources/' + root.attrib['template']
        else:
            break
    return result


def validate():
    # try:
    validate_unit_events()
    # except Exception as e:
    #     print(e)
    #     exit(-1)
