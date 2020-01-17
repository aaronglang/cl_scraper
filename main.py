from src.search import CraigSearch

cs = CraigSearch(city='san francisco bay area', search_type='cars trucks', vendor='owner')

cs.set_params(auto_make_model='porsche')

cs.extract_all_postings(first_page_only=False, depth=2, get_body=True)