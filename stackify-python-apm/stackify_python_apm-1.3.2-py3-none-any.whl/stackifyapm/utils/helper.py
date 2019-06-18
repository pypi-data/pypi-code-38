import time
import threading
import multiprocessing

from stackifyapm.conf.constants import RUM_SCRIPT_SRC


def get_current_time_in_millis():
    return time.time() * 1000


def get_current_time_in_string():
    return str(int(get_current_time_in_millis()))


def is_async_span():
    return hasattr(threading.current_thread(), 'transaction') or hasattr(multiprocessing.current_process(), 'transaction')


def get_stackify_header(transaction=None):
    if not transaction:
        return ""

    properties = transaction.get_meta_data().get('property_info')
    client_id = properties.get('clientId', None)
    device_id = properties.get('deviceId', None)

    stackify_params = ["V1"]
    transaction and stackify_params.append(str(transaction.get_id()))
    client_id and stackify_params.append("C{}".format(client_id))
    device_id and stackify_params.append("CD{}".format(device_id))

    return "|".join(stackify_params)


def get_rum_script_or_None(transaction):
    if transaction:
        meta_data = transaction.get_meta_data()

        property_info = meta_data.get('property_info', {})
        application_info = meta_data.get('application_info')

        data_enableInternalLogging = False

        rum_trace_parent = transaction.get_trace_parent()

        if property_info.get('clientRumDomain') and property_info.get('clientId') and property_info.get('deviceId'):

            rum_script_str = '<script src="{}" data-host="{}" data-requestId="V2|{}|{}|{}" data-a="{}" data-e="{}" data-enableInternalLogging="{}" async> </script>'.format(
                RUM_SCRIPT_SRC,
                property_info["clientRumDomain"],
                rum_trace_parent.trace_id,
                property_info["clientId"],
                property_info["deviceId"],
                application_info["application_name"],
                application_info["environment"],
                data_enableInternalLogging,
            )

            return rum_script_str
    return None
