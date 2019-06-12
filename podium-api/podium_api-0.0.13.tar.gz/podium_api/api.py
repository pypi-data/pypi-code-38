from podium_api.account import make_account_get
from podium_api.events import (
    make_events_get, make_event_create, make_event_get, make_event_delete,
    make_event_update
    )
from podium_api.devices import (
    make_device_get, make_device_create, make_device_update,
    make_device_delete, make_devices_get
    )
from podium_api.friendships import (
    make_friendship_get, make_friendships_get, make_friendship_create,
    make_friendship_delete
    )
from podium_api.users import make_user_get
from podium_api.eventdevices import (
    make_eventdevices_get, make_eventdevice_create, make_eventdevice_update,
    make_eventdevice_get, make_eventdevice_delete
)
from podium_api.alertmessages import (
    make_alertmessages_get, make_alertmessage_get, make_alertmessage_create
    )

from podium_api.venues import (
    make_venues_get, make_venue_get
    )
from podium_api.laps import make_laps_get, make_lap_get


class PodiumAPI(object):
    """
    The PodiumApi object holds references to the interfaces to the
    various asynchronous requests. You should provide a PodiumToken received
    from **podium_api.login.make_login_post** to create this object.

    Keep in mind all API requests are asynchronous, you need to provide
    callback functions that will receive the data once the request has
    completed. Most requests return their results in the on_success callback,
    but some creation requests return their success as a redirect to the
    newly created resource's URI. Reference the documentation for each
    function for more details.

    **Attributes:**
        **token** (PodiumToken): The token for the logged in user.

        **account** (PodiumAccountAPI): API object for account requests.

        **events** (PodiumEventsAPI): API object for event requests.

        **devices** (PodiumDevicesAPI): API object for device requests.

        **friendships** (PodiumFriendshipsAPI): API object for friendship
        requests.

        **users** (PodiumUsersApi): API object for user requests.

        **eventdevices** (PodiumEventDevicesAPI): API object for event-device
        requests.

        **laps** (PodiumLapsAPI): API object for lap requests.
        
        **alertmessages** (AlertMessagesAPI: API object for alertmessage requests.

    """

    def __init__(self, token):
        self.token = token
        self.account = PodiumAccountAPI(token)
        self.events = PodiumEventsAPI(token)
        self.devices = PodiumDevicesAPI(token)
        self.friendships = PodiumFriendshipsAPI(token)
        self.users = PodiumUsersAPI(token)
        self.eventdevices = PodiumEventDevicesAPI(token)
        self.laps = PodiumLapsAPI(token)
        self.alertmessages = PodiumAlertMessagesAPI(token)


