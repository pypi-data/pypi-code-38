import json
import os
import time
from functools import reduce
from random import randint
from time import perf_counter

from .resource import Resource
from .context import JSONContext


class ProfilerMeasurement:
    def __init__(self, profiler, item):
        self._profiler = profiler
        self._item = item

    def __enter__(self):
        self._start = perf_counter()
        self._sub_profiler = Profiler(self._profiler.sub_id(self._item))
        return self._sub_profiler

    def __exit__(self, *args):
        self._profiler._add_measurement(self._item,
                                        perf_counter() - self._start)
        self._profiler.merge(self._sub_profiler._measurements)


def DummyProfiler():
    return Profiler('dummy')


class Profiler:
    def __init__(self, id):
        self._id = id
        self._measurements = []

    def measure(self, item):
        return ProfilerMeasurement(self, item)

    def _add_measurement(self, item, time):
        def milliseconds(seconds):
            return int(seconds * 1000)

        self._measurements.append(('%s/%s' % (self._id, item),
                                   milliseconds(time)))

    def sub_id(self, sub_id):
        return '%s/%s' % (self._id, sub_id)

    def pack(self, value):
        return (self._measurements, value)

    def unpack(self, packed):
        self.merge(packed[0])
        return packed[1]

    def merge(self, measurements):
        self._measurements = self._measurements + measurements

    def save_report(self, reports_dir):
        filename = '%s/%s_%s_%s' % (reports_dir,
                                    self._id,
                                    time.strftime(
                                        '%Y-%m-%d-%H-%M-%S',
                                        time.gmtime()),
                                    randint(0, 99999))

        try:
            os.makedirs(reports_dir)
        except FileExistsError:
            pass

        with open(filename, 'w') as f:
            json.dump(self._format_report(), f)

    def _format_report(self):
        def group_measurements(acc, el):
            item, dt = el

            if item in acc:
                acc[item] = acc[item] + dt
            else:
                acc[item] = dt

            return acc

        return reduce(group_measurements, self._measurements, {})


class ReportsResource(Resource):
    def __init__(self, reports_dir):
        self._reports_dir = reports_dir


class ReportList(ReportsResource):
    def get(self, request):
        return JSONContext().response(os.listdir(self._reports_dir))


def _get_report_filenames(reports_dir, prefix):
    return list(filter(
        lambda filename: filename.startswith(prefix),
        os.listdir(reports_dir)))


class ReportCSVDetails(ReportsResource):
    def get(self, request, prefix):
        def format_csv(obj):
            return '\n'.join(list(
                map(lambda it: '"%s", %s' % it,
                    sorted(obj.items(),
                           key=lambda it: it[1],
                           reverse=True))))

        def read_report(acc, filename):
            with open('%s/%s' % (self._reports_dir, filename)) as f:
                acc[filename] = format_csv(json.load(f))

            return acc

        reports = reduce(read_report, _get_report_filenames(self._reports_dir,
                                                            prefix), {})
        return JSONContext().response(reports)


class ReportPlotDetails(ReportsResource):
    def get(self, request, prefix):
        def shortname(txt):
            CUTOFF = 50

            return (
                '…%s' % txt[-(min(len(txt), CUTOFF)):]
                if len(txt) > CUTOFF
                else txt)

        def is_significant(item):
            TIME_THRESHOLD = 1  # ms
            return item[1] > TIME_THRESHOLD

        def format_gnuplot(obj):
            return '\n'.join(list(
                map(lambda it: '"%s" %s' % (shortname(it[0]), it[1]),
                    filter(is_significant,
                           sorted(obj.items(),
                                  key=lambda it: it[0])))))

        def read_report(acc, filename):
            with open('%s/%s' % (self._reports_dir, filename)) as f:
                acc[filename] = format_gnuplot(json.load(f))

            return acc

        reports = reduce(read_report, _get_report_filenames(self._reports_dir,
                                                            prefix), {})
        return JSONContext().response(reports)


def should_profile_request(request):
    return request.META.get('HTTP_PROFILE', 'false') == 'true'
