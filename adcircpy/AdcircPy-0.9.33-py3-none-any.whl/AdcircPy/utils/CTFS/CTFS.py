import argparse
from datetime import datetime, date
import os
from AdcircPy.utils import get_cache_dir
from AdcircPy import Model


class CTFS(object):

    def __init__(self, AdcircMesh, start_date=None, start_cycle=None):
        self._AdcircMesh = AdcircMesh
        self._start_date = start_date
        self._start_cycle = start_cycle

    @staticmethod
    def stop(force=False):
        raise NotImplementedError('Need to stop process.')

    @property
    def AdcircMesh(self):
        return self._AdcircMesh

    @property
    def start_date(self):
        return self._start_date

    @property
    def start_cycle(self):
        return self._start_cycle

    @property
    def _AdcircMesh(self):
        return self.__AdcircMesh

    @property
    def _start_date(self):
        return self.__start_date

    @property
    def _start_cycle(self):
        return self.__start_cycle

    @_AdcircMesh.setter
    def _AdcircMesh(self, AdcircMesh):
        assert isinstance(AdcircMesh, Model.AdcircMesh)
        self.__AdcircMesh = AdcircMesh

    @_start_date.setter
    def _start_date(self, start_date):
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        assert isinstance(start_date, date)
        self.__start_date = start_date

    @_start_cycle.setter
    def _start_cycle(self, start_cycle):
        self.__start_cycle = start_cycle


def get_args():
    parser = argparse.ArgumentParser(
        description="ctfs-manager start and stops the continuous tidal "
        + "forecasting system.")
    subparser = parser.add_subparsers()
    subparser_start = subparser.add_parser('start',
                                           help='Starts %(prog)s daemon')
    subparser_start.add_argument('--mesh')
    subparser_start.add_argument(
        '--start-date', default=datetime.now().date(),
        help="Start date for which you want the first forecast cycle results.")
    subparser_start.add_argument('--start-cycle', type=str)
    subparser_start.add_argument('--mesh-epsg', type=int, default=4326,
                                 help="(default: %(default)d)")
    subparser_start.add_argument('--mesh-vertical-datum', default='LMSL',
                                 choices=['LSML', 'NAVD88'],
                                 help="(default: %(default)s)")
    subparser_start.add_argument('--config-file')
    subparser_stop = subparser.add_parser('stop', help='Stops %(prog)s daemon')
    subparser_stop.add_argument('--force', action='store_true', default=False)
    return parser.parse_args()


def main():
    args = get_args()
    if hasattr(args, 'force'):
        CTFS.stop(force=args.force)
        exit()
    mesh = args.mesh
    if mesh is None:
        mesh = os.getenv('CTFS_MESH')
    if mesh is None:
        raise RuntimeError(
            'Must set $CTFS_MESH or explicitly pass a mesh using the '
            + '--mesh optional argument.')
    mesh = Model.AdcircMesh(mesh, SpatialReference=args.mesh_epsg,
                            vertical_datum=args.mesh_vertical_datum)
    CTFS(mesh)


if __name__ == '__main__':
    main()
