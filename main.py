import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd

search_type = os.environ['SEARCH_TYPE']
vendor = os.environ['VENDOR']
city = os.environ['SEARCH_CITY']
make_model = os.environ['MAKE_MODEL']

from src.search import CraigSearch
cs = CraigSearch(city=city, search_type=search_type, vendor=vendor)
cs.set_params(auto_make_model=make_model)
g = cs.extract_all_postings(first_page_only=False, depth=2)
for x in g:
    print(x)