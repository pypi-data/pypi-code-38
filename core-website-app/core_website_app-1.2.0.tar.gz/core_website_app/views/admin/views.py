""" Admin views
"""
from django.contrib.admin.views.decorators import staff_member_required

import core_website_app.components.account_request.api as account_request_api
import core_website_app.components.contact_message.api as contact_message_api
from core_main_app.utils.rendering import admin_render as render


@staff_member_required
def user_requests(request):
    """ Page that allows to accept or deny user requests

        Args:
            request:

        Returns:
    """
    # Call the API
    requests = account_request_api.get_all()

    assets = {
        "js": [
            {
                "path": 'core_website_app/admin/js/user_requests.js',
                "is_raw": False
            },
        ],
    }

    modals = [
        'core_website_app/admin/account_requests/modals/deny_request.html',
    ]

    return render(request, 'core_website_app/admin/user_requests.html',
                  assets=assets, modals=modals,
                  context={'requests': requests})


@staff_member_required
def contact_messages(request):
    """ List messages from the contact page

        Args:
            request:

        Returns:
    """

    # Call the API
    messages_contact = contact_message_api.get_all()

    assets = {
        "js": [
            {
                "path": 'core_website_app/admin/js/messages.js',
                "is_raw": False
            },
        ],
        "css": [
            "core_website_app/admin/css/messages.css"
        ]
    }

    modals = [
        'core_website_app/admin/contact_messages/modals/delete_message.html',
    ]

    return render(request, 'core_website_app/admin/contact_messages.html',
                  assets=assets, modals=modals,
                  context={'contacts': messages_contact})