class PodiumLapsAPI(object):
    """
    Object that handles lap requests and keeps track of the
    authentication token necessary to do so. Usually accessed via
    PodiumAPI object.

    **Attributes:**
        **token** (PodiumToken): The token for the logged in user.

    """
    def __init__(self, token):
        self.token = token

    def list(self, *args, **kwargs):
        """
        Request that returns a PodiumPagedRequest of laps.

        Args:
            endpoint (str): The endpoint to make the request too.

        Kwargs:
            expand (bool): Expand all objects in response output.
            Defaults to True

            quiet (object): If not None HTML layout will not render endpoint
            description. Defaults to None.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(PodiumPagedResponse)
            Defaults to None.

            failure_callback (function): Callback for failures and errors.
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect,
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

            start (int): Starting index for events list. 0 indexed.

            per_page (int): Number per page of results, max of 100.

        Return:
            UrlRequest: The request being made.

        """
        make_laps_get(self.token, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
       Request that returns a PodiumLap that represents a specific
       lap found at the URI.

       Args:
           endpoint (str): The URI for the lap.

       Kwargs:
           expand (bool): Expand all objects in response output.
           Defaults to True

           quiet (object): If not None HTML layout will not render endpoint
           description. Defaults to None.

           success_callback (function): Callback for a successful request,
           will have the signature:
               on_success(PodiumLap)
           Defaults to None.

           failure_callback (function): Callback for failures and errors.
           Will have the signature:
               on_failure(failure_type (string), result (dict), data (dict))
           Values for failure type are: 'error', 'failure'. Defaults to None.

           redirect_callback (function): Callback for redirect,
           Will have the signature:
               on_redirect(result (dict), data (dict))
           Defaults to None.

           progress_callback (function): Callback for progress updates,
           will have the signature:
               on_progress(current_size (int), total_size (int), data (dict))
           Defaults to None.

       Return:
           UrlRequest: The request being made.

       """
        make_lap_get(self.token, *args, **kwargs)


class PodiumEventDevicesAPI(object):
    """
    Object that handles event-device requests and keeps track of the
    authentication token necessary to do so. Usually accessed via
    PodiumAPI object.

    **Attributes:**
        **token** (PodiumToken): The token for the logged in user.

    """
    def __init__(self, token):
        self.token = token

    def list(self, *args, **kwargs):
        """
        Request that returns a PodiumPagedRequest of events.
        By default a get request to
        'https://podium.live/api/v1/events/{event_id}/devices' will be made.

        Kwargs:
            expand (bool): Expand all objects in response output.
            Defaults to True

            quiet (object): If not None HTML layout will not render endpoint
            description. Defaults to None.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(PodiumPagedResponse)
            Defaults to None.

            failure_callback (function): Callback for failures and errors.
            Will have the signature:
                on_failure(failure_type (string), result (dict),
                           data (dict))
            Values for failure type are: 'error', 'failure'.
            Defaults to None.

            redirect_callback (function): Callback for redirect,
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int),
                            data (dict))
            Defaults to None.

            start (int): Starting index for events list. 0 indexed.

            per_page (int): Number per page of results, max of 100.

            endpoint (str): If provided this endpoint will be used instead
            of the default:
            'https://podium.live/api/v1/events/{event_id}/devices'

            event_id (int): If an endpoint is not provided you should
            provide the id of the event for which you want to look up
            the devices.

        Return:
            UrlRequest: The request being made.

        """
        make_eventdevices_get(self.token, *args, **kwargs)

    def create(self, *args, **kwargs):
        """
        Request that creates a new PodiumEventDevice.

        The uri for the newly created event device will be provided to the
        redirect_callback if one is provided in the form of a PodiumRedirect.

        Args:
            event_id (int): Id of the event to add the device to.

            device_id (int): Id of the device to add to the event.

            name (str): Name of the device for this particular event, allows for
            car number/name to change between events. If blank/missing, will
            default to device name.

        Kwargs:
            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(result (dict), data (dict))
            Defaults to None..

            failure_callback (function): Callback for failures and errors.
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect,
            Will have the signature:
                on_redirect(redirect_object (PodiumRedirect))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_eventdevice_create(self.token, *args, **kwargs)

    def update(self, *args, **kwargs):
        """
        Request that updates a PodiumEventDevice.

        Args:
            eventdevice_uri (str): URI for the eventdevice you are updating.

        Kwargs:
            name (str): Name of the device for this particular event, allows for
            car number/name to change between events. If blank/missing, will
            default to device name.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(result (dict), updated_uri (str))
            Defaults to None..

            failure_callback (function): Callback for failures and errors.
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect,
            Will have the signature:
                on_redirect(redirect_object (PodiumRedirect))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_eventdevice_update(self.token, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Request that returns a PodiumEventDevice for the provided
        eventdevice_uri

        Args:
            eventdevice_uri (str): URI for the eventdevice you want.

        Kwargs:

            expand (bool): Expand all objects in response output.
            Defaults to True

            quiet (object): If not None HTML layout will not render endpoint
            description. Defaults to None.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(PodiumEvent)
            Defaults to None.

            failure_callback (function): Callback for failures and errors.
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect,
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_eventdevice_get(self.token, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Deletes the device for the provided URI.

        Args:
            eventdevice_uri (str): URI for the eventdevice you want.

        Kwargs:
            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(deleted_uri (str))
            Defaults to None.

            failure_callback (function): Callback for failures and errors.
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect,
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_eventdevice_delete(self.token, *args, **kwargs)


class PodiumUsersAPI(object):
    """
    Object that handles user requests and keeps track of the
    authentication token necessary to do so. Usually accessed via
    PodiumAPI object.

    **Attributes:**
        **token** (PodiumToken): The token for the logged in user.

    """

    def __init__(self, token):
        self.token = token

    def get(self, *args, **kwargs):
        """
        Returns a PodiumUser object found at the uri provided in the endpoint
        arg.

        Args:
            endpoint (str): The URI to make the request to. Typically should be
            provided by some api object.

        Kwargs:
            expand (bool): Expand all objects in response output.
            Defaults to False

            quiet (object): If not None HTML layout will not render endpoint
            description. Defaults to None.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(token (string))
            Defaults to None.

            failure_callback (function): Callback for redirects, failures, and
            errors. Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'redirect', 'failure'.
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_user_get(self.token, *args, **kwargs)


