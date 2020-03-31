import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

types = {}
dirname = os.getcwd()
types['all'] = pd.read_csv(f'{dirname}/db/search_types/all.csv')
types['owner'] = pd.read_csv(f'{dirname}/db/search_types/owner.csv')
types['dealer'] = pd.read_csv(f'{dirname}/db/search_types/dealer.csv')

class ListingParser:

    def parse_individual_post(self, url, make_model=None, get_body=False):
        """ 
        Parse individual posting from URL 
        Keyword arguments:
            make_model -- make/model specified in search (for analytical purposes)
            get_body -- determines whether body/desription should be parsed
        """
        data = {}
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            # get post details
            data.update(self.__parse_post_details(url))
            data.update(self.__parse_post_title(soup))
            # get timestamps
            ts = self.__parse_post_timestamps(soup)
            data.update(ts)
            # get post attributes
            attrs = soup.find('div', class_='mapAndAttrs')
            data.update(self.__parse_post_attributes(attrs))
            # get posting text body if parameter is set
            if get_body:
                body_html = soup.find('section', id='postingbody')
                qr_message = 'QR Code Link to This Post'
                data['body_text'] = [ l.strip() for l in body_html.text.splitlines() if l and l != qr_message]
            else:
                data['body_text'] = None
        except:
            # assume expiration if above failed
            data['active'] = False
            print(f'url failed --> {url}')
        data['make_model'] = make_model
        return data

    def parse_listing_info(self, listing, make_model=None):
        """ Parse data from search listing tile
        Arguments:
        listing -- listing tile (soupified html) from search results
        make_model -- make/model specified in search (for analytical purposes)
        """
        p = listing.select_one('.result-price')
        price = int(re.search(r'(?<=\$)\d+', p.text).group(0))
        sel = 'a[data-id="%s"]' % listing['data-pid']
        desc = listing.select_one(sel)
        id_ = listing['data-pid']
        url = re.sub(r'(?<=\w{3}\/)d\/.*\/', '', desc['href'])
        return {
            'posting_id': id_,
            'price': price,
            'title': desc.text.strip(),
            'make_model': make_model,
            'url': url,
            'active': True
        }

    def __parse_post_title(self, post):
        """ Parses list title info """
        title = [p.text for p in post.find('span', class_='postingtitletext').findAll('span')]
        price = int(re.search(r'(?<=\$)\d+', title[1]).group(0))
        return {
            'price': price, 
            'title': title[0], 
            'active': True 
        }

    def __parse_post_details(self, url):
        _url_ = re.sub(r'(?<=\w{3}\/)d\/.*\/', '', url)
        posting_id_match = re.search(r'\d+(?=\.html$)', url)
        posting_id = posting_id_match.group(0) if posting_id_match else None
        vendor = self.__get_vendor(_url_)
        return {
            'posting_id': posting_id,
            'vendor': vendor,
            'url': _url_
        }

    def __get_vendor(self, url):
        stype_ = re.search(r'(?<=craigslist\.org)(\/\w+)+(?=\/d|\/\d)', url)
        stype = stype_.group(1) if stype_ else None
        for t in ['all', 'owner', 'dealer']:
            df =  types[t]
            matcher = df[df.search.str.contains(r'%s' % stype)]
            if len(matcher) > 0:
                return t

    def __parse_post_timestamps(self, post):
        """ Parses timestamps from listing """
        timestamps = post.find('div', class_='postinginfos').findAll('time', class_='date timeago')
        data = {}
        ts = [t['datetime'] for t in timestamps]
        data['created_on'] = min(ts)
        data['updated_on'] = max(ts)
        return data

    def __parse_post_attributes(self, attrs):
        """ Parses listing details and location """
        data = {}
        if attrs.div and 'mapbox' in attrs.div.attrs['class']:
            map_info = attrs.div.div.attrs
            data['longitude'] = map_info['data-longitude']
            data['latitude'] = map_info['data-latitude']
            data['accuracy'] = map_info['data-accuracy']
        info = attrs.select('p span')
        for s in info:
            full = s.text.split(':')
            key = full[0] if len(full) > 1 else 'post_title' if 'post_title' not in data else 'xtra_val'
            value = full[1] if len(full) > 1 else full[0]
            data[key.strip().replace(' ', '_')] = value.strip()
        return data
            