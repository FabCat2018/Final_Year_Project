from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get/search-suggestions', views.get_search_suggestions, name='get_search_suggestions'),
    path('search/game/keyword', views.search_game_by_keyword, name='search_game_by_keyword'),
    path('search/game/id', views.search_game_by_id, name='search_game_by_id'),
]
