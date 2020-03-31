import requests
from functools import wraps
import editdistance
import pandas as pd
import re, os

# set dirname
dirname = os.getcwd()

def validate_params(func):
    params = [
        ('min_price', int),
        ('max_price', int),
        ('auto_make_model', str),
        ('min_auto_year', int),
        ('max_auto_year', int),
        ('min_auto_miles', int),
        ('max_auto_miles', int),
        ('search_distance', int),
        ('postal', int),
        ('s', int),
        ('query', str)
    ]
    @wraps(func)
    def val(*args, **kwargs):
        for k in kwargs.items():
            p = [param for param in params if param[0] == k[0] and type(k[1]) is param[1]]
            if len(p) == 0:
                message = f'invalid type:\n\t function: {func.__name__}, arg: {k[0]}, value: {k[1]}, type: {type(k[1])}'
                print(message)
                raise TypeError(message)
        return func(*args, **kwargs)
    return val


class Extract:
        
    def __init__(self, city, search_type='cars trucks', vendor='all'):
        self.__city = city
        self.__search_type = search_type
        self.__vendor = vendor

    @validate_params
    def extract_search(self, **kwargs):
        """ Extract html from given url and return raw html """
        (city, city_url) = self.__get_city_url()
        search = self.__get_search_type()
        if search is None:
            raise ValueError(f'search type invalid:\n\t"{self.__search_type}"')
        city_url = re.sub(r'/$', '', city_url)
        url = f'{city_url}{search}'
        r = self.__get(url, kwargs)
        print(f'QUERY = {r.url}')
        s = re.sub(r'\/search\/', '', search)
        return (r, s, city)

    def __get_city_url(self):
        """ 
        Get city from CSV/DB

        search conditions: 
        if edit distance is less than 4 -> return city

        """
        df = pd.read_csv(f'{dirname}/db/cities/craigslist_cities.csv')
        # if link provided
        if re.search(r'^https', self.__city):
            apply_func = lambda x: x['link'] == self.__city
        # if city name provided -> search for matching city name
        else:
            apply_func = lambda x: editdistance.eval(x['city_name'], self.__city) < 4
        matcher = df[df.apply(apply_func, axis=1)]
        if not matcher.empty:
            return (matcher['city_name'].values[0], matcher['link'].values[0])

    def __get_search_type(self):
        df = pd.read_csv(f'{dirname}/db/search_types/{self.__vendor}.csv')
        apply_func = lambda x: editdistance.eval(x['name'], self.__search_type) < len(self.__search_type)/3
        matcher = df[df.apply(apply_func, axis=1)]
        if not matcher.empty:
            return matcher['search'].values[0]

    def __get(self, url: str, params):
        """ performs all GET requests and returns html """
        return requests.get(url, params=params)