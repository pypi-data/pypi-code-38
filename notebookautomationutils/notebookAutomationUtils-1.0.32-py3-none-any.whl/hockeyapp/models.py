import logging
import pprint
import typing
from datetime import datetime
from enum import Enum
from typing import List, Union


class CrashReasonStatus(Enum):
    open = 0
    resolved = 1
    ignored = 2

class AppVersionStatus(Enum):
    submitted = 1
    available = 2
    unknown = 3

class ReleaseType(Enum):
    beta = 0
    store = 1
    alpha = 2
    enterprise = 3


class UserRole(Enum):
    owner = 0
    developer = 1
    member = 2
    tester = 3

HistogramPoint  = typing.NamedTuple('HistogramPoint', [('point_date', str), ('occurrences', int)])
CrashAnnotation = typing.NamedTuple('CrashAnnotation', [('id', int),
                                                        ('crash_reason_id', int),
                                                        ('text', str),
                                                        ('created_at', datetime),
                                                        ('updated_at', datetime)])


class CrashReason(object):
    """
    A crash group or collection of crashes. They may span across app versions, devices, and dates
    Specific crashes are in the `Crash` object.
    """
    def __init__(self, kwarg):
        self.data = kwarg
        self.logger = logging.getLogger(__name__)
        self._strptimeformat = '%Y-%m-%dT%H:%M:%SZ'
        # Clean up some data from Hockeyapp.
        if self.data.get('class', None) == '-':
            self.data['class'] = None
        # a bunch of keys return 'None' - just delete them.
        self.data = {k: v for k, v in self.data.items() if v is not None}

    @property
    def id(self) -> int:
        return self.data['id']

    @property
    def app_id(self) -> int:
        return self.data['app_id']

    @property
    def created_at(self) -> datetime:
        return datetime.strptime(self.data['created_at'], self._strptimeformat)

    @property
    def updated_at(self) -> datetime:
        return datetime.strptime(self.data['updated_at'], self._strptimeformat)

    @property
    def last_crash_at(self) -> datetime:
        return datetime.strptime(self.data['last_crash_at'], self._strptimeformat)

    @property
    def status(self) -> CrashReasonStatus:
        # This is usually an Int, but let's hide that.
        return CrashReasonStatus(self.data['status'])

    @property
    def reason(self) -> Union[str, None]:
        return self.data.get('reason', None)

    @property
    def exception_type(self) -> Union[str, None]:
        return self.data.get('exception_type', None)  # example: SIGSEGV for iOS

    @property
    def is_fixed(self) -> bool:
        return self.data.get('fixed', False)

    @property
    def app_version_id(self) -> int:
        return self.data.get('app_version_id', 0)

    @property
    def bundle_version(self) -> int:
        return self.data.get('bundle_version_id', 0)

    @property
    def bundle_short_version(self) -> Union[str, None]:
        return self.data.get('bundle_short_version', None)

    @property
    def number_of_crashes(self) -> int:
        return self.data.get('number_of_crashes', 0)

    @property
    def crash_method(self) -> Union[str, None]:
        """Returns the method name where the crash occurred."""
        return self.data.get('method', None)

    @property
    def crash_file(self) -> Union[str, None]:
        """Returns the filename where the crash occurred. e.g. main.m"""
        return self.data.get('file', None)

    @property
    def crash_class(self) -> Union[str, None]:
        return self.data.get('class', None)

    @property
    def crash_line(self) -> int:
        return self.data.get('line', 0)

    @property
    def crash_url(self):
        """
        Get the URL to view this crash reason in the HockyApp website
        :return: URL to hockeyapp website to view this crash reason
        """
        return 'https://rink.hockeyapp.net/manage/apps/' \
               '{app_id}/app_versions/{app_version_id}/crash_reasons/' \
               '{id}'.format(**self.data)

    def platform(self) -> 'str':
        """
        What platform did this crash occur on?
        :return: one of [Android, iOS, Windows]
        """
        if (self.crash_file is not None and self.crash_file.endswith('.m')) \
                or (self.exception_type is not None and self.exception_type.startswith('SIG')):
            return 'iOS'
        if self.crash_file is not None and self.crash_file.endswith('.java'):
            return 'Android'
        return 'Unknown'

    def crash_title(self) -> str:
        """Returns a nice string similar to the summary on hockeyapp website."""
        platform = self.platform()
        if platform == 'iOS':
            # - [SFOAuthCoordinator updateCredentials:] line 767
            # SIGSEGV - objc_msgSend() selector name: observeValueForKeyPath:ofObject:change:context:
            if self.crash_class is not None and self.crash_method is not None:
                if 'reason' in self.data:
                    return '- [{class} {method}] line {line}\n' \
                           '{exception_type} - {reason}'.format(**self.data)
                else:
                    return '- [{class} {method}] line {line}\n' \
                           '{exception_type}'.format(**self.data)
            elif self.crash_method is not None:
                return '{exception_type} - {method}'.format(**self.data)
            elif 'reason' in self.data:
                return '{exception_type}: {reason}'.format(**self.data)
            else:
                return self.exception_type or '(no crash)'
        elif platform == 'Android':
            return '{class}.{method} line {line}\n' \
                    '{reason}'.format(**self.data)
        else:
            self.logger.warning('cannot determine platform type of this crash=%s',
                                pprint.pformat(self.data))
            return self.reason or '(no crash)'

    def emoji(self) -> str:
        """
        Returns a cute emoji to go along with this crash.
        :return a cute emoji
        :rtype str
        """
        if self.platform() == 'iOS':
            signals = {
                'SIGSEGV': '\U0001F4A5',  # bad memory access -> :collision-symbol:
                'SIGBUS':  '\U0001F4A5',  # bad memory access -> (same)
                'SIGABRT': '\U0001F4A5',  # The process exited abnormally.
                'SIGILL': '',  # The process attempted to execute an illegal or undefined instruction.
                'SIGTRAP': '',
            }
            if self.exception_type in signals:
                return signals[self.exception_type]

            # :reminder-ribbon:
            # The exception code 0xbaaaaaad indicates that the log is a stackshot of
            # the entire system, not a crash report. To take a stackshot, push the Home button and any
            # volume button. Often these logs are accidentally created by users, and do not indicate an error.

            # The exception code 0xbad22222 indicates that a VoIP application has been terminated
            # by iOS because it resumed too frequently.

            # :timer-clock: \U000023F2
            # The exception code 0x8badf00d indicates that an application has been terminated
            # by iOS because a watchdog timeout occurred. The application took too long to launch,
            # terminate, or respond to system events. One common cause of this is doing synchronous
            # networking on the main thread. Whatever operation is on Thread 0 needs to be moved
            # to a background thread, or processed differently, so that it does not block the main
            # thread.

            # :fire:
            # The exception code 0xc00010ff indicates the app was killed by the operating system
            # in response to a thermal event. This may be due to an issue with the particular device
            # that this crash occurred on, or the environment it was operated in. For tips on making
            # your app run more efficiently, see iOS Performance and Power Optimization with
            # Instruments WWDC session.

            # The exception code 0xdead10cc indicates that an application has been terminated by
            # iOS because it held on to a system resource (like the address book database)
            # while running in the background.

            # snowflake?
            # The exception code 0xdeadfa11 indicated that an application has been force quit by
            # the user. Force quits occur when the user first holds down the On/Off button until
            # "slide to power off" appears, then holds down the Home button. It's reasonable to
            # assume that the user has done this because the application has become unresponsive,
            # but it's not guaranteed - force quit will work on any application.

        if self.platform() == 'Android':
            # common exceptions
            exceptionclass = self.reason.split(':')[0]

            common_exceptions = {
                'java.lang.NullPointerException': '\U0001F573',  # :hole:
                'java.lang.RuntimeException': '\U0001F3C3',  # :runner:
                'android.view.WindowManager$BadTokenException': '\U0001F5BC',  # frame with picture
                'java.lang.OutOfMemoryError': '',
                'java.lang.IllegalStateException': '\U0001F3F4',  # waving black flag
            }
            if exceptionclass in common_exceptions:
                return common_exceptions[exceptionclass]
        return '\U00002620'  # skull-and-crossbones


