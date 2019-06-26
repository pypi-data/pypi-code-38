from zmz.utility.error import ParseError


class Result(object):

    def __init__(self, data):
        try:
            self.id = data['id']
            self.title = data['title']
            self.channel_type = data['channel']
            self.channel_name = data['channel_cn']
        except KeyError:
            raise ParseError
