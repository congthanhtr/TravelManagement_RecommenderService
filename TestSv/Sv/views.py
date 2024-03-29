import json
import time
import uuid

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings
from http import HTTPStatus

from .crawler import Crawler
from .service.weather_forcast import WeatherForecastService
from .service.recommend_service import RecommendService
from .service.time_travel import TimeTravelService
from .service.ml_service import MachineLearningService
from .model.result_object import ResultObject, ErrorResultObjectType
from .myutils import util

import pandas as pd
import traceback, sys

# ML models
# from .ml_model.decision_tree import model as dc_model
# from .ml_model.decision_tree import x_train

# from .ml_model.linear_regression import lm_model

# from .ml_model.logistic_regression import lgr_model

# Create your views here.

BASE_API_URL = 'api/'
print('connecting to db...')
db = util.get_db_handle(db_name='recommender')
print('connected successfully')
def index(request):
    API_ENDPOINT = BASE_API_URL+'index'
    result = ResultObject()
    # region request content
    # endregion
    try:
        crawler = Crawler()
        list_tour = crawler.crawl_tour_detail()
        result.data = list_tour
    except Exception as ex:
        result.data = util.get_exception(API_ENDPOINT, traceback.format_exc())
        result.status_code = HTTPStatus.BAD_REQUEST.value
    return JsonResponse(util.to_json(result))
def maps(request):
    map_client = googlemaps.Client(util.API_KEY)
    location = util.searchForLocation('Đà Lạt') # param from requests
    search_string = 'hotel' # param from request
    distance = 15*1.6
    response = map_client.places_nearby(location=location, keyword=search_string, name='hotel',radius=distance, types=[types])
    result = response.get('results')
    print(result)
    return HttpResponse(result)

def maps_v3(request):
    start = time.time()
    API_ENDPOINT = BASE_API_URL+'maps_v3'
    result = ResultObject()
    if request.method == "POST":
        try:
            body_content = json.loads(request.body)
            address = body_content['address']
            limit = body_content['limit']
            location = util.get_list_interesting_places(addresses=address, limit=limit)
            end = time.time()
            print('total request time: ' + str(end-start))
            result.data = location
            result.status_code = HTTPStatus.OK.value
        except Exception as e:
            result.data = util.get_exception(API_ENDPOINT, traceback.format_exc())
    return JsonResponse(util.to_json(result))

def maps_v2(request):
    API_ENDPOINT = BASE_API_URL+'maps_v2'
    if request.method == "POST":
        # region request content
        body_content = json.loads(request.body)
        address = body_content['address']
        types = body_content['types']
        # endregion
        result = ResultObject()
        location = util.searchForLocation_v2(address)
        if type(location) == 'str':
            return JsonResponse(util.to_json(location))
        else:
            google_places = GooglePlaces(util.API_KEY)
            try:
                nearby = google_places.nearby_search(
                    lat_lng=location,
                    radius=10000,
                    types=types,
                    rankby=ranking.PROMINENCE,
                    language=lang.VIETNAMESE
                )
                return JsonResponse(util.to_json(nearby))
            except Exception as e:
                return JsonResponse(util.get_exception(API_ENDPOINT, str(e))) 
    else:
        return JsonResponse(util.get_exception(API_ENDPOINT, util.NOT_SUPPORT_HTTP_METHOD_JSONRESPONSE))

def crawl(request):
    crawler = Crawler()
    list_tour = crawler.crawl(None)
    return JsonResponse({"status": "OK"})

def recommend_tour(request):
    API_ENDPOINT = BASE_API_URL+'recommend_tour'
    if request.method == "POST":
        # get data of hot tour
        try:
            dataset, temp_dataset = pd.read_csv('static/crawl.csv'), pd.read_csv('static/crawl.csv')
        except Exception as e:
            return JsonResponse(util.get_exception(API_ENDPOINT, str(e)))
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
    else:
        return JsonResponse(util.get_exception(API_ENDPOINT, util.NOT_SUPPORT_HTTP_METHOD_JSONRESPONSE))