class Crash(object):
    """
    Represents a single crash inside a CrashGroup
    """

    def __init__(self, kwargs):
        self.data = kwargs
        self._strptimeformat = '%Y-%m-%dT%H:%M:%SZ'

    @property
    def id(self) -> int:
        return self.data['id']

    @property
    def app_id(self) -> int:
        return self.data['app_id']

    @property
    def app_version_id(self) -> int:
        return self.data['app_version_id']

    @property
    def crash_reason_id(self) -> int:
        return self.data['crash_reason_id']

    @property
    def created_at(self) -> datetime:
        return datetime.strptime(self.data['created_at'], self._strptimeformat)

    @property
    def updated_at(self) -> datetime:
        return datetime.strptime(self.data['updated_at'], self._strptimeformat)

    @property
    def oem(self) -> str:
        """OEM of the device. For example, 'Apple'"""
        return self.data['oem']

    @property
    def model(self) -> str:
        """Device model where the crash occurred. For example, 'iPhone3.1'"""
        return self.data['model']

    @property
    def bundle_version(self) -> int:
        # is this always an integer?? comes as Str from Hockeyapp API documentation.
        return int(self.data['bundle_version'])

    @property
    def bundle_short_version(self) -> str:
        """gets the 'marketing label' version label. For example, '1.2'"""
        return self.data['bundle_short_version']

    @property
    def contact_string(self) -> str:
        # this converts the "" values to None
        return self.data['contact_string'] or None

    @property
    def user_string(self) -> str:
        # this converts the "" values to None
        return self.data['user_string'] or None

    @property
    def os_version(self) -> str:
        """The operating system version of the device where the crash occurred. Example: '7.0'"""
        return self.data['os_version']


