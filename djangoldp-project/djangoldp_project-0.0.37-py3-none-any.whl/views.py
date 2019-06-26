from djangoldp.views import LDPViewSet
import requests

from djangoldp.views import LDPViewSet
from .models import Project


class ProjectViewSet(LDPViewSet):
    model = Project
    permission_classes = []
    nested_fields = ["members"]

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        requests.post("https://jabber.happy-dev.fr/happydev_muc_admin/",
                      json={"@context": "https://cdn.happy-dev.fr/owl/hdcontext.jsonld",
                            "@graph": [{"object": str(self.get_object().get_absolute_url()), "type": "Update"}]})
        return response


Project._meta.view_set = ProjectViewSet
