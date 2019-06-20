from vk import API


class ApiBased:
    __VERSION = 5.92

    def __init__(self, api) -> None:
        super().__init__()

        self.__api = api

    @property
    def api(self) -> API:
        return self.__api

    def get_default_object(self):
        return {
            "v": ApiBased.__VERSION
        }

    def get_request(self, parameters: dict) -> dict:
        assert "v" not in parameters

        request = self.get_default_object()

        request.update(parameters)

        return request
