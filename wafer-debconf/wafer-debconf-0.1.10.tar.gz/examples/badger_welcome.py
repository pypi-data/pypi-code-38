# -*- coding: utf-8 -*-
from collections import namedtuple

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template import Context, engines

from dc17.models import Accomm, Attendee, Food


SUBJECT = "Welcome to DebConf17! (arrival details)"

TEMPLATE = """\
Dear {{ name }},

Welcome to DebConf17, hosted at the Collège de Maisonneuve in Montreal, Canada.
We're delighted that you decided to join us for what we hope will be one of the
best DebConfs yet.

Please read the contents of this mail, and the attached PDF, carefully, as it
contains important information related to your travel and visit to Montreal.

== Before departing for Montreal ==

Print this e-mail and the attached PDF which also includes a venue map.

In case of any problems (including delays or cancellation), please contact
<registration@debconf.org> as soon as possible, or if you are already
travelling, phone or SMS the Front Desk at +1 514-316-7065 (use this number
sparingly after-hours Eastern time).

Check your data, and report any errors and changes as soon as possible to
<registration@debconf.org>:

Arriving: {{ attendee.arrival|date:"DATETIME_FORMAT" }}
Departing: {{ attendee.departure|date:"DATETIME_FORMAT" }}{% if food %}
Meals requested:{% for day in meals %}
{{ day.date|date:"SHORT_DATE_FORMAT" }}: {{ day.meals|join:", "|title }}{% endfor %}
Diet: {{ food.diet|default:"Whatever is provided" }}{% if food.special_diet %}
Details: {{ food.special_diet }}{% endif %}{% else %}
No conference-organised food requested.{% endif %}

Familiarize yourself with the Codes of Conduct for both Debian [1] and DebConf
[2].  If you are harassed, or observe harassment, you can contact
<antiharassment@debian.org> or members of the local anti-harassment team who
are recognizable with pink conference badges.  For any other kind of problem,
the Front Desk and Organisation team may be of help.

[1] http://debconf.org/codeofconduct.shtml
[2] https://www.debian.org/code_of_conduct

Check your travel documents.  Will your passport remain valid for the duration
of your stay?  Do you have all necessary travel authorizations such as an eTA
or visa?  If are used to visiting Canada without a visa and haven't in the last
6 months, you may be unaware of the new eTA system.  You should check if you
need an eTA, and apply online ASAP:

https://travel.gc.ca/returning/customs/entering-canada

Notify your bank that you'll be travelling to Canada to avoid having your
card(s) blocked.

Do you have travel insurance?  This could be important should you become in
need of medical attention, as the Canadian public health insurance system does
not cover travellers.  Be sure to also check with your provider if you're
covered in case of lost or stolen items, such as electronics and computer
devices.

Note that cheese may be imported but duty may be charged if the total product
value exceeds 20 CAD.  For alcohol, the permitted allowance is 1,5L of wine and
up to 8,5L of beer.  This information might be relevant to your (optional)
contribution to the Cheese and Wine party.

== Your Accommodation Details ==
{% if not accomm %}
You have not requested any conference-provided accommodation.  Remember to
print the details of your accommodation in case you're asked by immigration
officials.{% endif %}{% if stays.onsite %}

=== On-site accommodation ===

According to our records, you're registered to stay on-site on the following
days:

Check-in: {{ stays.onsite.checkin|date }}
Checkout: {{ stays.onsite.checkout|date }}
Room: {{ accomm.onsite_room }}

No bed sheets, blanket, or duvet are provided, only a cot and pillow.  You will
need to bring a sleeping bag, blanket and pillowcase.  Lockers will be
available on the venue to store your valuables, so bring also a padlock or
combination lock.  Don't forget to bring any showering items you might need:
bath towel, facecloth, soap, shampoo and the like.  You'll be sharing a room
with others, so if you're sensitive to noise when sleeping, consider bringing
earplugs.

https://wiki.debconf.org/wiki/DebConf17/Accommodation#On-site{% endif %}{% if stays.rvc %}

=== McGill Royal Victoria College Residence ===

According to our records, you're registered at RVC on the following days:

Check-in: {{ stays.rvc.checkin|date }}
Checkout: {{ stays.rvc.checkout|date }}
Room: {{ accomm.rvc_room }}

Bed sheets and a pillow are provided, as are showering necessities such as a
towel, soap and shampoo.

https://wiki.debconf.org/wiki/DebConf17/Accommodation#McGill_Royal_Victoria_College_Residence{% endif %}{% if stays.hotel %}

=== Hôtel Universel Montréal ===

According to our records, you're registered at the Hotel on the following days:

Check-in: {{ stays.hotel.checkin|date }}
Checkout: {{ stays.hotel.checkout|date }}

Refer to the hotel front desk for details.

https://wiki.debconf.org/wiki/DebConf17/Accommodation#Hotel_Universel{% endif %}

== What to Bring ==

An international adapter (if required) and power supplies for all your devices.

Light clothes.  It's summer in Montreal, and the days are warm and often humid.
The daily maximums range from 22 to 30°C, while nights usually drop to around
15 to 18°C.  The conference venue will be air conditioned so depending on the
outdoor conditions and the number of people in the venue, the indoor
temperature could get relatively cold so do also bring along a couple of warmer
clothing items such as a hoodie.  It will rain from time to time so a raincoat
and/or umbrella will be useful.  Don't forget a reusable water bootle and
sunscreen if you plan to enjoy the outdoors.

An Ethernet cable is always useful to have, if we have WiFi trouble.  WiFi
should be available in every area we use on the campus.

Printed PGP/GPG fingerprint slips, if you want to have your key signed by other
peers.

== Airport Arrival ==

=== Public Transit (747 bus) ===

See page 3 of the attached PDF.

=== Taxis ===

Upon exiting the border control check zone and arriving in the part of the
airport open to the public, look for the taxi signs.  Follow them outside and
the taxis should be there.

The taxi fare from the airport to downtown Montreal is priced at a fixed 40
CAD.  It might cost you more to get to the venue, since it is about 5km east of
the downtown area.  You can simply hail for a cab at the airport.  Uber is also
available.

Ask them to drop you off at Collège de Maisonneuve.  The address is 3800
Sherbrooke Est.  Once inside, look for the signs showing you the way to the
front desk!

== Front Desk location ==

The Front Desk is located on the second floor, in the main hall.  Look for a
windowed room with DebConf signs.  If you're arriving late (after 22:00) and
Front Desk is closed, there will be a volunteer stationed at the Nicolet
entrance who will help you get into your designated dorm.  If you're arriving
very late (after 3am) you'll need to go through the 3800 Sherbrooke entrance
and use the buzzer to call a security guard to open the door for you.  In case
of problems, the Front Desk may be reached at +1 514-316-7065.

Have a safe trip.  We look forward to seeing you in Montréal.

The DebConf Team
"""