def weather_forecast(request):
    API_ENDPOINT = BASE_API_URL+'v2/weather_forecast'
    result = ResultObject()
    if request.method == "POST":
        try:
            forecaster = WeatherForecastService()
            # region request content
            body_content = json.loads(request.body)
            latitude = body_content['latitude']
            longitude = body_content['longitude']
            forecast_type = body_content['forecast_type']
            # endregion
            forecast_result = forecaster.do_forecast(latitude, longitude, forecast_type)
            if (forecast_result is None):
                forecast_result = {"msg": "latitude, longitude or forecast_type is invalid"}
                result.assign_value(forecast_result, HTTPStatus.BAD_REQUEST.value)
            else:
                result.assign_value(forecast_result, HTTPStatus.OK.value)
        except Exception as e:
            result.data = util.get_exception(API_ENDPOINT, str(traceback.format_exc()))
            result.status_code = HTTPStatus.BAD_REQUEST.value
    else:
        result.data = util.get_exception(API_ENDPOINT, util.NOT_SUPPORT_HTTP_METHOD_JSONRESPONSE)
        result.status_code = HTTPStatus.METHOD_NOT_ALLOWED.value

    return JsonResponse(util.to_json(result))

def predict_vehicle(request):
    API_ENDPOINT = BASE_API_URL+'predict_vehicle'
    result = ResultObject()
    if request.method == "POST":
        try:
            data = json.loads(request.body) # Data is an array

            # Load the data into a pandas DataFrame
            df = pd.DataFrame([data['data']])

            y_pred = dc_model.predict(df.values)

            # Convert the predicted labels to a list
            predictions = y_pred.tolist()

            # Create a dictionary with the predicted labels
            resData = result.assign_value(predictions, 200)

        except Exception as e:
            result.data = util.get_exception(API_ENDPOINT, str(traceback.format_exc()))
            result.status_code = HTTPStatus.BAD_REQUEST.value  
    # Return the result as a JSON response
    return JsonResponse(util.to_json(resData))

def predict_places(request):
    API_ENDPOINT = BASE_API_URL+'predict_places'
    result = ResultObject()
    if request.method == "POST":
        try:
            data = json.loads(request.body) # Data is an array

            # Load the data into a pandas DataFrame
            df = pd.DataFrame(data["data"])

            y_pred = lm_model.predict(df.values)

            # make y_pred a rounded number
            actualResult = round(y_pred[0])

            # Create a dictionary with the predicted labels
            result = result.assign_value(actualResult, 200)

        except Exception as e:
            result.data = util.get_exception(API_ENDPOINT, str(traceback.format_exc()))
            result.status_code = HTTPStatus.BAD_REQUEST.value  
    # Return the result as a JSON response
    return JsonResponse(util.to_json(result))

def recommend(request):
    API_ENDPOINT = BASE_API_URL+'recommend'
    result = ResultObject()
    if request.method == 'POST':
        try:
            #region bodycontent
            body = json.loads(request.body)
            num_of_day = body['num_of_day'] # số ngày
            num_of_night = body['num_of_night'] # số đêm
            cities_from = body['from']
            cities_to = body['to']
            cost_range = body['cost_range']
            contains_ticket = body['contains_ticket']
            hotel_filter_condition = body['hotel_filter_condition']
            tour_filter_condition = body['tour_filter_condition']
            #endregion

            time_travel_service = TimeTravelService()
            ml_service = MachineLearningService()
            # db = util.get_db_handle(db_name='recommender')

            recommend_service = RecommendService(
                num_of_day=num_of_day, 
                num_of_night=num_of_night, 
                cities_from=cities_from, 
                cities_to=cities_to, 
                cost_range=cost_range,
                contains_ticket=contains_ticket,
                hotel_filter_condition=hotel_filter_condition,
                tour_filter_condition=tour_filter_condition, 
                ml_service=ml_service, 
                time_travel_service=time_travel_service,
                db=db)
            result = result.assign_value(data=recommend_service.recommend_v3(), status_code=HTTPStatus.OK.value)
            return JsonResponse(util.to_json(result), status=HTTPStatus.OK)

        except Exception as e:
            result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.EXCEPTION)
            return JsonResponse(util.to_json(result), status=HTTPStatus.BAD_REQUEST)

    else:
        result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.METHOD_NOT_ALLOWED)
        return JsonResponse(util.to_json(result), status=HTTPStatus.BAD_REQUEST)
    
