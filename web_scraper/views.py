import re

from django.http import JsonResponse
from django.shortcuts import render

from .db_connector import DatabaseConnector as dbConnector
from .get_stored_similar_items import get_similar_items
from .keyword_mapper import map_id_to_keyword, map_keyword_to_id
from .matrix_factorisation import recommend_items_for_target_item_mf
from .web_scraper import web_scrape


def index(request):
    return render(request, 'web_scraper/index.html')


def get_search_suggestions(request):
    if request.is_ajax() and request.method == 'GET' and 'term' in request.GET:
        cursor = dbConnector.setup_db_connection()
        search_term = request.GET['term']
        escaped_search_term = re.sub(r"['\"]+", "", search_term)

        get_matching_item_keywords_query = """
            SELECT [item_id], [keywords]
            FROM [Final Year Project].[dbo].[Item_Id_To_Keywords]
            WHERE [keywords] LIKE '%{term}%'
        """.format(term=escaped_search_term)
        cursor.execute(get_matching_item_keywords_query)

        search_suggestions = list()
        for element in cursor.fetchall():
            search_suggestions.append({"label": element.keywords, "value": element.item_id})

        return JsonResponse(search_suggestions, safe=False)


def search_game_by_keyword(request):
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
    similar_items = list()

    if target_item_id == "":
        similar_items.append({'name': "", 'id': ""})
        return similar_items

    similar_item_ids = get_similar_items(target_item_id)

    if not similar_item_ids:
        similar_item_ids = recommend_items_for_target_item_mf(target_item_id)

    for item_id in similar_item_ids:
        similar_items.append({'name': map_id_to_keyword(item_id), 'id': item_id})

    return similar_items
