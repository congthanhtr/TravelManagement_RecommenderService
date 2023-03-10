import pickle
import time
import jsonpickle
import pandas as pd
import requests
import urllib.parse

import googlemaps
import wikipediaapi
from deep_translator import GoogleTranslator

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from .model.interesting_places import InterestingPlace
from .model.vietnam_city_geo import VietnamCityGeo, VietnamCityBBox

class util:

    wiki = wikipediaapi.Wikipedia('vi')
    translator = GoogleTranslator(source='en', target='vi')

    API_KEY = open('static/api_key.txt').read()
    API_KEY_OPENTRIPMAP = open('static/api_key_opentripmap.txt').read()
    NOT_SUPPORT_HTTP_METHOD_JSONRESPONSE = {'msg': 'not supported this http method'}
    EXCEPTION_THROWN_AT_JSONRESPONSE = 'exception thrown at '
    EXCEPTION_MESSAGE_JSONRESPONSE = ''

    vietnam_city_geo = VietnamCityGeo().load_list()
    vietnam_city_bbox = VietnamCityBBox().load_list()

    NOMINATIM_API = 'https://nominatim.openstreetmap.org/search/{}?format=json&addressdetails=1&countrycodes=vn'
    NOMINATIM_CHECK_API = 'https://nominatim.openstreetmap.org/status.php?format=json'
    NOMINATIM_DETAIL_API = 'https://nominatim.openstreetmap.org/details.php?osmtype={}&osmid={}&format=json'

    OPENTRIPMAP_API = 'https://api.opentripmap.com/0.1/en/places/bbox?lon_min={}&lon_max={}&lat_min={}&lat_max={}&format=json&src_attr=osm&limit={}&apikey={}' # must format with {lonmin, lonmax, latmin, latmax, maxobject, apikey}
    OPENTRIPMAP__DETAIL_PLACE_API = 'https://api.opentripmap.com/0.1/en/places/xid/{}?apikey={}'
    
    @staticmethod
    def get_exception(at: str, msg: str) -> dict:
        '''
        get exception and return it as msg to client
        '''
        util.EXCEPTION_THROWN_AT_JSONRESPONSE += at
        util.EXCEPTION_MESSAGE_JSONRESPONSE = str(msg)
        return {
            'ex_at': util.EXCEPTION_THROWN_AT_JSONRESPONSE,
            'ex_msg': util.EXCEPTION_MESSAGE_JSONRESPONSE
        }

    #region topsis method
    @staticmethod
    def Calc_Values(temp_dataset, nCol, impact):
        # print(" Calculating Positive and Negative values...\n")
        p_sln = (temp_dataset.max().values)[0:]
        n_sln = (temp_dataset.min().values)[0:]
        for i in range(0, nCol):
            if impact[i] == '-':
                p_sln[i], n_sln[i] = n_sln[i], p_sln[i]
        return p_sln, n_sln

    def Normalize(temp_dataset, nCol, weights):
        # normalizing the array
        # print(" Normalizing the DataSet...\n")
        for i in range(0, nCol):
            temp = 0
            for j in range(len(temp_dataset)):
                temp = temp + temp_dataset.iloc[j, i]**2
            temp = temp**0.5
            for j in range(len(temp_dataset)):                      
                temp_dataset.iat[j, i] = (
                    temp_dataset.iloc[j, i] / temp)*weights[i]
        return temp_dataset

    def topsis_pipy(temp_dataset, dataset, nCol, weights, impact):
        # normalizing the array
        temp_dataset = util.Normalize(temp_dataset, nCol, weights)

        # Calculating positive and negative values
        p_sln, n_sln = util.Calc_Values(temp_dataset, nCol, impact)

        # calculating topsis score
        # print(" Generating Score and Rank...\n")
        score = []
        for i in range(len(temp_dataset)):
            temp_p, temp_n = 0, 0
            for j in range(0, nCol):
                temp_p = temp_p + (p_sln[j] - temp_dataset.iloc[i, j])**2
                temp_n = temp_n + (n_sln[j] - temp_dataset.iloc[i, j])**2
            temp_p, temp_n = temp_p**0.5, temp_n**0.5
            score.append(temp_n/(temp_p + temp_n))
        dataset['Topsis Score'] = score

        # calculating the rank according to topsis score
        dataset['Rank'] = (dataset['Topsis Score'].rank(
            method='max', ascending=False))
        dataset = dataset.astype({"Rank": int})
        return dataset
        #endregion

    @staticmethod
    def searchForLocation(address):
        '''
        Parameters:
            address: String
                - The address is a user input.

        Returns:
            location: Dictionary
                - A dictionary returning the latitude, and longitude
                of an address.
        '''

        gmaps = googlemaps.Client(key=util.api_key)
        #geocoding and address
        geocodeResult = gmaps.geocode(address)

        if geocodeResult:
            location = geocodeResult[0]['geometry']['location']
            return location

    @staticmethod
    def searchForLocation_v2(address):
        '''
        Parameters:
            address: String
                - The address is a user input.

        Returns:
            location: Dictionary
                - A dictionary returning the latitude, and longitude
                of an address.
        '''
        url = util.NOMINATIM_API.format(address)
        response = requests.get(url).json()
        if response:
            location = response[0]
            return {'lat': location['lat'], 'lng': location['lon']}
            # return location
    
    @staticmethod
    def search_for_boundary_box(address):
        '''
        T??m th??ng tin v??? boundary box th??ng qua address
            Tr??? v???: tuple (lonmin, lonmax, latmin, latmax)
        '''
        response = requests.get(util.NOMINATIM_API.format(address)).json()
        if response:
            location = response[0]['boundingbox']
            return (location[2], location[3], location[0], location[1])

    @staticmethod
    def to_json(obj):
        '''
        transform data into json to send to client
        '''
        encoded_data = jsonpickle.encode(obj, unpicklable=False)
        decoded_data = jsonpickle.decode(encoded_data)
        return decoded_data

    @staticmethod
    def contains_day(source: str, no_of_day: int):
        day_with_zero = 'ng??y 0' + str(no_of_day)
        day_without_zero = 'ng??y ' + str(no_of_day)
        if source.lower().__contains__(day_with_zero):
            return (True, day_with_zero)
        elif source.lower().__contains__(day_without_zero):
            return (True, day_without_zero)
        else:
            return (False, '')
        
    @staticmethod
    def find_between_element(first_element: WebElement, second_element: WebElement):
        """
        T??m t???t c??? c??c element n???m gi???a first v?? second element 
        """
        if first_element is not None and second_element is not None:
            after = first_element.find_elements(By.XPATH, 'following-sibling::*')
            before = second_element.find_elements(By.XPATH, 'preceding-sibling::*')
            middle = [elem for elem in after if elem in before]
        elif first_element is None:
            middle = second_element.find_elements(By.XPATH, 'preceding-sibling::*')
        elif second_element is None:
            middle = first_element.find_elements(By.XPATH, 'following-sibling::*')
        return middle
    
    @staticmethod
    def is_contains(source: str, child: str):
        """
        Ki???m tra xem chu???i source c?? bao g???m chu???i child kh??ng?
            Tr??? v???: True n???u ch???a, False n???u kh??ng
        """
        if source.lower().__contains__(child.lower()):
            return True
        return False
    
    @staticmethod
    def is_equals(source: str, des: str):
        if source.lower() == des.lower():
            return True
        return False
    
    @staticmethod
    def is_null_or_empty(source: str):
        """
        Ki???m tra chu???i None hay chu???i tr???ng hay kh??ng?
        """
        if source == '' or source is None:
            return True
        return False
    
    @staticmethod
    def find_city_for_destination(destination: str):
        """
        T??m t???nh/th??nh ph??? cho ?????a ??i???m du l???ch
        """
        response = requests.get(util.NOMINATIM_API.format(urllib.parse.quote(destination))).json()
        if response:
            address = response[0]['address']
            city: str = ''
            if 'state' in address:
                city = address['state']
            if 'city' in address:
                city = address['city']
            return city
        
    @staticmethod
    def translate(text: str):
        return util.translator.translate(text)

    @staticmethod
    def translate_to_vietnamese(text: str):
        return util.translate(text=text)
    
    @staticmethod
    def get_boundary_box(address: str):
        index = util.vietnam_city_bbox.list_id.index(address)
        return (
            util.vietnam_city_bbox.list_min_lon[index],
            util.vietnam_city_bbox.list_max_lon[index],
            util.vietnam_city_bbox.list_min_lat[index],
            util.vietnam_city_bbox.list_max_lat[index],
        )
    
    @staticmethod
    def get_list_interesting_places(addresses: list[str], limit: int) -> list:
        '''
        T??m th??ng tin v??? c??c ?????a ??i???m tham quan du l???ch h???p d???n t???i m???t ??i???m
        '''
        list_interesting_places = []
        for address in addresses:
            boundary_box = util.get_boundary_box(address=address)
            url = util.OPENTRIPMAP_API.format(boundary_box[0], boundary_box[1], boundary_box[2], boundary_box[3], limit, util.API_KEY_OPENTRIPMAP)
            response = requests.get(url=url)
            if not response.raise_for_status():
                response = response.json()
                for poi in response:
                    xid = poi['xid']
                    detail_url = util.OPENTRIPMAP__DETAIL_PLACE_API.format(xid, util.API_KEY_OPENTRIPMAP)
                    detail_response = requests.get(detail_url)
                    if (not detail_response.raise_for_status()):
                        detail_response = detail_response.json()
                        # get value
                        en_summary = ''
                        en_name = ''
                        image = ''
                        if 'wikipedia_extracts' in detail_response:
                            en_summary = detail_response['wikipedia_extracts']['text']
                        if 'name' in detail_response:
                            en_name = detail_response['name']
                        if 'image' in detail_response:
                            image = detail_response['image']
                        # assign value
                        interesting = InterestingPlace()
                        # interesting.summary = util.translate_to_vietnamese(en_summary)
                        interesting.summary = en_summary
                        # interesting.vi_name = util.translate_to_vietnamese(en_name)
                        interesting.vi_name = en_name
                        interesting.image = image
                        interesting.province = address
                        # append to list
                        list_interesting_places.append(interesting)
        return list_interesting_places
    
    
