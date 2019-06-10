from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()

router.register( r'users', views.User, base_name='users' )

token_router = routers.NestedSimpleRouter( router, r'users', lookup='users' )
token_router.register( r'token', views.Token, base_name='tokens' )


urlpatterns = router.urls + token_router.urls
