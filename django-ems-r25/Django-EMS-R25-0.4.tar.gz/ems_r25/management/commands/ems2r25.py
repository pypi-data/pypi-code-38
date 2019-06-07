import datetime
import logging
import re

from dateutil.parser import parse
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from ems_client.models import Status
from ems_client.service import Service
from restclients_core.exceptions import DataFailureException
from urllib3.exceptions import HTTPError
from uw_r25.events import get_event_by_alien_id, get_event_by_id
from uw_r25.models import Event, Reservation, Space

from ems_r25.more_r25 import (delete_event, update_event,
                              R25MessageException, R25ErrorException)
from ems_r25.utils import update_get_space_ids


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'adds or updates R25 events with events from EMS'

    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            '--start',
            help="Start of date range. Default is today, or yesterday if "
                 "using --changed.",
        )
        parser.add_argument(
            '-e',
            '--end',
            help="End of date range. Default is START+7 days, or today if "
                 "using --changed.",
        )

        parser.add_argument(
            '-c',
            '--changed',
            action='store_true',
            help="Get Bookings that have changed within date range. Includes "
                 "Bookings where the Reservation has changed, even if the "
                 "Booking has not.",
        )

        parser.add_argument(
            '-d',
            '--delete',
            action='store_true',
            help='Delete matched R25 Events',
        )

        parser.add_argument(
            '-u',
            '--update',
            action='store_true',
            help='Update R25 Events',
        )

    def handle(self, *args, **options):
        if options['changed']:
            if options['start']:
                start_date = parse(options['start']).date()
            else:
                start_date = datetime.date.today()
            if options['end']:
                end_date = parse(options['end']).date()
            else:
                end_date = datetime.date.today()

        else:
            if options['start']:
                start_date = parse(options['start']).date()
            else:
                start_date = datetime.date.today()
            if options['end']:
                end_date = parse(options['end']).date()
            else:
                end_date = start_date + datetime.timedelta(days=7)

        _ems = Service()

        space_ids = update_get_space_ids(_ems.get_all_rooms())

        status_list = _ems.get_statuses()
        statuses = {}
        search_statuses = []
        for status in status_list:
            statuses[status.id] = status
            if status.description not in settings.EMS_R25_IGNORE_STATUSES:
                search_statuses.append(status.id)

        # Get all bookings in range, regardless of room, status, or event type.
        # We do this because a now-unwanted booking might already have been
        # Created in R25, and we need to cancel it there.
        bookings = _ems.get_changed_bookings(
            start_date=start_date.isoformat(), end_date=end_date.isoformat(),
            statuses=search_statuses
        ) if options['changed'] else _ems.get_bookings(
            start_date=start_date.isoformat(), end_date=end_date.isoformat(),
            statuses=search_statuses
        )

        ems_reservations = {}
        for booking in bookings:
            if options['changed']:
                # Booking hasn't changed, EMS Reservation has...
                if (booking.date_changed.date() < start_date or
                        booking.date_changed.date() > end_date):
                    continue

            booking.status = statuses[booking.status_id]

            if booking.reservation_id not in ems_reservations:
                # Use data from first booking as reservation data.
                # FIXME: we need a way to grab actual EMS Reservation data
                # FIXME: instead of just Bookings
                ems_reservations[booking.reservation_id] = booking
                ems_reservations[booking.reservation_id].bookings = {}
            ems_reservations[
                booking.reservation_id].bookings[booking.id] = booking

        for ems_res_id in ems_reservations:
            ems_reservation = ems_reservations[ems_res_id]
            logger.info("Processing EMS Reservation %d" % ems_res_id)

            # alien_uid is how we tie EMS Reservation to R25 Event.
            r25_alien_uid = "AT_EMS_RSRV_%s" % ems_res_id

            r25_event = None
            try:
                r25_event = get_event_by_alien_id(r25_alien_uid)
                logger.debug("\tFound R25 event %s: '%s'" %
                             (r25_event.event_id, r25_event.name))

            except DataFailureException:
                # No R25 event matching this EMS event
                pass

            if options['delete']:
                if r25_event:
                    logger.debug("\tDeleting!")
                    delete_event(r25_event.event_id)
                else:
                    logger.debug("\tNothing to delete.")
                continue

            if r25_event is None:
                r25_event = Event()
                r25_event.alien_uid = r25_alien_uid
                r25_event.reservations = []

            r25_event.name = ems_reservation.event_name[:40].strip()
            r25_event.title = ems_reservation.event_name.strip()
            r25_event.state = r25_event.CONFIRMED_STATE

            ems_bookings = ems_reservation.bookings
            for ems_bk_id in ems_bookings:
                ems_booking = ems_bookings[ems_bk_id]

                logger.debug("\tProcessing EMS Booking %d: '%s'" %
                             (ems_bk_id, ems_booking.event_name))
                logger.debug("\t\tStatus: %s, space_id: %s" % (
                             (ems_booking.status.description,
                              space_ids.get(ems_booking.room_id))))
                logger.debug("\t\tStart: %s, End: %s, Changed: %s" % (
                    ems_booking.time_booking_start.isoformat(),
                    ems_booking.time_booking_end.isoformat(),
                    ems_booking.date_changed.isoformat()))

                # profile_name is how we tie EMS Booking to R25 Reservation.
                # We only use the most basic type of profile, so profile to
                # reservation is a 1:1 relationship.
                r25_profile_name = "AT_EMS_BOOK_%s" % ems_bk_id

                r25_res = None
                for r in r25_event.reservations:
                    if r.profile_name == r25_profile_name:
                        logger.debug(
                            "\t\tFound R25 reservation/profile %s: '%s'" %
                            (r.reservation_id, r.profile_name))
                        logger.debug(
                            "\t\t\tState: %s, Space Reservation: %s" %
                            (r.state_name(),
                             r.space_reservation.space_id if
                             r.space_reservation else ''))
                        r25_res = r
                        break

                # does this Booking belong in R25?
                if (ems_booking.status_type_id ==
                        Status.STATUS_TYPE_BOOKED_SPACE and
                        ems_booking.room_id in space_ids and
                        ems_booking.status.description not in
                        settings.EMS_R25_REMOVE_STATUSES):

                    # We want a reservation. Create if necessary.
                    if r25_res is None:
                        r25_res = Reservation()
                        r25_res.profile_name = r25_profile_name
                        r25_res.space_reservation = None
                        r25_event.reservations.append(r25_res)

                    r25_res.start_datetime = \
                        ems_booking.time_booking_start.isoformat()
                    r25_res.end_datetime = \
                        ems_booking.time_booking_end.isoformat()
                    r25_res.state = r25_res.STANDARD_STATE
                    if r25_res.space_reservation is None:
                        r25_res.space_reservation = Space()

                    r25_res.space_reservation.space_id = space_ids[
                        ems_booking.room_id]

                # does not belong. Does one already exist?
                elif r25_res is not None:
                    # Cancel this unwanted r25 reservation
                    r25_res.state = r25_res.CANCELLED_STATE
                    r25_res.space_reservation = None

            # if this R25 Event is empty, there's nothing to do
            if not r25_event.reservations:
                logger.debug("\tNo existing R25 reservations and no wanted "
                             "new R25 reservations")
                continue

            # if there are no active reservations left, cancel the event
            has_active_reservations = False
            for r in r25_event.reservations:
                if r.state != r.CANCELLED_STATE:
                    has_active_reservations = True
                    break
            if not has_active_reservations:
                r25_event.state = r25_event.CANCELLED_STATE

            # by default, don't actually make changes
            if not options['update']:
                continue

            try:
                logger.debug("\tUpdating event")
                updated = update_event(r25_event)

            except R25MessageException as ex:
                while ex:
                    if ex.msg_id == 'EV_I_SPACECON':
                        logger.warning(
                            "Conflict while syncing EMS Reservation %s: %s" %
                            (ems_reservation.reservation_id, ex.text))
                        match = re.search(r'\[(?P<event_id>\d+)\]', ex.text)
                        old_event = get_event_by_id(match.group('event_id'))
                        logger.warning(
                            "Existing event: %s" % old_event.live_url())
                        logger.warning(
                            "Is blocking event: %s" % r25_event.live_url())

                    else:
                        logger.warning(
                            "R25 message while syncing EMS Reservation %s to "
                            "R25 Event %s: %s" % (
                                ems_reservation.reservation_id,
                                r25_event.event_id, ex))

                    ex = ex.next_msg

            except R25ErrorException as ex:
                logger.warning(
                    "R25 error while syncing EMS Reservation %s to R25 Event "
                    " %s: %s" % (ems_reservation.reservation_id,
                                 r25_event.event_id, ex))

            except HTTPError as ex:
                logger.warning(
                    "HTTP error while syncing EMS Reservation %s to R25 Event "
                    " %s: %s" % (ems_reservation.reservation_id,
                                 r25_event.event_id, ex))