class App(object):

    def __init__(self, kwargs):
        self.data = kwargs

    @property
    def id(self) -> int:
        """
        The identifier for this App. This often shows up in URLs so you can
        now tie it back to a specific bundleId and platform.
        """
        return int(self.data['id'])

    @property
    def title(self) -> str:
        return self.data['title']

    @property
    def bundle_identifier(self) -> str:
        return self.data['bundle_identifier']

    @property
    def public_identifier(self) -> str:
        """Sometimes known as the HockeyApp App ID, this looks like a UUID without any hyphens."""
        return self.data['public_identifier']

    @property
    def device_family(self) -> str:
        return self.data['device_family']

    @property
    def minimum_os_version(self) -> str:
        return self.data['minimum_os_version']

    @property
    def release_type(self) -> ReleaseType:
        return ReleaseType(self.data['release_type'])

    @property
    def status(self):
        # another integer-based ENUM
        # 1 = to not allow users to download the version
        # 2 = allow users to download
        return self.data['status']

    @property
    def os_platform(self) -> str:
        """iOS, Android, Mac OS, Windows Phone, Custom"""
        return self.data['platform']

    @property
    def created_at(self) -> datetime:
        return datetime.strptime(self.data['created_at'], '%Y-%m-%dT%H:%M:%SZ')

    @property
    def updated_at(self) -> datetime:
        return datetime.strptime(self.data['updated_at'], '%Y-%m-%dT%H:%M:%SZ')

    @property
    def description(self) -> str:
        """plain text with newlines. (\r\n)"""
        return self.data['description']

    @property
    def retention_days(self) -> Union[int, str]:
        """
        Returns the retention policy. Typically 28, 90, or 'unlimited'
        :return: an int if possible, otherwise a str.
        """
        try:
            return int(self.data['retention_days'])
        except ValueError:
            return self.data['retention_days']


class AppVersion(object):

    def __init__(self, kwargs):
        self.data = kwargs

    @property
    def id(self) -> int:
        return int(self.data['id'])

    @property
    def version(self) -> str:
        """
        Usually a build number, like an integer, but on Windows, this is a semantic version.
        """
        return self.data['version']

    @property
    def mandatory(self) -> bool:
        return self.data['mandatory']

    @property
    def config_url(self) -> str:
        return self.data['config_url']

    @property
    def download_url(self) -> str:
        return self.data['download_url']

    @property
    def timestamp(self) -> datetime:
        #TODO looks like unix time.
        return None

    @property
    def app_size(self) -> int:
        """Application package file size, in bytes"""
        return self.data['appsize']

    @property
    def device_family(self) -> str:
        return self.data['device_family']

    @property
    def notes(self) -> str:
        """simple HTML release notes."""
        return self.data['notes']

    @property
    def status(self) -> AppVersionStatus:
        return AppVersionStatus(self.data['status'])

    @property
    def shortversion(self) -> str:
        return self.data['shortversion']

    @property
    def minimum_os_version(self) -> str:
        return self.data['minimum_os_version']

    @property
    def title(self) -> str:
        """Title of the App"""
        return self.data['title']


class AppStatistic(object):

    def __init__(self, kwargs):
        self.data = kwargs

    @property
    def id(self) -> int:
        return self.data['id']

    @property
    def version(self) -> str:
        """
        Usually a build number, like an integer, but on Windows, this is a semantic version.
        """
        return self.data['version']

    @property
    def shortversion(self) -> str:
        return self.data['shortversion']

    @property
    def created_at(self) -> datetime:
        return datetime.strptime(self.data['created_at'], '%Y-%m-%dT%H:%M:%SZ')

    @property
    def crashes(self) -> int:
        """Total count of crashes for this App Version"""
        return self.data['statistics']['crashes']

    @property
    def devices(self) -> int:
        return self.data['statistics']['devices']

    @property
    def count_downloads(self) -> int:
        return self.data['statistics']['downloads']

    @property
    def count_installs(self) -> int:
        return self.data['statistics']['installs']

    @property
    def last_request_at(self) -> datetime:
        return datetime.strptime(self.data['statistics']['last_request_at'],
                                 '%Y-%m-%dT%H:%M:%SZ')

    @property
    def usage_time(self):
        return self.data['statistics']['usage_time']


class User(object):

    def __init__(self, kwargs):
        self.data = kwargs

    @property
    def user_app_id(self) -> int:
        """
        The identifier for this user on the app, unique for an app
        """
        return int(self.data['id'])

    @property
    def user_id(self) -> int:
        """
        The identifier for this user on the system, unique for a user
        """
        return int(self.data['user_id'])

    @property
    def app_id(self) -> str:
        """
        app id for which this user has access
        """
        return self.data.get('app_id')

    @property
    def role(self) -> UserRole:
        return UserRole(int(self.data['role']))

    @property
    def tags(self) -> List[str]:
        # handle the case of splitting empty strings as it returns list with one element
        tags = self.data['tags']
        if tags:
            return tags.split(',')
        else:
            return []

    @property
    def email(self) -> str:
        return self.data['email']

    @property
    def name(self) -> str:
        return self.data['full_name']

    @property
    def created_at(self) -> datetime:
        return datetime.strptime(self.data['created_at'], '%Y-%m-%dT%H:%M:%SZ')
