import os, datetime
dirname = os.getcwd()

class Utils:

    def save_results(self, df, params, city, search_type):
        """ write parsed search results to files """
        fname = params['auto_make_model'] if 'auto_make_model' in params else 'generic'
        city = city.replace(' ', '')
        ts = datetime.datetime.now().isoformat()
        df.to_csv(f'{dirname}/db/results/{search_type}_{fname}_{city}_{ts}_results.csv')