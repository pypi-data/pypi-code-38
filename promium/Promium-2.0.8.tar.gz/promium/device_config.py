
from collections import namedtuple


USER_AGENT_ANDROID = (
    "Mozilla/5.0 (Linux; Android 8.0;"
    "Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko)"
    "Chrome/70.0.3538.77 Mobile Safari/537.36"
)

USER_AGENT_IOS = (
    "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34"
    "(KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
)

Device = namedtuple('Device', ['width', 'height', 'user_agent', 'device_name'])

CHROME_DESKTOP_1920_1080 = Device(1920, 1080, '', '')
CHROME_DESKTOP_1024_768 = Device(1024, 768, '', '')

ANDROID_360_640 = Device(360, 640, USER_AGENT_ANDROID, '')
ANDROID_1280_800 = Device(1280, 800, USER_AGENT_ANDROID, '')
ANDROID_1080_1920 = Device(1080, 1920, USER_AGENT_ANDROID, '')
IOS_750_1334 = Device(750, 1334, USER_AGENT_IOS, '')
IOS_1080_1920 = Device(1080, 1920, USER_AGENT_IOS, '')

#  opens emulator Nexus 5 (360x640) in browser window 1920x1080
EMULATED_NEXUS_5 = Device(1920, 1080, USER_AGENT_ANDROID, "Nexus 5")
#  opens emulator iPad Mini (768x1024) in browser window 1920x1080
EMULATED_IPAD_MINI = Device(1920, 1080, USER_AGENT_IOS, "iPad Mini")
#  opens emulator iPad Pro (1024x1366) in browser window 1920x1080
EMULATED_IPAD_PRO = Device(1920, 1080, USER_AGENT_IOS, "iPad Pro")
