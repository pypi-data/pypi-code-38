# coding=utf8


class FrameParser(object):
    def __init__(self, file_path, func_name, line_no, locals):
        self.data = {
            'file_path': file_path,
            'func_name': func_name,
            'line_no': line_no,
            'locals': self.format_locals(locals)
        }

    def format_locals(self, locals):
        return dict([(k, str(v))for k, v in locals.iteritems()])



class TracebackParser(object):
    def __init__(self, traceback_object):
        self.obj = traceback_object
        self.frames = []

    def _has_next(self, current):
        tb_frame = current.tb_frame
        self.frames.append(
            FrameParser(tb_frame.f_code.co_filename, tb_frame.f_code.co_name, tb_frame.f_lineno, tb_frame.f_locals)
        )
        if current.tb_next:
            self._has_next(current.tb_next)

    def parse(self):
        self._has_next(self.obj)
        frames = []
        for f in self.frames:
            frames.append(f.data)
        return frames
