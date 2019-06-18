from ms_sdk.Lib.Http.Response import Response
from ms_sdk.Lib.Makers.ObjectMaker import ObjectMaker


class CountMaker(ObjectMaker):

    def makeSingle(self, response: Response):
        """
        :param Response response:
        :return int|None|ms_sdk.Entities.Entity:
        """
        if not response.getSuccess():
            return 0

        data = response.getData()

        try:
            item = self.getAttributes(data[0])
            return int(item['count'])
        except KeyError:
            return 0
