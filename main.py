import os, json
import pandas as pd
from src.search import CraigSearch

try:
    if os.environ['ENV'] in ['dev', 'local']:
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
except:
    print("Error loading environment variables...")
    print("Exiting scraper... Clean exit")
    exit(0)

def main():
    try:
        # initialize search class with parameters
        cs = CraigSearch(city=city, search_type=search_type, vendor=vendor)
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
    except (RuntimeError, TypeError, NameError) as err:
        print("Error running scraper...")
        print("Exiting scraper with exit code 0...")
        print(err)
        exit(0)


if __name__ == '__main__':
    try:
        main()
    except:
        print('Failed to execute main function')
        exit(0)