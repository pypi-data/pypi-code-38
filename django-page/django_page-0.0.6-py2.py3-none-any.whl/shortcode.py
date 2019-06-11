import re
from pprint import pprint

from django.conf import settings
from django.template import RequestContext, Template

REMAP_COMMANDS = {
    "페이지넣기": "page",
    "반복문구넣기": "pagelet",
    "포함하기": "include",
    "가져오기": "include",
    "다운로드": "download",
}

if hasattr(settings, "PAGE_SHORTCODES"):
    REMAP_COMMANDS = { **REMAP_COMMANDS, **settings.PAGE_SHORTCODES}

UNPACK_WITH = [
    'page',
]

if hasattr(settings, "PAGE_UNPACK_WITH"):
    UNPACK_WITH = (*UNPACK_WITH, *settings.PAGE_UNPACK_WITH)


def remap_and_markup(matches):
    groups = tuple(map(lambda x: x.strip(), matches.groups()))

    command = groups[0]
    args = groups[1].split()

    if command in REMAP_COMMANDS.keys():
        command = REMAP_COMMANDS[command]
    elif command in REMAP_COMMANDS.values():
        pass
    else:
        return "[등록되지 않은 단축어 사용]"

    if command == "include":
        args[0] = settings.PAGE_TARGET_MAP.get(args[0], args[0])

    args = map(lambda x: '"%s"' % x, args)

    template_code = '{%% %s %s %%}' % (command, " ".join(args))
    return template_code


def unpack_shortcode(content):
    key_and_command = list(REMAP_COMMANDS.keys()) + list(REMAP_COMMANDS.values())
    full_commands = "|".join(key_and_command)
    return re.sub(r'\[(' + full_commands + ')(.+?)\]', remap_and_markup, content, flags=re.IGNORECASE)


def unpack_content_with_request(request, content, data=None):
    if data is None:
        data = {}
    return unpack_content(content, RequestContext(request, data))


def unpack_content(content, context):
    content = "".join(["{%% load %s %%}" % tags for tags in UNPACK_WITH]) + unpack_shortcode(content)
    return Template(content).render(context)
