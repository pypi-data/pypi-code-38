import django.dispatch

# box_changed = django.dispatch.Signal(providing_args=["before", "after"])
# order_created = django.dispatch.Signal(providing_args=["order"])
app_ready = django.dispatch.Signal(providing_args=[])
