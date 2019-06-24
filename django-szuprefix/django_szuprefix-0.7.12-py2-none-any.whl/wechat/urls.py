from django.conf.urls import url, include
from . import mp
app_name = "wechat"
urlpatterns = [
    url(r'^mp/', include(mp.urls)),
]
