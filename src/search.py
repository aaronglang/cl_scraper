import re
from bs4 import BeautifulSoup
import pandas as pd
import math
from multiprocessing import Process, Pool
import requests
# module imports
from src.extract import Extract
from src.listing_parser import ListingParser
from src.utils import Utils

class CraigSearch(Extract, ListingParser, Utils):
    """ Search class is responsible for parsing a For-Sale search in craigslist """

    def __init__(self, **kwargs):
        self.__params = {}
        self.__total = (0,0,0)
        self.__search_type = None
        self.__city = kwargs['city']
        super().__init__(kwargs['city'], kwargs['search_type'], kwargs['vendor'])

    def get_params(self):
        """ get search parameters """
        return self.__params

    def set_params(self, **params):
        """ set search parameters """
        self.__params = params

    def get_search_type(self):
        return self.__search_type

    def get_city(self):
        return self.__city

    def soupify(self, params):
        """ Creates bs4 formatted soup from html response """
        (response, search_type, city) = self.extract_search(**params)
        self.__search_type = search_type
        self.__city = city
        soup = BeautifulSoup(response.text, 'html.parser')
        self.__get_totals(soup)
        return soup

    def extract_all_postings(self, first_page_only=False, depth=2, get_body=False):
        """ Extract and parse all data from postings according to search """
        first_group = self.soupify(self.__params)
        if sum(self.__total) == 0:
            yield None
        # scraping first page of results
        if first_page_only:
            # extract data from first page of search results
            yield self.__parse_listings(0, first_group, depth, get_body)
        # scraping all result pages
        else:
            # calculate search groups
            ranges = self.__total[2]/self.__total[1]
            groups = math.ceil(ranges) - 1
            # totals
            group_total = self.__total[1]
            search_total = self.__total[2]
            # set list of search group amounts for url
            s_num = [0] + [group_total * (i+1) if group_total * (i+1) <= search_total else search_total - 1 for i in range(groups)]
            for i in s_num:
                yield self.__parse_listings(i,first_group,depth,get_body)
                

    def __get_totals(self, soup):
        """ Get totals from search results """
        pnum_span = soup.select_one('.pagenum')
        if pnum_span.text != 'no results':
            range_1 = int(pnum_span.span.select_one('.rangeFrom').text)
            range_2 = int(pnum_span.span.select_one('.rangeTo').text)
            total = int(pnum_span.select_one('.totalcount').text)
            self.__total = (range_1, range_2, total)
            self.__params['s'] = range_2
            # check for limit
            self.__limit = self.__check_limit(soup)
        return self.__total


    def __check_limit(self, html):
        """ Check if results are limited and set last posting id if applicable """
        limit = html.find('ul',class_='rows')
        h4 = limit.h4
        if h4:
            l = limit.h4.find_previous_sibling('li')
            return l['data-pid']
        else:
            return None

    def __get_posting_hrefs(self, soup):
        """ Get all posting urls from search results """
        urls = []
        links = soup.findAll('a', class_='result-title hdrlnk')
        for a in links:
            urls.append(a['href'])
            if self.__limit and a['data-id'] == self.__limit:
                break
        return urls

    def __parse_listings(self, search_num, html, depth, get_body):
        """ Parse listing info from search results """
        self.__params['s'] = search_num
        search_results = self.soupify(self.__params) if search_num > 0 else html
        make_model = self.__params['auto_make_model'] if 'auto_make_model' in self.__params else None
        if depth == 1:
            listings = search_results.find_all(attrs={'class': 'result-row'})
            posts = []
            for li in listings:
                info = self.parse_listing_info(li, make_model)
                posts.append(info)
                if self.__limit and info['posting_id'] == self.__limit:
                    break
        elif depth == 2:
            # search by urls --> will not be using values from post
            urls = self.__get_posting_hrefs(search_results)   
            p = Pool(20)
            urls = [(u, make_model, get_body) for u in urls]
            posts = p.starmap(self.parse_individual_post, urls)
            p.terminate()
            p.join()
        return posts