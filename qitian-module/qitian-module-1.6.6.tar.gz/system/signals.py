import django.dispatch
from django.core.signals import request_finished

image_signal = django.dispatch.Signal(providing_args=["origin_src", 'local_src', 'remote_src'])

# class ImageSignal:
#
#     @staticmethod
#     def send(origin_src, local_src, remote_src):
#         pass