Stay = namedtuple('Stay', ('checkin', 'checkout'))
Meal = namedtuple('Meal', ('date', 'meals'))


def meal_sort(meal):
    return ['breakfast', 'lunch', 'dinner'].index(meal)


class Command(BaseCommand):
    help = 'Send welcome emails'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something'),
        parser.add_argument('--username',
                            help='Send mail to a specific user, only'),

    def badger(self, attendee, dry_run):
        name = attendee.user.userprofile.display_name()
        to = attendee.user.email

        try:
            accomm = attendee.accomm
        except Accomm.DoesNotExist:
            accomm = None

        try:
            food = attendee.food
        except Food.DoesNotExist:
            food = None

        stays = {}
        if accomm:
            stay_details = attendee.accomm.get_stay_details()
            for checkin, checkout, alt_accomm in stay_details:
                venue = {
                    '': 'onsite',
                    'hotel': 'hotel',
                    'rvc_single': 'rvc',
                    'rvc_double': 'rvc',
                }[alt_accomm]
                stays[venue] = Stay(checkin, checkout)

        meals = []
        if food:
            by_day = {}
            for meal in food.meals.all():
                by_day.setdefault(meal.date, []).append(meal.meal)
            for date, days_meals in sorted(by_day.items()):
                meals.append(Meal(date, sorted(days_meals, key=meal_sort)))

        ctx = {
            'accomm': accomm,
            'attendee': attendee,
            'food': food,
            'meals': meals,
            'name': name,
            'stays': stays,
        }

        template = engines['django'].from_string(TEMPLATE)
        body = template.render(Context(ctx))

        if dry_run:
            print('Would badger %s <%s>' % (name, to))
            return

        attachments = []
        if (settings.EMAIL_BACKEND !=
                'django.core.mail.backends.console.EmailBackend'):
            attachments.append(
                ('DebConf17-arrival.pdf', self.attachment, 'application/pdf'))

        email_message = EmailMultiAlternatives(
            SUBJECT, body, to=["%s <%s>" % (name, to)],
            attachments=attachments)
        email_message.send()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')

        with open('assets/docs/welcome.pdf', 'rb') as f:
            self.attachment = f.read()

        queryset = Attendee.objects.filter(reconfirm=True)
        if options['username']:
            queryset = queryset.filter(user__username=options['username'])

        for attendee in queryset:
            self.badger(attendee, dry_run)