def recommend_v2(request):
    API_ENDPOINT = BASE_API_URL+'v2/recommend'
    result = ResultObject()
    if request.method == 'POST':
        try:
            #region bodycontent
            body = json.loads(request.body)
            num_of_day = body['num_of_day'] # số ngày
            num_of_night = body['num_of_night'] # số đêm
            cities_from = body['from']
            cities_to = body['to']
            cost_range = body['cost_range']
            hotel_filter_condition = body['hotel_filter_condition']
            tour_filter_condition = body['tour_filter_condition']
            num_of_tour = body['num_of_tour'] if 'num_of_tour' in body else 4
            num_of_similar = body['num_of_similar'] if 'num_of_similar' in body else 1
            #endregion

            time_travel_service = TimeTravelService()
            ml_service = MachineLearningService()
            # if cost_range is None or cost_range < 1:
            #     raise ValueError('cost_range must be greater than 1')

            recommend_service = RecommendService(
                num_of_day=num_of_day, 
                num_of_night=num_of_night, 
                cities_from=cities_from, 
                cities_to=cities_to, 
                cost_range=cost_range,
                hotel_filter_condition=hotel_filter_condition,
                tour_filter_condition=tour_filter_condition, 
                ml_service=ml_service, 
                time_travel_service=time_travel_service,
                db=db,
                num_of_tour=num_of_tour,
                num_of_similar=num_of_similar)
            result = result.assign_value(data=recommend_service.recommend_v3(), status_code=HTTPStatus.OK.value)
            return JsonResponse(util.to_json(result), status=HTTPStatus.OK)

        except Exception as e:
            result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.EXCEPTION)
            return JsonResponse(util.to_json(result), status=HTTPStatus.BAD_REQUEST)

    else:
        result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.METHOD_NOT_ALLOWED)
        return JsonResponse(util.to_json(result), status=HTTPStatus.METHOD_NOT_ALLOWED)
    
def poi_recommend(request):
    API_ENDPOINT = BASE_API_URL+'v2/poi/recommend'
    result = ResultObject()
    if request.method == 'POST':
        try:
            #region bodycontent
            body = json.loads(request.body)
            cities_to = body['to']
            tour_filter_condition = body['tour_filter_condition']
            #endregion

            recommend_service = RecommendService(
                cities_to=cities_to, 
                tour_filter_condition=tour_filter_condition, 
                db=db)
            result = result.assign_value(data=recommend_service.poi_recommend(), status_code=HTTPStatus.OK.value)
            return JsonResponse(util.to_json(result), status=HTTPStatus.OK)

        except Exception as e:
            result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.EXCEPTION)
            return JsonResponse(util.to_json(result), status=HTTPStatus.BAD_REQUEST)

    else:
        result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.METHOD_NOT_ALLOWED)
        return JsonResponse(util.to_json(result), status=HTTPStatus.METHOD_NOT_ALLOWED)
    
def poi_find(request):
    import requests
    API_ENDPOINT = BASE_API_URL+'v2/poi/find'
    result = ResultObject()
    if request.method == 'POST':
        try:
            #region bodycontent
            body = json.loads(request.body)
            address = body['address']
            #endregion
            data = dict()
            req = requests.get(util.NOMINATIM_API.format(address)).json()[0]
            data['vi_name'] = req['display_name']
            data['point'] = dict()
            data['point']['lat'] = req['lat']
            data['point']['lon'] = req['lon']
            osm_type = req['osm_type']
            if util.is_equals(osm_type, 'way'):
                data['xid'] = 'W'+str(req['osm_id'])
            elif util.is_equals(osm_type, 'node'):
                data['xid'] = 'N'+str(req['osm_id'])
            elif util.is_equals(osm_type,'relation'):
                data['xid'] = 'R'+str(req['osm_id'])
            data['kinds'] = ''
            data['preview'] = ''
            data['description'] = ''

            result = result.assign_value(data=data, status_code=HTTPStatus.OK.value)
            return JsonResponse(util.to_json(result), status=HTTPStatus.OK)

        except Exception as e:
            result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.EXCEPTION)
            return JsonResponse(util.to_json(result), status=HTTPStatus.BAD_REQUEST)

    else:
        result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.METHOD_NOT_ALLOWED)
        return JsonResponse(util.to_json(result), status=HTTPStatus.METHOD_NOT_ALLOWED)
    
