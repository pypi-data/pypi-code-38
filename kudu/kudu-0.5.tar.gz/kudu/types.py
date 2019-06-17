from click.types import IntParamType

from kudu.api import request as api_request


class PitcherFileType(IntParamType):
    name = 'pitcher-file'

    def __init__(self, category=None):
        self.category = category

    def convert(self, value, param, ctx):
        value = super(PitcherFileType, self).convert(value, param, ctx)

        res = api_request('get', '/files/%d/' % value, token=ctx.obj['token'])
        if res.status_code != 200:
            self.fail('%d is not a valid file' % value)

        data = res.json()
        if self.category and data.get('category') not in self.category:
            self.fail('%d is not of a valid file category' % value)

        return data
