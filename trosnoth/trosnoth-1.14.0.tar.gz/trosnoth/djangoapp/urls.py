from django.urls import path

from . import views


app_name = 'trosnoth'
urlpatterns = [
    path('', views.index, name='index'),
    path('u/', views.userList, name='userlist'),
    path('u/<int:userId>/', views.userProfile, name='profile'),
    path(
        'u/<int:userId>/<str:nick>/', views.userProfile, name='profile'),
    path('g/', views.gameList, name='gamelist'),
    path('g/<int:gameId>/', views.viewGame, name='viewgame'),
    path('t/<int:tournamentId>/', views.tournament, name='tournament'),
    path('a/<int:arenaId>/', views.manageArena, name='arena'),
    path('a/<int:arenaId>/delete/', views.deleteArena, name='delarena'),
    path('a/<int:arenaId>/scenario/', views.startLevel, name='scenario'),
    path('a/', views.arenas, name='arenas'),
    path('a/new/', views.newArena, name='newarena'),

    path('settings', views.serverSettings, name='settings'),
    path('shutdown', views.shutdown, name='shutdown'),
    path('mu', views.manageUsers, name='manageusers'),
    path('tokenauth', views.tokenAuth, name='tokenauth'),
]