def poi_find_by_xid(request, xid):
    API_ENDPOINT = BASE_API_URL+'v2/poi/poi_find_by_xid'
    result = ResultObject()
    if request.method == 'GET':
        try:
            collection_poi = db.get_collection('vn_pois')
            poi_with_xid = list(collection_poi.find({'xid':xid}, {'_id':0}))[0]
            from .model.interesting_places import InterestingPlace
            data = InterestingPlace(
                xid=poi_with_xid['xid'],
                vi_name=poi_with_xid['vi_name'],
                description=poi_with_xid['vi_description'] if 'vi_description' in poi_with_xid and not util.is_null_or_empty(poi_with_xid['vi_description']) else util.LOREM,
                lat=poi_with_xid['point']['lat'],
                lng=poi_with_xid['point']['lon'],
                preview=poi_with_xid['preview'] if 'preview' in poi_with_xid and not util.is_null_or_empty(poi_with_xid['preview']) else util.PREVIEW,
                rate=poi_with_xid['rate'],
                kinds=util.get_poi_kinds(poi_with_xid['kinds']),
                province_id=poi_with_xid['province_id']
            )
            result = result.assign_value(data=data, status_code=HTTPStatus.OK.value)
            return JsonResponse(util.to_json(result), status=HTTPStatus.OK)
        except Exception as e:
            result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.EXCEPTION)
            return JsonResponse(util.to_json(result), status=HTTPStatus.BAD_REQUEST)
    else:
        result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.METHOD_NOT_ALLOWED)
        return JsonResponse(util.to_json(result), status=HTTPStatus.METHOD_NOT_ALLOWED)

def poi_delete_by_xid(request, xid):
    API_ENDPOINT = BASE_API_URL+'v2/poi/poi_delete_by_xid'
    result = ResultObject()
    if request.method == 'DELETE':
        try:
            collection_poi = db.get_collection('vn_pois')
            data = str(collection_poi.delete_one({'xid':xid}))
            print(data)
            result = result.assign_value(data=data, status_code=HTTPStatus.OK.value)
            return JsonResponse(util.to_json(result), status=HTTPStatus.OK)
        except Exception as e:
            result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.EXCEPTION)
            return JsonResponse(util.to_json(result), status=HTTPStatus.BAD_REQUEST)
    else:
        result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.METHOD_NOT_ALLOWED)
        return JsonResponse(util.to_json(result), status=HTTPStatus.METHOD_NOT_ALLOWED)
    
def poi_add_and_update(request):
    API_ENDPOINT = BASE_API_URL+'v2/poi_api'
    result = ResultObject()
    if request.method == 'POST': # add
        API_ENDPOINT+='/add'
        try:
            #region bodycontent
            body = json.loads(request.body)
            xid = body['xid']
            province_id = body['province_id']
            vi_name = body['vi_name']
            kinds = body['kinds']
            lat = body['lat']
            lon = body['lon']
            preview = body['preview']
            description = body['description']
            #endregion
            collection_poi = db.get_collection('vn_pois')
            data = {}
            data['xid'] = xid if not util.is_null_or_empty(xid) else uuid.uuid4().hex
            data['province_name'] = util.preprocess_city_name(util.get_province_name_by_code(province_id)) if not util.is_null_or_empty(province_id) else None
            data['province_id'] = str(province_id)
            data['vi_name'] = str(vi_name)
            data['name'] = str(vi_name)
            data['kinds'] = str(kinds)
            data['point'] = dict()
            data['point']['lat'] = float(lat)
            data['point']['lon'] = float(lon)
            data['vi_description'] = str(description)
            data['description'] = str(description)
            data['preview'] = dict()
            data['preview']['source'] = str(preview)
            data['rate'] = 2
            
            collection_poi.insert_one(data)
            data.pop('_id')

            result = result.assign_value(data=data, status_code=HTTPStatus.OK.value)
            return JsonResponse(util.to_json(result), status=HTTPStatus.OK)

        except Exception as e:
            result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.EXCEPTION)
            return JsonResponse(util.to_json(result), status=HTTPStatus.BAD_REQUEST)
    elif request.method == 'PUT':
        API_ENDPOINT+='/update'
        try:
            #region bodycontent
            body = json.loads(request.body)
            xid = body['xid']
            province_id = body['province_id']
            name = body['vi_name']
            kinds = body['kinds']
            lat = body['lat']
            lon = body['lon']
            preview = body['preview']
            description = body['description']
            #endregion
            data = {}
            if not util.is_null_or_empty(xid):
                collection_poi = db.get_collection('vn_pois')
                poi = list(collection_poi.find({'xid': xid}))
                if len(list(poi)) == 0:
                    raise ValueError('No xid found')
                poi = poi[0]
                data['province_name'] = util.preprocess_city_name(util.get_province_name_by_code(province_id)) if not util.is_null_or_empty(province_id) else poi['province_name']
                data['province_id'] = province_id if not util.is_null_or_empty(province_id) else poi['province_id']
                data['vi_name'] = str(name)
                data['name'] = str(name)
                data['kinds'] = str(kinds) if not util.is_null_or_empty(kinds) else poi['kinds']
                data['point'] = dict()
                data['point']['lat'] = float(lat)
                data['point']['lon'] = float(lon)
                data['vi_description'] = str(description)
                data['description'] = str(description)
                data['preview'] = dict()
                data['preview']['source'] = str(preview)
                data['rate'] = poi['rate']
                collection_poi.update_many({'xid': xid}, {'$set': data})
                result = result.assign_value(data=data, status_code=HTTPStatus.OK.value)
                return JsonResponse(util.to_json(result), status=HTTPStatus.OK)
            else:
                data['msg'] = 'xid cannot be empty or not found'
                result = result.assign_value(data=data, status_code=HTTPStatus.BAD_REQUEST.value)
                return JsonResponse(util.to_json(result), status=HTTPStatus.BAD_REQUEST)
        
        except Exception as e:
            result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.EXCEPTION)
            return JsonResponse(util.to_json(result), status=HTTPStatus.BAD_REQUEST)

    else:
        result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.METHOD_NOT_ALLOWED)
        return JsonResponse(util.to_json(result), status=HTTPStatus.METHOD_NOT_ALLOWED)

