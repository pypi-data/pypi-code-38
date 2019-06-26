"""Dummies to stand in for macOS specific functions"""


NSActivityIdleDisplaySleepDisabled = (1 << 40)
NSActivityIdleSystemSleepDisabled = (1 << 20)
NSActivitySuddenTerminationDisabled = (1 << 14)
NSActivityAutomaticTerminationDisabled = (1 << 15)
NSActivityUserInitiated = (0x00FFFFFF | NSActivityIdleSystemSleepDisabled)
NSActivityUserInitiatedAllowingIdleSystemSleep = (NSActivityUserInitiated & ~NSActivityIdleSystemSleepDisabled)
NSActivityBackground = 0x000000FF
NSActivityLatencyCritical = 0xFF00000000


def begin_activity(options=None, reason=None):
    pass


def end_activity(activity):
    pass
