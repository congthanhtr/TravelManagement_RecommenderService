import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .crawler import Crawler, TourInformation
from .weather_forcast import WeatherForecast
from .myutils import util

import pandas as pd
import googlemaps
from googleplaces import GooglePlaces, types, lang, ranking

# Create your views here.

def index(request):
    # region request content
    body_content = json.loads(request.body)
    address = body_content['address']
    # types = body_content['types']
    types = ['restaurant']
    # endregion
    location = util.searchForLocation_v2(address)
    if type(location) == 'str':
        return JsonResponse(util.to_json(location))
    else:
        google_places = GooglePlaces(util.api_key)
        nearby = google_places.nearby_search(
            lat_lng=location,
            radius=10000,
            types=types,
            rankby=ranking.PROMINENCE,
            language=lang.VIETNAMESE
        )
        return JsonResponse(util.to_json(nearby))

def maps(request):
    map_client = googlemaps.Client(util.api_key)
    location = util.searchForLocation('Đà Lạt') # param from requests
    search_string = 'hotel' # param from request
    distance = 15*1.6
    response = map_client.places_nearby(location=location, keyword=search_string, name='hotel',radius=distance, types=[types])
    result = response.get('results')
    print(result)
    return HttpResponse(result)

def crawl(request):
    crawler = Crawler()
    list_tour = crawler.crawl(None)
    return JsonResponse({"status": "OK"})

def recommend_tour(request):
    # get data of hot tour
    dataset, temp_dataset = pd.read_csv('static/crawl.csv'), pd.read_csv('static/crawl.csv')
    # region request content
    body_content = json.loads(request.body)
    list_column_names = body_content['list_column_names']
    weights = body_content['weights']
    impacts = body_content['impacts']
    n_col = body_content['n_col']
    # endregion
    temp_dataset = temp_dataset.filter(list_column_names)
    #region temp
    # all_weight = list(ConfigweightTour.objects.filter(isdeleted=False))
    # all_impact = list(ConfigimpactTour.objects.filter(isdeleted=False))
    # list_column_names = ['TourHotelRate', 'TourPrice']
    # weights = []
    # impacts = []
    # n_col = len(temp_dataset.columns.values)
    # for column_name in list_column_names:
    #     for w in all_weight:
    #         if (w.tourproperty == column_name):
    #             weights.append(w.weight)
    #             break
    #     for i in all_impact:
    #         if i.tourproperty == column_name:
    #             impacts.append("+" if i.tourimpact else "-")
    #             break
    #endregion
    # calculate rank for each tour
    data = util.topsis_pipy(temp_dataset, temp_dataset, n_col, weights, impacts)
    # add column rank to original dataset 
    dataset['Rank'] = data['Rank']
    # sort by rank
    dataset = dataset.sort_values(by='Rank', ascending=True)
    # transfrom dataframe to json
    dataset_dict = dataset.to_dict('records')
    tour_infos = [TourInformation(
        tour_name=data['TourName'],
        tour_code=data['TourCode'],
        tour_length=data['TourLength'],
        tour_from=data['TourFrom'],
        tour_transport=data['TourTransport'],
        tour_hotel_rate=data['TourHotelRate'],
        tour_start_date=data['TourStartDate'],
        tour_price=data['TourPrice'],
        tour_kid=data['TourKid'],
        tour_program=data['TourProgram']
    ) for data in dataset_dict]
    return JsonResponse(util.to_json(tour_infos), safe=False)
    # return HttpResponse(dataset.to_string())

def weather_forecast(request):
    forecaster = WeatherForecast()
    # region request content
    body_content = json.loads(request.body)
    latitude = body_content['latitude']
    longitude = body_content['longitude']
    forecast_type = body_content['forecast_type']
    # endregion
    result = forecaster.do_forecast(latitude, longitude, forecast_type)
    if (result is None):
        result = {"msg": "latitude, longitude or forecast_type is invalid"}
    return JsonResponse(util.to_json(result), safe=False)
