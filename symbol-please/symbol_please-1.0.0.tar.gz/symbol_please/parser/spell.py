"""Spell events module."""
import asyncio
import datetime
import logging
import re

from symbol_please.data import SPELL_DATA

_LOGGER = logging.getLogger(__name__)

CASTING_REGEX = re.compile(r'^You begin casting (?P<spell>.+)\.$')
INTERRUPTED_REGEX = re.compile(r"^Your spell is interrupted\.$")
DID_NOT_TAKE_HOLD_REGEX = re.compile(r"^Your spell did not take hold\.$")
LOADING_REGEX = re.compile(r"^LOADING, PLEASE WAIT\.\.\.$")

# We'll cache the regexes we use to wait for spell messages
SPELL_CAST_REGEXES = {}
SPELL_WEARS_OFF_REGEXES = {}


class SpellEvent():
    """A detected spell event."""
    __slots__ = ('instance_id', 'spell')

    def __init__(self, instance_id, spell):
        """Create a new spell effect."""
        self.instance_id = instance_id
        self.spell = spell


class SpellEventCasting(SpellEvent):
    """A spell is being cast."""


class SpellEventInterrupted(SpellEvent):
    """A spell cast was interrupted."""


class SpellEventDidNotTakeHold(SpellEvent):
    """A spell cast did not take hold."""


class SpellEventResisted(SpellEvent):
    """A spell cast was resisted."""


class SpellEventTargeted(SpellEvent):
    """A spell event with a target detected."""
    __slots__ = ('target',)

    def __init__(self, instance_id, spell, target):
        """Create a new spell effect."""
        super().__init__(instance_id, spell)
        self.target = target


class SpellEventCast(SpellEventTargeted):
    """A spell has been successfully cast."""
    __slots__ = ('cast_time', 'duration')

    def __init__(self, instance_id, spell, target, cast_time, duration):
        """Create a new spell effect."""
        super().__init__(instance_id, spell, target)
        self.cast_time = cast_time
        self.duration = duration


class SpellEventExpired(SpellEventTargeted):
    """A spell effect has expired."""


class LineListener():
    """A regex log listener."""

    def __init__(self, name, pattern):
        """Create the listener."""
        self.name = name
        self.pattern = pattern
        self.line = None
        self.match = None

    def check_line(self, line):
        """Check if the given line matches."""
        _LOGGER.debug("Pattern %s", self.pattern)
        self.match = self.pattern.match(line.message)
        if self.match is not None:
            self.line = line
            return True
        return False


