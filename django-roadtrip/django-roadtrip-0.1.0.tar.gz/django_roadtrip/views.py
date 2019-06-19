from django.core.exceptions import ObjectDoesNotExist
from django.templatetags.static import static
from django.views.generic import TemplateView
from .models import RoadTripProfile, RoadTrip


def get_default_profile():
    return RoadTripProfile.objects.first()


class ProfileView(TemplateView):
    template_name = "roadtrip/profile.html"

    def get(self, request, profile_username=None, *args, **kwargs):

        if profile_username:
            try:
                profile = RoadTripProfile.objects.get(user__username=profile_username)
            except ObjectDoesNotExist:
                self.template_name = 'road-trip/error.html'
                return self.render_to_response({'error': "Profil inexistant : {}".format(profile_username)})
        else:
            profile = get_default_profile()

        context = self.get_context_data()
        context['profile'] = profile
        context['road_trips'] = profile.roadtrips.all()

        return self.render_to_response(context)


class IndexView(ProfileView):
    pass # template_name = "roadtrip/index.html"


class RoadTripView(TemplateView):
    template_name = "roadtrip/roadtrip.html"

    def __init__(self):
        super().__init__()

        self.roadtrip = None
        self.events = []

    def get_event_data(self, event):
        data = {
            'date': event.date,
            'type': event.type,
            'mileage': event.mileage,
            'location': event.location,
            'lat': event.lat,
            'lon': event.lon,
        }

        return data

    def get_events_context(self):
        """
        Get the events context of the instance roadtrip
        :return:
        """
        context = dict()
        context['events'] = []
        for data in self.roadtrip.events.order_by('date', 'mileage').all():
            if data.lat == 0 and data.lon == 0 or data.type != "Carburant" and data.type != "Sommeil":
                context['events'].append(self.get_event_data(data))
        return context

    def get_fuel_context(self):
        """
        Get the fuel context
        :return:
        """
        context = dict()

        context['refuels'] = []

        total_price = 0
        total_amount = 0
        total_mileage = self.calculate_total_mileage()
        vehicles = []

        for event in self.events:
            if event.type == "Carburant":
                data = event.refuelevent
                total_price += data.price
                total_amount += data.amount

                if data.vehicle not in vehicles:
                    vehicles.append(data.vehicle)

                data.style_width_percent = round(data.amount * 100 / data.vehicle.tank_capacity, ndigits=2)
                context['refuels'].append(data)

        context['fuel_data'] = {
            'total_price': total_price,
            'total_amount': total_amount,
            'consumption_per_100': total_amount * 100 / total_mileage,
            'price_per_100': total_price * 100 / total_mileage,
            'main_vehicle': None if not vehicles else vehicles[0],
        }

        return context

    def get_map_marker(self, event):
        """
        Create a marker to display to the map
        :param event:
        :return:
        """

        icon = 'markerIcon'

        if event.type == "Carburant":
            icon = 'fuelIcon'
        elif event.type == "Sommeil":
            icon = 'sleepIcon'

        marker = {
            'lat': event.lat,
            'lng': event.lon,
            'options': {
                'icon': icon,
                'alt': event.type
            },
        }
        return marker

    def get_map_context(self):
        """
        Get the map context of the instance roadtrip
        :return:
        """
        context = dict()

        if self.roadtrip.slug == 'finlande-2016':
            context['gpx_url'] = '/blog/file/voyages/2016-road-trip/roadmap.gpx'

        context['include_map'] = True

        context['map_markers'] = []
        for event in self.events:
            if event.lat != 0 and event.lon != 0:
                context['map_markers'].append(self.get_map_marker(event))

        context['map_options'] = {
            'icons': {
                'startIcon': {
                    'iconUrl': static('icons/flag_flyaway_green.png'),
                    'iconSize': [32, 32],
                    'iconAnchor': [5, 31],
                },
                'endIcon': {
                    'iconUrl': static('icons/flag_finish.png'),
                    'iconSize': [32, 32],
                    'iconAnchor': [5, 31],
                },
                'markerIcon': {
                    'iconUrl': static('icons/flag_flyaway_pointed.png'),
                    'iconSize': [32, 32],
                },
                'fuelIcon': {
                    'iconUrl': static('icons/gas.png'),
                    'iconSize': [40, 40]
                },
                'sleepIcon': {
                    'iconUrl': static('icons/bed.png'),
                    'iconSize': [40, 40]
                }
            }
        }

        return context

    def calculate_total_mileage(self):
        """
        Calculate the total mileage of the instance roadtrip
        :return:
        """
        mileage = 0

        if self.roadtrip.mileage_end:
            mileage = self.roadtrip.mileage_end - self.roadtrip.mileage_start
        else:
            last_events = self.roadtrip.events.filter(mileage__isnull=False)
            if last_events.exists():
                event = last_events.order_by('mileage').last()
                mileage = event.mileage - self.roadtrip.mileage_start

        return mileage

    def get(self, request, roadtrip_slug, *args, **kwargs):
        context = self.get_context_data()

        self.roadtrip = RoadTrip.objects.get(slug=roadtrip_slug)
        self.events = self.roadtrip.events.order_by('date', 'mileage').all()

        context['roadtrip'] = self.roadtrip
        context['total_mileage'] = self.calculate_total_mileage()

        context = {
            **context,
            **self.get_map_context(),
            **self.get_events_context(),
            **self.get_fuel_context()
        }

        return self.render_to_response(context)