def extract_info_to_excel(request):
    API_ENDPOINT = BASE_API_URL+'v2/extract_info_to_excel'
    result = ResultObject()
    if request.method == 'POST':
        try:
            #region bodycontent
            body = json.loads(request.body)
            num_of_day = body['num_of_day'] # số ngày
            num_of_night = body['num_of_night'] # số đêm
            cities_from = body['from']
            cities_to = body['to']
            cost_range = body['cost_range']
            #endregion

            time_travel_service = TimeTravelService()
            ml_service = MachineLearningService()

            recommend_service = RecommendService(
                num_of_day=num_of_day, 
                num_of_night=num_of_night, 
                cities_from=cities_from, 
                cities_to=cities_to, 
                cost_range=cost_range,
                ml_service=ml_service, 
                time_travel_service=time_travel_service,
                db=db)
            result = result.assign_value(data=recommend_service.extract_info_to_excel(), status_code=HTTPStatus.OK.value)
            return JsonResponse(util.to_json(result), status=HTTPStatus.OK)

        except Exception as e:
            result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.EXCEPTION)
            return JsonResponse(util.to_json(result), status=HTTPStatus.BAD_REQUEST)

    else:
        result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.METHOD_NOT_ALLOWED)
        return JsonResponse(util.to_json(result), status=HTTPStatus.METHOD_NOT_ALLOWED)

def rearrange_grid_view(request):
    API_ENDPOINT = BASE_API_URL+'v2/grid_view'
    result = ResultObject()
    if request.method == 'POST':
        try:
            #region bodycontent
            body = json.loads(request.body)
            xids = body['xids']
            #endregion

            time_travel_service = TimeTravelService()
            recommend_service = RecommendService(time_travel_service=time_travel_service,db=db)
            result = result.assign_value(data=recommend_service.rearrange_grid_view(xids=xids), status_code=HTTPStatus.OK.value)
            return JsonResponse(util.to_json(result), status=HTTPStatus.OK)

        except Exception as e:
            result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.EXCEPTION)
            return JsonResponse(util.to_json(result), status=HTTPStatus.BAD_REQUEST)

    else:
        result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.METHOD_NOT_ALLOWED)
        return JsonResponse(util.to_json(result), status=HTTPStatus.METHOD_NOT_ALLOWED)
    
def get_provider(request, province_id):
    API_ENDPOINT = BASE_API_URL+'v2/get_providers'
    result = ResultObject()
    if request.method == 'GET':
        try:
            #region bodycontent
            types = request.GET.get('types', '').split(',')
            #endregion
            from .model.provider import Provider
            data = Provider().get_provider(db=db, types=types, province_id=int(province_id))
            result = result.assign_value(data=data, status_code=HTTPStatus.OK.value)
            return JsonResponse(util.to_json(result), status=HTTPStatus.OK)
        
        except Exception as e:
            result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.EXCEPTION)
            return JsonResponse(util.to_json(result), status=HTTPStatus.BAD_REQUEST)

    else:
        result = result.assign_value(API_ENDPOINT=API_ENDPOINT, error=ErrorResultObjectType.METHOD_NOT_ALLOWED)
        return JsonResponse(util.to_json(result), status=HTTPStatus.METHOD_NOT_ALLOWED)
