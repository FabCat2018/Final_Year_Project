from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/game', views.search_game, name='search_game'),
    path('search/game/id', views.search_game_by_id, name='search_game_by_id'),
]
