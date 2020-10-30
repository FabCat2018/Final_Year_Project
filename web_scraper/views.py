# from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'web_scraper/index.html')
