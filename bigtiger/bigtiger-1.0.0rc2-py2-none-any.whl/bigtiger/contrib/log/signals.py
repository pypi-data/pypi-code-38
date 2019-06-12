from django.dispatch import Signal

# user_logged_in = Signal(providing_args=['request', 'user'])
# user_login_failed = Signal(providing_args=['credentials'])
# user_logged_out = Signal(providing_args=['request', 'user'])

user_log_success = Signal(
    providing_args=['request', 'action_class', 'action_object', 'action_handler', 'status_note'])

user_log_error = Signal(
    providing_args=['request', 'action_class', 'action_object', 'action_handler', 'status_note'])
