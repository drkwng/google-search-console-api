import os
import csv
import json
import httplib2
from datetime import date, timedelta

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow


class SearchConsoleAuth:
    """
    API Auth Request
    """
    def __init__(self, client_id, client_secret):
        """
        :param client_id: get it from oauth api key
        :param client_secret: get it from oauth api key
        """
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
        self.OAUTH_SCOPE = 'https://www.googleapis.com/auth/webmasters.readonly'

    def get_gsc_service(self):
        """
        Send OAuth2 request with client_id and client_secret
        :return webmasters_service:
        """
        flow = OAuth2WebServerFlow(self.CLIENT_ID, self.CLIENT_SECRET,
                                   self.OAUTH_SCOPE, redirect_uri=self.REDIRECT_URI)
        authorize_url = flow.step1_get_authorize_url()
        print('Go to the following link in your browser: ' + authorize_url)
        code = input('Enter verification code and press Enter: ').strip()
        credentials = flow.step2_exchange(code)
        http = httplib2.Http()
        http = credentials.authorize(http)
        webmasters_service = build('webmasters', 'v3', http=http)
        return webmasters_service


class GetKeywords(SearchConsoleAuth):
    """
    Get keywords from Search Console API
    """
    def __init__(self, client_id, client_secret, domain, start, end, data_state='all'):
        """
        :param client_id: get it from oauth api key (or load from json)
        :param client_secret: get it from oauth api key (or load from json)
        :param domain: resource name in Google Search Console
        :param start: start date
        :param end: end date
        :param data_state: 'all' param value gets fresh data (send an empty value if you don't need it)
        """
        super().__init__(client_id, client_secret)
        self.service = self.get_gsc_service()
        self.domain = domain
        self.start = start
        self.end = end
        self.data_state = data_state
        self.file = 'gsc_keywords.csv'

        # Check if result csv file exist
        if not os.path.isfile(self.file):
            with open(self.file, 'w', encoding='utf-8') as f:
                f.write('Keyword;Page;Clicks;CTR;Impressions;Position\n')
        else:
            os.remove(self.file)
            with open(self.file, 'w', encoding='utf-8') as f:
                f.write('Keyword;Page;Clicks;CTR;Impressions;Position\n')

    def execute_request(self, start_row):
        """
        Executes a searchAnalytics.query request.
        :param start_row: Program will request next 25K rows (max rowLimit = 25K)
        :return request:
        """
        params = {
            'startDate': self.start,
            'endDate': self.end,
            'dimensions': ['query', 'page'],
            # 'aggregationType': 'byPage',
            'dataState': self.data_state,
            'rowLimit': 25000,
            'startRow': start_row
        }
        request = self.service.searchanalytics().query(siteUrl=self.domain, body=params).execute()
        return request

    def write_to_file(self, result):
        """
        Writes rows from API response to csv file
        :param result:
        """
        with open(self.file, 'a', encoding='utf-8', newline='') as res:
            my_csv = csv.writer(res, delimiter=';')
            for elem in result['rows']:
                row = [elem['keys'][0], elem['keys'][1], elem['clicks'],
                       elem['ctr'], elem['impressions'], elem['position']]
                my_csv.writerow(row)

    def initiate_parse(self):
        """
        Worker. Makes API requests and writes results to csv.
        """
        start_row = 0
        while True:
            try:
                result = self.execute_request(start_row)
                self.write_to_file(result)
                if len(result['rows']) == 25000:
                    print('There are more than 25000 rows in response. Continue parsing...')
                    start_row += 25000
                else:
                    print(f'Finally! We got {start_row + len(result["rows"])} keywords in total.')
                    break

            except Exception as err:
                print(err, type(err))
                break

    def clear_not_unique(self):
        """
        Clears not unique values from result csv file
        """
        with open(self.file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f, delimiter=';')
            all_keys = {rows[0]: rows[1:] for rows in reader}
        with open(self.file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            for _key, _value in all_keys.items():
                row = [_key, _value[0], _value[1], _value[2], _value[3], _value[4]]
                writer.writerow(row)


if __name__ == '__main__':
    try:
        key_filename = input('Enter JSON filename: ').strip()
        website = input('Enter GSC resource name: ').strip()

        with open(key_filename) as key:
            data = json.load(key)
        api_id = data['installed']['client_id']
        api_secret = data['installed']['client_secret']

        today = date.today()
        # Last 16 month API limit
        start_date = str(today - timedelta(days=486))
        end_date = str(date.today() - timedelta(days=1))

        api_req = GetKeywords(api_id, api_secret, website, start_date, end_date)
        api_req.initiate_parse()

        # Dialog to clear not unique values from csv
        while True:
            choose_msg = input('Do you want to clear not unique values from your result csv (YES / NO)?\n')
            if 'yes' in choose_msg.lower():
                api_req.clear_not_unique()
                print("Done! Your keys here: 'gsc_keywords.csv'")
                break
            elif 'no' in choose_msg.lower():
                print("Done! Your keys here: 'gsc_keywords.csv'")
                break
            else:
                print('Please choose the correct answer (YES/NO)')

    except Exception as e:
        print('Out of class error:\n', e, type(e))
