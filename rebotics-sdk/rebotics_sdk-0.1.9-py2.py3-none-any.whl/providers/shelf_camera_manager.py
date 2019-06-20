from .base import ReboticsBaseProvider, remote_service


class ShelfCameraManagerProvider(ReboticsBaseProvider):
    @remote_service('')
    def send_new_file(self):
        self.session.post(

        )

