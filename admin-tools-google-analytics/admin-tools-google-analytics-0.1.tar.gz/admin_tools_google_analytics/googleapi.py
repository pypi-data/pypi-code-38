""" 
    Код позаимствован из официального примера[1] с небольшими модификациями. 
    [1] : https://developers.google.com/analytics/devguides/reporting/core/v3/quickstart/service-py?hl=ru
"""

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


from django.conf import settings


def get_service(api_name, api_version, scopes, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        key_file_location, scopes=scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=credentials)

    return service


def get_first_profile_id(service):
    # Use the Analytics service object to get the first profile id.

    # Get a list of all Google Analytics accounts for this user
    accounts = service.management().accounts().list().execute()

    if accounts.get('items'):
        # Get the first Google Analytics account.
        account = accounts.get('items')[0].get('id')

        # Get a list of all the properties for the first account.
        properties = service.management().webproperties().list(
            accountId=account).execute()

        if properties.get('items'):
            # Get the first property id.
            property = properties.get('items')[0].get('id')

            # Get a list of all views (profiles) for the first property.
            profiles = service.management().profiles().list(
                accountId=account,
                webPropertyId=property).execute()

            if profiles.get('items'):
                # return the first view (profile) id.
                return profiles.get('items')[0].get('id')

    return None


def get_data(metrics, start_date, end_date):
    service = get_service(
        api_name='analytics',
        api_version='v3',
        scopes=['https://www.googleapis.com/auth/analytics.readonly', ],
        key_file_location=settings.GOOGLE_ANALYTICS_KEY_FILE)

    profile_id = get_first_profile_id(service)

    return service.data().ga().get(
        ids='ga:' + profile_id,
        start_date=start_date,
        end_date=end_date,
        metrics=metrics,
        dimensions='ga:date').execute()['rows']


def get_visitors(start_date='6daysAgo', end_date='today'):
    data = get_data(metrics='ga:pageviews',
                    start_date=start_date, end_date=end_date)
    dates, pageviews = [], []
    for date, pageview in data:
        # datae = int("YYYYMMDD")
        dates.append(int(date))
        pageviews.append(int(pageview))
    return {'dates': dates, 'pageviews': pageviews}


def get_visitors_total(start_date='6daysAgo', end_date='today'):
    data = get_data(metrics='ga:users,ga:sessions,ga:pageviews',
                    start_date=start_date, end_date=end_date)
    users, sessions, views = 0, 0, 0
    print(data)

    return {'users': users, 'sessions': sessions, 'views': views}