class PodiumFriendshipsAPI(object):
    """
    Object that handles friendship requests and keeps track of the
    authentication token necessary to do so. Usually accessed via
    PodiumAPI object.

    **Attributes:**
        **token** (PodiumToken): The token for the logged in user.

    """

    def __init__(self, token):
        self.token = token

    def get(self, *args, **kwargs):
        """
        Request that returns a PodiumFriendship that represents a specific
        friendship found at the URI.

        Args:
            endpoint (str): The URI for the friendship.

        Kwargs:
            expand (bool): Expand all objects in response output.
            Defaults to True

            quiet (object): If not None HTML layout will not render endpoint
            description. Defaults to None.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(PodiumPagedResponse)
            Defaults to None.

            failure_callback (function): Callback for failures and errors.
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect,
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_friendship_get(self.token, *args, **kwargs)

    def list(self, *args, **kwargs):
        """
        Request that returns a PodiumPagedRequest of friendships.

        Args:
            endpoint (str): The endpoint to make the request too.

        Kwargs:
            expand (bool): Expand all objects in response output.
            Defaults to True

            quiet (object): If not None HTML layout will not render endpoint
            description. Defaults to None.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(PodiumPagedResponse)
            Defaults to None.

            failure_callback (function): Callback for failures and errors.
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect,
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

            start (int): Starting index for events list. 0 indexed.

            per_page (int): Number per page of results, max of 100.

        Return:
            UrlRequest: The request being made.

        """
        make_friendships_get(self.token, *args, **kwargs)

    def create(self, *args, **kwargs):
        """
        Request that adds a friendship for the user whose token is in use.

        The uri for the newly created event will be provided to the
        redirect_callback if one is provided in the form of a PodiumRedirect.

        Kwargs:
            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(result (dict), data (dict))
            Defaults to None..

            failure_callback (function): Callback for failures and errors.
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect,
            Will have the signature:
                on_redirect(redirect_object (PodiumRedirect))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_friendship_create(self.token, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Deletes the friendship for the provided URI.

        Args:
            friendship_uri (str): URI for the friendship you want to delete.

        Kwargs:
            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(deleted_uri (str))
            Defaults to None.

            failure_callback (function): Callback for failures and errors.
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect,
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_friendship_delete(self.token, *args, **kwargs)


class PodiumAccountAPI(object):
    """
    Object that handles account requests and keeps track of the
    authentication token necessary to do so. Usually accessed via
    PodiumAPI object.

    **Attributes:**
        **token** (PodiumToken): The token for the logged in user.

    """

    def __init__(self, token):
        self.token = token

    def get(self, *args, **kwargs):
        """
        Request that returns the account for the provided authentication token.
        Hits the api/v1/account endpoint with a GET request.

        Kwargs:
            expand (bool): Expand all objects in response output.
            Defaults to False

            quiet (object): If not None HTML layout will not render endpoint
            description. Defaults to None.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(account (PodiumAccount))
            Defaults to None.

            failure_callback (function): Callback for redirects, failures, and
            errors. Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'redirect', 'failure'. 
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_account_get(self.token, *args, **kwargs)


class PodiumDevicesAPI(object):
    """
    Object that handles device requests and keeps track of the
    authentication token necessary to do so. Usually accessed via
    PodiumAPI object.

    **Attributes:**
        **token** (PodiumToken): The token for the logged in user.

    """
    def __init__(self, token):
        self.token = token

    def create(self, *args, **kwargs):
        """
        Request that creates a new PodiumDevice.

        The uri for the newly created event will be provided to the
        redirect_callback if one is provided in the form of a PodiumRedirect.

        Args:
            name(str): Name of the device.

        Kwargs:
            success_callback (function): Callback for a successful request,
            will have the signature: 
                on_success(result (dict), data (dict))
            Defaults to None..

            failure_callback (function): Callback for failures and errors. 
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect, 
            Will have the signature:
                on_redirect(redirect_object (PodiumRedirect))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_device_create(self.token, *args, **kwargs)

    def update(self, *args, **kwargs):
        """
        Request that updates a PodiumDevice

        Args:
            device_uri (str): URI for the device you are updating.

        Kwargs:
            name(str): Name of the device.

            success_callback (function): Callback for a successful request,
            will have the signature: 
                on_success(result (dict), updated_uri (str))
            Defaults to None..

            failure_callback (function): Callback for failures and errors. 
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect, 
            Will have the signature:
                on_redirect(redirect_object (PodiumRedirect))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_device_update(self.token, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Request that returns a PodiumDevice for the provided device_uri

        Args:
            device_uri (str): URI for the device you want.

        Kwargs:
            expand (bool): Expand all objects in response output.
            Defaults to True

            quiet (object): If not None HTML layout will not render endpoint
            description. Defaults to None.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(PodiumEvent)
            Defaults to None.

            failure_callback (function): Callback for failures and errors. 
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect, 
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_device_get(self.token, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Deletes the device for the provided URI.

        Args:
            device_uri (str): URI for the device you want.

        Kwargs:
            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(deleted_uri (str))
            Defaults to None.

            failure_callback (function): Callback for failures and errors. 
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect, 
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_device_delete(self.token, *args, **kwargs)

    def list(self, *args, **kwargs):
        """
            Request that returns a PodiumPagedRequest of PodiumDevice.

            Args:
                endpoint (str): the endpoint to make the request to.

            Kwargs:
                expand (bool): Expand all objects in response output.
                Defaults to True

                quiet (object): If not None HTML layout will not render endpoint
                description. Defaults to None.

                success_callback (function): Callback for a successful request,
                will have the signature:
                    on_success(PodiumPagedResponse)
                Defaults to None.

                failure_callback (function): Callback for failures and errors.
                Will have the signature:
                    on_failure(failure_type (string), result (dict),
                               data (dict))
                Values for failure type are: 'error', 'failure'.
                Defaults to None.

                redirect_callback (function): Callback for redirect,
                Will have the signature:
                    on_redirect(result (dict), data (dict))
                Defaults to None.

                progress_callback (function): Callback for progress updates,
                will have the signature:
                    on_progress(current_size (int), total_size (int),
                                data (dict))
                Defaults to None.

                start (int): Starting index for events list. 0 indexed.

                per_page (int): Number per page of results, max of 100.

            Return:
                UrlRequest: The request being made.

            """
        make_devices_get(self.token, *args, **kwargs)


class PodiumEventsAPI(object):
    """
    Object that handles event requests and keeps track of the
    authentication token necessary to do so. Usually accessed via
    PodiumAPI object.

    **Attributes:**
        **token** (PodiumToken): The token for the logged in user.

    """

    def __init__(self, token):
        self.token = token

    def list(self, *args, **kwargs):
        """
        Request that returns a PodiumPagedRequest of events. 
        By default a get request to 
        'https://podium.live/api/v1/events' will be made.

        Kwargs:
            expand (bool): Expand all objects in response output. 
            Defaults to True

            quiet (object): If not None HTML layout will not render endpoint
            description. Defaults to None.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(PodiumPagedResponse)
            Defaults to None.

            failure_callback (function): Callback for failures and errors. 
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect, 
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

            start (int): Starting index for events list. 0 indexed.

            per_page (int): Number per page of results, max of 100.

            endpoint (str): If provided the start, per_page, expand, and quiet
            params will not be used instead making a request based on the
            provided endpoint.

        Return:
            UrlRequest: The request being made.

        """
        make_events_get(self.token, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Request that returns a PodiumEvent for the provided event_uri. 

        Args:
            event_uri (str): URI for the event you want.

        Kwargs:
            expand (bool): Expand all objects in response output.
            Defaults to True

            quiet (object): If not None HTML layout will not render endpoint
            description. Defaults to None.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(PodiumEvent)
            Defaults to None.

            failure_callback (function): Callback for failures and errors. 
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect, 
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_event_get(self.token, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Deletes the event for the provided URI.

        Args:
            event_uri (str): URI for the event you want.

        Kwargs:
            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(deleted_uri (str))
            Defaults to None.

            failure_callback (function): Callback for failures and errors. 
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect, 
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_event_delete(self.token, *args, **kwargs)

    def create(self, *args, **kwargs):
        """
        Request that creates a new PodiumEvent.

        The uri for the newly created event will be provided to the
        redirect_callback if one is provided in the form of a PodiumRedirect.

        Args:
            title (str): title for the vent.

            start_time (str): Starting time, use ISO 8601 format.

            end_time (str): Ending time, use ISO 8601 format.

        Kwargs:
            venue_id(str): ID for the venue of event.

            success_callback (function): Callback for a successful request,
            will have the signature: 
                on_success(result (dict), data (dict))
            Defaults to None..

            failure_callback (function): Callback for failures and errors. 
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect, 
            Will have the signature:
                on_redirect(redirect_object (PodiumRedirect))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_event_create(self.token, *args, **kwargs)

    def update(self, *args, **kwargs):
        """
        Request that updates a PodiumEvent.

        The uri for the newly created event will be provided to the
        redirect_callback if one is provided in the form of a PodiumRedirect.

        Args:
            event_uri (str): URI for the event you are updating.

        Kwargs:
            venue_id(str): ID for the venue of event.

            title (str): title for the vent.

            start_time (str): Starting time, use ISO 8601 format.

            end_time (str): Ending time, use ISO 8601 format.

            success_callback (function): Callback for a successful request,
            will have the signature: 
                on_success(result (dict), updated_uri (str))
            Defaults to None..

            failure_callback (function): Callback for failures and errors. 
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect, 
            Will have the signature:
                on_redirect(redirect_object (PodiumRedirect))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_event_update(self.token, *args, **kwargs)

class PodiumAlertMessagesAPI(object):
    """
    Object that handles event requests and keeps track of the
    authentication token necessary to do so. Usually accessed via
    PodiumAPI object.

    **Attributes:**
        **token** (PodiumToken): The token for the logged in user.

    """

    def __init__(self, token):
        self.token = token

    def list(self, *args, **kwargs):
        """
        Request that returns a PodiumPagedRequest of events. 
        By default a get request to 
        'https://podium.live/api/v1/events' will be made.

        Kwargs:
            expand (bool): Expand all objects in response output. 
            Defaults to True

            quiet (object): If not None HTML layout will not render endpoint
            description. Defaults to None.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(PodiumPagedResponse)
            Defaults to None.

            failure_callback (function): Callback for failures and errors. 
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect, 
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

            start (int): Starting index for events list. 0 indexed.

            per_page (int): Number per page of results, max of 100.

            endpoint (str): If provided the start, per_page, expand, and quiet
            params will not be used instead making a request based on the
            provided endpoint.

        Return:
            UrlRequest: The request being made.

        """
        make_alertmessages_get(self.token, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Request that returns an AlertMessage for the provided alertmessage_uri. 

        Args:
            endpoint (str): URI for the alertmessage you want.

        Kwargs:
            expand (bool): Expand all objects in response output.
            Defaults to True

            quiet (object): If not None HTML layout will not render endpoint
            description. Defaults to None.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(PodiumEvent)
            Defaults to None.

            failure_callback (function): Callback for failures and errors. 
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect, 
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_alertmessage_get(self.token, *args, **kwargs)

    def create(self, *args, **kwargs):
        """
        Request that creates a new PodiumAlertMessage.

        The uri for the newly created alertmessage will be provided to the
        redirect_callback if one is provided in the form of a PodiumRedirect.

        Args:
            message (str): message for the alertmessage

            priority (int): priority of the alertmessage

        Kwargs:
            message(str): ID for the venue of event.
            priority(int): priority for the message.

            success_callback (function): Callback for a successful request,
            will have the signature: 
                on_success(result (dict), data (dict))
            Defaults to None..

            failure_callback (function): Callback for failures and errors. 
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect, 
            Will have the signature:
                on_redirect(redirect_object (PodiumRedirect))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_alertmessage_create(self.token, *args, **kwargs)

class PodiumVenuesAPI(object):
    """
    Object that handles event requests and keeps track of the
    authentication token necessary to do so. Usually accessed via
    PodiumAPI object.

    **Attributes:**
        **token** (PodiumToken): The token for the logged in user.

    """

    def __init__(self, token):
        self.token = token

    def list(self, *args, **kwargs):
        """
        Request that returns a PodiumPagedRequest of events. 
        By default a get request to 
        'https://podium.live/api/v1/events' will be made.

        Kwargs:
            expand (bool): Expand all objects in response output. 
            Defaults to True

            quiet (object): If not None HTML layout will not render endpoint
            description. Defaults to None.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(PodiumPagedResponse)
            Defaults to None.

            failure_callback (function): Callback for failures and errors. 
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect, 
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

            start (int): Starting index for events list. 0 indexed.

            per_page (int): Number per page of results, max of 100.

            endpoint (str): If provided the start, per_page, expand, and quiet
            params will not be used instead making a request based on the
            provided endpoint.

        Return:
            UrlRequest: The request being made.

        """
        make_venues_get(self.token, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Request that returns an Venue for the provided endpoint. 

        Args:
            endpoint (str): URI for the venue you want.

        Kwargs:
            expand (bool): Expand all objects in response output.
            Defaults to True

            quiet (object): If not None HTML layout will not render endpoint
            description. Defaults to None.

            success_callback (function): Callback for a successful request,
            will have the signature:
                on_success(PodiumEvent)
            Defaults to None.

            failure_callback (function): Callback for failures and errors. 
            Will have the signature:
                on_failure(failure_type (string), result (dict), data (dict))
            Values for failure type are: 'error', 'failure'. Defaults to None.

            redirect_callback (function): Callback for redirect, 
            Will have the signature:
                on_redirect(result (dict), data (dict))
            Defaults to None.

            progress_callback (function): Callback for progress updates,
            will have the signature:
                on_progress(current_size (int), total_size (int), data (dict))
            Defaults to None.

        Return:
            UrlRequest: The request being made.

        """
        make_venue_get(self.token, *args, **kwargs)

