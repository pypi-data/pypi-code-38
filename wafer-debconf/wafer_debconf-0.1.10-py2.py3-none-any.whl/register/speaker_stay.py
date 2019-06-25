from register.models import Attendee
from wafer.schedule.admin import register_schedule_item_validator
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as N_


def validate_speaker_stay(all_items):
    errors = []
    for item in all_items:
        if not item.talk:
            continue
        for speaker in item.talk.authors.all():
            try:
                attendee = speaker.attendee
            except Attendee.DoesNotExist:
                continue
            for slot in item.slots.all():
                if not slot.day:
                   continue
                arrival = attendee.arrival
                if arrival and slot.day.date < arrival.date():
                    errors.append(
                        _('<%(talk)s> scheduled %(scheduled)s; %(speaker)s arrives %(arrival)s') % {
                            'talk': item.talk.title,
                            'speaker': speaker.get_full_name(),
                            'scheduled': slot.day.date,
                            'arrival': arrival,
                        }
                    )
                    break
                departure = attendee.departure
                if departure and slot.day.date > departure.date():
                    errors.append(
                        _('<%(talk)s> scheduled for %(scheduled)s; %(speaker)s departs %(departure)s') % {
                            'talk': item.talk.title,
                            'speaker': speaker.get_full_name(),
                            'scheduled': slot.day.date,
                            'departure': departure,
                        }
                    )
                    break
    return errors


register_schedule_item_validator(
    validate_speaker_stay,
    'speaker_not_at_conference',
    N_('Talk scheduled when speaker is not at the conference')
)
