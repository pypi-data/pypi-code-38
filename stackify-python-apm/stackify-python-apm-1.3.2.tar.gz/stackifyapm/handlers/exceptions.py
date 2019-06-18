import linecache

from stackifyapm.utils.helper import get_current_time_in_string


def get_exception_context(exception, tb):
    frames, caught_by = get_exception_frames(exception, tb)
    return {
        "CaughtBy": caught_by,
        "Exception": exception.__class__.__name__,
        "Message": exception.__str__(),
        "Timestamp": get_current_time_in_string(),
        "Frames": frames,
    }


def get_exception_frames(exception, tb):
    frames = []
    caught_by = None

    """
    Format exception traceback into readable list of exception stack trace
    """
    while tb:
        frame = tb.tb_frame
        lineno = frame.f_lineno
        filename = frame.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, frame.f_globals)
        frames.append({
            'Method': "File '{}', line {}, in {}: {}".format(
                filename,
                lineno,
                frame.f_code.co_name,
                line.strip(),
            ),
        })
        tb = tb.tb_next
        if not tb:
            caught_by = _get_class_name(frame, exception)

    return frames, caught_by


def _get_class_name(frame, exception):
    class_object = frame.f_locals.get('self', None)
    return class_object and class_object.__class__.__name__ or frame.f_code.co_name or exception.__class__.__name__
