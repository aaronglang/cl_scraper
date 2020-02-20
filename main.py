import os, json
import pandas as pd
from src.search import CraigSearch

if os.environ['ENV'] == 'dev':
    # dev only
    from dotenv import load_dotenv
    load_dotenv()

# get search params from environment variables
search_type = os.environ['SEARCH_TYPE']
vendor = os.environ['VENDOR']
city = os.environ['SEARCH_CITY']
make_model = os.environ['MAKE_MODEL']
depth = int(os.environ['SEARCH_DEPTH'])
get_body = bool(os.environ['GET_BODY'])

def main():
    # initialize search class with parameters
    cs = CraigSearch(city=city, search_type=search_type, vendor=vendor)
    cs.set_params(auto_make_model=make_model)
    posts = []
    generated = cs.extract_all_postings(first_page_only=False, depth=depth, get_body=get_body)
    # loop through generated results and append to list
    for post_list in generated:
        posts = post_list + posts
    # convert to dataframe for analysis
    df = pd.DataFrame(posts)
    stype = cs.get_search_type()
    if depth == 1: 
        fname_prefix = f'{stype}_depth_1'
    else:
        fname_prefix = stype
    # save results to S3
    cs.save_results(df, cs.get_params(), cs.get_city(), fname_prefix)


if __name__ == '__main__':
    try:
        main()
    except:
        print('Failed to execute main function')