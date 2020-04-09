import os, json, sys
import pandas as pd
from src.search import CraigSearch

try:
    if os.environ.get('ENV') in ['dev', 'local']:
        from dotenv import load_dotenv
        load_dotenv()

    # get search params from environment variables
    search_type = os.environ.get('SEARCH_TYPE')
    vendor = os.environ.get('VENDOR_TYPE')
    city = os.environ.get('SEARCH_CITY_URL')
    if city is None:
        city = os.environ.get('SEARCH_CITY')
    make_model = os.environ.get('MAKE_MODEL')
    depth = os.environ.get('SEARCH_DEPTH')
    get_body = os.environ.get('GET_BODY')

    if all(v is None for v in [search_type, vendor, city, depth, get_body]):
        print('Necessary environment variables missing... Clean exit')
        exit(0)
    else:
        depth = int(depth)
        get_body = bool(get_body)


except Exception as err:
    print(err)
    print("Error loading environment variables...")
    print("Exiting scraper... Clean exit")
    exit(0)

def main():
    try:
        # initialize search class with parameters
        cs = CraigSearch(city=city, search_type=search_type, vendor=vendor)
        if make_model is not None:
            cs.set_params(auto_make_model=make_model)
        posts = []
        generated = cs.extract_all_postings(first_page_only=False, depth=depth, get_body=get_body)
        # loop through generated results and append to list
        for post_list in generated:
            if post_list is not None:
                posts = post_list + posts
            else:
                break
        # convert to dataframe for analysis
        if(len(posts) > 0):
            df = pd.DataFrame(posts)
            stype = cs.get_search_type()
            if depth == 1: 
                fname_prefix = f'{stype}_depth_1'
            else:
                fname_prefix = stype
            # save results to S3
            cs.save_results(df, cs.get_params(), cs.get_city(), fname_prefix)
        else:
            print("No postings found!")
    except Exception as err:
        print("Error running scraper...")
        print("Exiting scraper with exit code 0...")
        print(err)
        exit(0)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, TypeError, NameError) as err:
        print(err)
        print('Failed to execute main function')
        exit(0)