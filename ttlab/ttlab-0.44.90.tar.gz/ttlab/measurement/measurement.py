from ..mass_spectrometer import MassSpectrometer
from ..flow_reactor import FlowReactor
from ..xps import XPS
from ..X0_reactor import X0Reactor
from ..optical_spectroscopy import OpticalSpectroscopy
from ..frames import Frames


def get_measurement_from_history_event(history_event, dbConnection):
    measurement = None

    if history_event['description'] == 'xps':
        measurement = _import_xps_from_history_event(history_event, dbConnection)
        measurement.history_event = history_event
    elif history_event['description'].lower() == 'x0':
        measurement = _import_X0_from_history_event(history_event, dbConnection)
        measurement.history_event = history_event
    elif history_event['description'] == 'cary':
        measurement = _import_cary5000_from_history_event(history_event, dbConnection)
        measurement.history_event = history_event
    elif history_event['description'] == 'fart':
        measurement = _import_frames_from_history_event(history_event, dbConnection)
        measurement.history_event = history_event
    return measurement


def _import_cary5000_from_history_event(history_event, dbConnection):
    gridfs = dbConnection.get_gridfs_file(id=history_event['file_id'])
    return OpticalSpectroscopy(gridfs=gridfs, equipment_name='cary5000')


def _import_X0_from_history_event(history_event, dbConnection):
    grid_fr = None
    grid_ms = None
    grid_ils = None
    grid_lamp = None
    if history_event['file_id_fr'] is not None:
        grid_fr = dbConnection.get_gridfs_file(id=history_event['file_id_fr'])
    if history_event['file_id_ms'] is not None:
        grid_ms = dbConnection.get_gridfs_file(id=history_event['file_id_ms'])
    if history_event['file_id_ils'] is not None:
        grid_ils = dbConnection.get_gridfs_file(id=history_event['file_id_ils'])
    if history_event['file_id_lamp'] is not None:
        grid_lamp = dbConnection.get_gridfs_file(id=history_event['file_id_lamp'])
    return X0Reactor(gridfs_fr=grid_fr, gridfs_ms=grid_ms)


def _import_xps_from_history_event(history_event, dbConnection):
    grid_fs = dbConnection.get_gridfs_file(id=history_event['file_id'])
    if history_event['extra'] == 'survey':
        return XPS(gridfs_survey=grid_fs)
    return XPS(gridfs_multi=grid_fs)


def _import_frames_from_history_event(history_event, dbConnection):
    gridfs = dbConnection.get_gridfs_file(id=history_event['file_id'])
    return Frames(gridfs=gridfs)
