import os
import re
import sys
import click
import time
import json
import datetime
import logging
from potnanny_core.database import init_db, init_engine, init_users, db_session
from potnanny_core.utils import load_plugins, blescan_devices, subprocess_cmd
from potnanny_core.models.room import Room
from potnanny_core.models.sensor import Sensor
from potnanny_core.models.measurement import Measurement
from potnanny_core.models.action import Action, SingularAction, ActionRouter
from potnanny_core.models.plugin import BlePluginBase, ActionPluginBase
from potnanny_core.models.schedule import ScheduleOnOff, RoomLightManager
from potnanny_core.models.setting import PollingInterval


# logger basic setup
logger = logging.getLogger('potnanny')
logger_format = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s')

# global datetimes
g_now = datetime.datetime.now().replace(second=0, microsecond=0)
g_utcnow = datetime.datetime.utcnow().replace(second=0, microsecond=0)

line_width = 30

# config object for Click
class Config(object):
    def __init__(self):
        self.mode = 'production'
        self.config = None

pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('-m', '--mode', default='production', type=click.Choice([
    'development', 'production', 'testing'] ))
@click.option('--debug', is_flag=True)
@pass_config
def cli(config, mode, debug):
    """PotNanny Command-Line Interface"""

    # logging setup
    global logger
    handler = logging.StreamHandler()
    handler.setFormatter(logger_format)

    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    logger.addHandler(handler)

    # database config
    config.mode = mode
    if mode == 'development':
        from potnanny_core.config import Development
        config.config = Development
    elif mode == 'testing':
        from potnanny_core.config import Testing
        config.config = Development
    else:
        from potnanny_core.config import Production
        config.config = Production


    logger.debug(config.mode.upper() + " mode")

    # initialize db interface/engine
    uri = config.config.SQLALCHEMY_DATABASE_URI
    logger.debug("initializing db engine for {}".format(uri))
    init_engine(uri)


## BLE devices
# list
## ==========================
@cli.group()
def ble():
    """Bluetooth LE functions."""

    pass

@ble.command(name='scan')
def scan_ble():
    """Scan and list all discovered BLE devices"""

    data = blescan_devices()
    click.echo("BLE Devices")
    click.echo("-" * line_width)
    if not data:
        click.echo("No data")
    else:
        for d in data:
            click.echo("address='{}', name='{}'".format(d['address'],d['name']))


## DB functions
## init, migrate?
## ==========================
@cli.group()
def db():
    """Database functions."""

    pass

@db.command(name='init')
def setup_db():
    """Initialize new database."""

    click.echo("Initializing database and creating models... ", nl=False)
    init_db()
    click.echo("OK")

    click.echo("Creating default user accounts... ", nl=False)
    init_users()
    click.echo("OK")


## ROOM functions
## list, add, delete, rename, read, schedules
## ==========================
@cli.group()
def room():
    """Room functions."""

    pass

@room.command(name='list')
def list_rooms():
    """List rooms"""

    rooms = Room.query.all()
    click.echo("Rooms")
    click.echo("-" * line_width)
    if not rooms:
        click.echo("No data")
    else:
        for room in rooms:
            click.echo("id={}, name='{}'".format(room.id, room.name))

@room.command(name='add')
@click.argument('name', required=True)
def add_room(name):
    """Add named room"""

    room = Room(name=name)
    db_session.add(room)
    db_session.commit()
    click.echo("OK")

@room.command(name='delete')
@click.argument('id', required=True)
def delete_room(id):
    """Delete room with id"""

    room = Room.query.get(id)
    if room:
        db_session.delete(room)
        db_session.commit()
        click.echo("OK")
    else:
        click.echo("Room id {} not found".format(id))

@room.command(name='rename')
@click.argument('room_id', required=True, type=int)
@click.argument('name', required=True, type=str)
def rename_room(room_id, name):
    """Rename room"""

    room = Room.query.get(room_id)
    if room:
        room.name = name
        db_session.commit()
        click.echo("OK")
    else:
        click.echo("Room id {} not found".format(room_id))

