from django.http import JsonResponse
from django.shortcuts import render

from .get_stored_similar_items import get_similar_items
from .keyword_mapper import map_id_to_keyword, map_keyword_to_id
from .recommender_system import find_similar_items_to_target_item
from .web_scraper import web_scrape


def index(request):
    return render(request, 'web_scraper/index.html')


def search_game(request):
    if request.is_ajax() and request.method == 'GET':
        term = request.GET.get("search_term", None)
        search_results = web_scrape(term)
        recommender_results = _recommend_items(term)
        return JsonResponse({"search_results": search_results, "recommender_results": recommender_results})


def search_game_by_id(request):
    if request.is_ajax() and request.method == 'GET':
        game_id = request.GET.get("game_id", None)
        search_results = web_scrape(map_id_to_keyword(game_id))
        recommender_results = _recommend_items_from_id(game_id)
        return JsonResponse({"search_results": search_results, "recommender_results": recommender_results})


def _recommend_items(target_item):
    target_item_id = map_keyword_to_id(target_item)
    return _recommend_items_from_id(target_item_id)


def _recommend_items_from_id(target_item_id):
    similar_item_ids = get_similar_items(target_item_id)

    if not similar_item_ids:
        similar_item_ids = find_similar_items_to_target_item(target_item_id)

    similar_items = list()
    for item_id in similar_item_ids:
        if type(item_id) is str:
            key_id = item_id
        else:
            key_id = item_id['item_id']
        similar_items.append({'name': map_id_to_keyword(key_id), 'id': key_id})

    return similar_items