class SpellEventHandler():
    """Manages tracking of spell events."""

    @classmethod
    def create_events(cls, client, line):
        """Parses every log line, and returns new events to be tracked."""
        spell_match = CASTING_REGEX.match(line.message)
        if spell_match is not None:
            spell_name = spell_match.group('spell')
            if spell_name not in SPELL_DATA:
                _LOGGER.warning("No data for spell '%s'", spell_name)
                return
            spell = SPELL_DATA[spell_name]

            if not spell['msg_cast_on_you'] and not spell['msg_cast_on_other']:
                _LOGGER.info("No trackable logging for spell '%s'", spell)
                return

            return set((cls(client, line, spell),))

    def __init__(self, client, line, spell):
        """Create a new spell effect handler."""
        self.client = client
        self.line = line
        self.spell = spell
        # Start tracking new log lines as soon as the handler is constructed
        self.line_queue = asyncio.Queue()
        # We don't need to watch for other spell events by default
        self.event_queue = None

    def _send_event(self, event):
        """Send an event to the parser client."""
        # Pass the event up to the client
        self.client.send_event(event)

    async def _wait_for_messages(self, messages, timeout=None):
        """Wait for possible effect messages, with a given timeout."""
        listeners = tuple(
            LineListener(name, message) for name, message in messages.items())

        return await asyncio.wait_for(
            self.wait_for_listeners(listeners), timeout)

    async def wait_for_event(self, check_event):
        """Read events until a match is found."""
        if self.event_queue is None:
            self.event_queue = asyncio.Queue()
        while True:
            event = await self.event_queue.get()
            if check_event(event):
                return event

    async def wait_for_listeners(self, listeners):
        """Parse a line of input."""
        while True:
            line = await self.line_queue.get()
            for listener in listeners:
                if listener.check_line(line):
                    return listener

    async def run(self):
        """Handle the casting of a spell"""
        instance_id = self.line.line_id
        self._send_event(SpellEventCasting(instance_id, self.spell))

        if self.spell['name'] not in SPELL_CAST_REGEXES:
            # Always need to listen for interruped messages
            regexes = {
                'interrupted': INTERRUPTED_REGEX,
                'did_not_take_hold': DID_NOT_TAKE_HOLD_REGEX,
                'loading': LOADING_REGEX,
                'resisted': re.compile("^{}$".format(
                    re.escape("Your target resisted the {} spell.".format(
                        self.spell['name'])))),
            }
            if self.spell['msg_cast_on_you']:
                # Listen for the spell to effect self
                regexes['self'] = re.compile("^{}$".format(
                    re.escape(self.spell['msg_cast_on_you'])))
            if self.spell['msg_cast_on_other']:
                # Listen for the spell to effect others
                regexes['other'] = re.compile("^{}$".format(
                    re.escape(self.spell['msg_cast_on_other']).replace(
                        "Someone", r"(?P<target>.+)")))
            SPELL_CAST_REGEXES[self.spell['name']] = regexes

            # Listen for the spell to wear off
            if self.spell['msg_wears_off']:
                SPELL_WEARS_OFF_REGEXES[self.spell['name']] = {
                    'wears_off': re.compile("^{}$".format(
                        re.escape(self.spell['msg_wears_off'])))
                }
        try:
            result = await self._wait_for_messages(
                SPELL_CAST_REGEXES[self.spell['name']], 30)
        except asyncio.TimeoutError as ex:
            _LOGGER.warning("No cast result message detected for spell '%s'",
                            self.spell['name'], exc_info=ex)
            return
        if self.spell['target_type'] == 'Group':
            # Skip spell did not take hold messages if casting group spell to
            # see if it took effect on anyone
            while result.name == 'did_not_take_hold':
                try:
                    result = await self._wait_for_messages(
                        SPELL_CAST_REGEXES[self.spell['name']], 1)
                except asyncio.TimeoutError:
                    break

        if result.name == 'interrupted':
            self._send_event(SpellEventInterrupted(instance_id, self.spell))
            return

        if result.name == 'loading':
            self._send_event(SpellEventInterrupted(instance_id, self.spell))
            return

        if result.name == 'did_not_take_hold':
            self._send_event(SpellEventDidNotTakeHold(instance_id, self.spell))
            return

        if result.name == 'resisted':
            self._send_event(SpellEventResisted(instance_id, self.spell))
            return

        if self.spell['target_type'] == 'Group':
            target = 'GROUP'
        elif result.name == 'self':
            target = 'YOU'
        else:
            target = result.match.group('target')

        cast_time = datetime.datetime.now()
        duration = self._calculate_duration()

        self._send_event(SpellEventCast(
            instance_id, self.spell, target, cast_time, duration))

        if duration is None:
            return

        _LOGGER.info("Spell in effect: '%s'", self.spell['name'])

        def check_event(event):
            """Callback to check for spell replacement event."""
            if not isinstance(event, SpellEventCast):
                return False
            if event.spell['name'] != self.spell['name']:
                return False
            if event.instance_id == instance_id:
                return False
            if event.target != target:
                return False
            return True

        wait_for_event = self.wait_for_event(check_event)
        if target == 'YOU' and self.spell['name'] in SPELL_WEARS_OFF_REGEXES:
            wait_for_messages = self._wait_for_messages(
                SPELL_WEARS_OFF_REGEXES[self.spell['name']])
            done, pending = await asyncio.wait(
                (wait_for_messages, wait_for_event),
                timeout=duration, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                # Cancel tasks that didn't finish first
                task.cancel()
        else:
            try:
                await asyncio.wait_for(wait_for_event, duration)
            except asyncio.TimeoutError:
                pass
        _LOGGER.info("Spell expired: '%s'", self.spell['name'])

        self._send_event(SpellEventExpired(instance_id, self.spell, target))

    def _calculate_duration(self):
        """Calculate the duration for a spell cast."""
        duration = self.spell['duration']
        if not isinstance(duration, dict):
            return duration

        minlevel = duration['start']['level']
        maxlevel = duration['end']['level']
        minduration = duration['start']['duration']
        maxduration = duration['end']['duration']
        if self.client.level <= minlevel:
            return minduration
        if self.client.level >= maxlevel:
            return maxduration

        # Interpolate
        fraction = (self.client.level - minlevel) / (maxlevel - minlevel)
        return ((maxduration - minduration) * fraction) + minduration