@room.command(name='read')
def read_rooms():
    """Read latest room measurements"""

    rooms = Room.query.all()
    for room in rooms:
        click.echo("ROOM ({}): '{}'".format(room.id, room.name))
        click.echo("-" * 30)
        data = room.environment()
        if data:
            for k, v in data.items():
                click.echo("  {}  {}".format(v, k))
        else:
            click.echo("No data")

        click.echo("")

@room.command(name='schedules')
@click.argument('id', required=True, type=int)
def room_schedules(id):
    """List schedules for room with id"""

    room = Room.query.get(id)
    if room:
        click.echo("ROOM ({}): '{}' schedules".format(room.id, room.name))
        click.echo("-" * line_width)
        if room.schedules:
            click.echo("  {:2} {:24} {}".format('id', 'name', 'is_active'))
            click.echo("-" * line_width)
            for s in room.schedules:
                click.echo("  {:2} {:24} {}".format(s.id, s.name, s.is_active))
        else:
            click.echo("No data")
    else:
        click.echo("Room id {} not found".format(id))


## SENSOR functions
## list, assign, rename, read
## ==========================
@cli.group()
def sensor():
    """Sensor functions."""

    pass

@sensor.command(name='list')
def list_sensors():
    """List sensors"""

    sensors = Sensor.query.all()
    click.echo("Sensors")
    click.echo("-" * line_width)
    if not sensors:
        click.echo("No data")
    else:
        for sensor in sensors:
            click.echo("id={}, address='{}', name='{}'".format(
                sensor.id, sensor.address, sensor.name))

@sensor.command(name='rename')
@click.argument('sensor_id', required=True, type=int)
@click.argument('name', required=True, type=str)
def rename_sensor(sensor_id, name):
    """Rename sensor"""

    sensor = Sensor.query.get(sensor_id)
    if sensor:
        sensor.name = name
        db_session.commit()
        click.echo("OK")
    else:
        click.echo("Sensor id {} not found".format(sensor_id))

@sensor.command(name='assign')
@click.argument('sensor_id', required=True, type=int)
@click.argument('room_id', required=True, type=int)
def assign_sensor(sensor_id, room_id):
    """Assign sensor to a room"""

    sensor = Sensor.query.get(sensor_id)
    if not sensor:
        click.echo("Sensor id {} not found".format(sensor_id))
    else:
        sensor.room_id = room_id
        db_session.commit()
        click.echo("OK")

@sensor.command(name='read')
@click.argument('sensor_id', required=True, type=int)
def read_sensor(sensor_id, room_id):
    """Read latest sensor measurements"""

    sensor = Sensor.query.get(sensor_id)
    click.echo("Sensor ({}) Readings".format(sensor_id))
    click.echo("-" * line_width)
    if not sensor:
        click.echo("Sensor id {} not found".format(sensor_id))
    else:
        data = sensor.latest_readings()
        if not data:
            click.echo("No data")
        else:
            for k, v in data.items():
                click.echo("  {}  {}".format(v, k))


## SCHEDULE functions
## list
## ==========================
@cli.group()
def schedule():
    """Sensor functions."""

    pass

@schedule.command(name='get')
@click.argument('schedule_id', required=True, type=int)
def get_schedule(schedule_id):
    """Get details for schedule with id."""

    sched = ScheduleOnOff.query.get(schedule_id)
    if not sensor:
        click.echo("Schedule with id {} not found".format(sensor_id))
    else:
        data, errors = ScheduleOnOffSchema().dump(sched)
        if errors:
            click.echo("ERROR: {}".format(errors))
        else:
            click.echo(json.dumps(data, indent=4, sort_keys=True))

        click.echo("OK")


## RF functions
## scan, send
## ==========================
@cli.group()
def rf():
    """Radio Frequency (RF) functions."""
    pass

@rf.command(name='scan')
def scan_rf():
    """Scan RF for remote code"""
    rval, output, errors = subprocess_cmd(['rf_scan'])
    if rval:
        click.echo("Error: '{}'".format(errors))
    else:
        click.echo("Code: '{}'".format(output))


## POLL command
## and all associated functions for polling, actions, etc...
## ==========================
@cli.command()
@click.option('-f', '--force', is_flag=True,
    help="force poll regardless of the poll interval setting.")
@pass_config
def poll(config, force):
    """Poll Bluetooth LE devices for measurements."""

    # first, process any future actions and schedules that need to happen.
    process_future_actions(g_utcnow)
    process_schedules(g_utcnow)

    # not the right time to be polling devices?
    if not force and g_now.minute % PollingInterval.get() > 0:
        # confirm_triggered_outlet_states()
        logger.debug("Incorrect polling interval. No polling to do.")
        sys.exit(0)

    register_plugins(config.config.POTNANNY_PLUGIN_PATH)
    collect_ble_measurements()


def process_future_actions(now=datetime.datetime.utcnow()):
    """
    process any SingularActions that need action now.

    args:
        - datetime: defaults to utcnow
    returns:
        none
    raises:
        none
    """

    actions = SingularAction.query.filter(SingularAction.completed is None).all()
    if not actions:
        return

    for a in actions:
        if not a.runs_now(now):
            continue

        result = ActionRouter.route(a.action)
        if result:
            a.status = 'ok'
            a.completed = now
        else:
            a.status = 'failed at %s' % now

        db_session.commit()


def process_schedules(now=datetime.datetime.utcnow()):
    """
    process any ScheduleOnOff that need action now.

    args:
        - datetime: defaults to utcnow
    returns:
        none
    raises:
        none
    """

    scheds = ScheduleOnOff.query.all()
    if not scheds:
        return

    for s in scheds:
        action = s.action_now(now)
        if action:
            result = ActionRouter.route(action)


def register_plugins(plugin_path):
    """
    load and register BLE and Action plugins from base path

    args:
        - str (path name)
    returns:
        none
    raises:
        RuntimeError if there are no BLE plugins to scan with.
    """

    try:
        load_plugins(os.path.join(plugin_path, 'ble'))
        load_plugins(os.path.join(plugin_path, 'action'))
    except:
        logger.exception("Failure loading plugins")

    if len(BlePluginBase.plugins) == 0:
        raise RuntimeError("No system BLE plugins found in %s" % plugin_path)


def collect_ble_measurements():
    """
    Scan and collect measurements from all BLE devices
    """
    measurements = []
    ble_devices = blescan_devices()
    if ble_devices:
        for cls in BlePluginBase.plugins:
            results = cls.poll(ble_devices)
            if results:
                measurements += results

    if measurements:
        load_measurements(measurements)


def load_measurements(data):
    """
    load measurement data into database, take actions on measurements if needed.

    args:
        - a list: contains dicts, like:
        [
            {   'address': '11:11:11:11:11',
                'name': 'flower care',
                'measurements': {
                    'temperature': 24.2,
                    'soil-moisture': 21.0,
                    'light': 11300.0,
                    'soil-ec': 612,
                }
            },
        ]

    returns:
        none
    raises:
        none
    """

    logger.debug("loading measurements from {} sensors".format(len(data)))

    for d in data:
        meas = None
        sensor = get_or_create_sensor(d)
        if not sensor:
            continue

        for k, v in d['measurements'].items():
            params = {
                'sensor_id': sensor.id,
                'value': v,
                'type': k,
                'created': g_utcnow }

            try:
                meas = Measurement(**params)
                db_session.add(meas)
                db_session.commit()
            except Exception:
                logger.exception("create new Measurement failed")
                continue

            # sensors not assigned to a room cannot have actions. so skip
            if sensor.room_id is None:
                continue

            room = Room.query.get(sensor.room_id)
            if not room:
                continue

            for action in room.actions:
                if action.is_active:
                    action.eval_measurement(meas)
