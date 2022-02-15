import logging

from datetime import date, timedelta

from .auth import GoogleOAuth


class GetKeywords(GoogleOAuth):
    def __init__(self, _client_secret_file, _domain):
        """
        Get all keywords from Google Search Console (last 16 months)
        :param _client_secret_file: OAuth json file path
        :type _client_secret_file: str
        :param _domain: Google Search Console resource name
        :type _domain: str
        """
        self.SCOPES = ['https://www.googleapis.com/auth/webmasters']
        self.CLIENT_SECRET = _client_secret_file
        self.SERVICE_NAME = 'searchconsole'
        self.VERSION = 'v1'

        self.domain = _domain

        super().__init__(self.CLIENT_SECRET, self.SCOPES, self.SERVICE_NAME, self.VERSION)
        self.service = self.auth()

    def execute_request(self, start_row, start, end, r_type, aggregate_by):
        """
        Executes a searchAnalytics.query request.
        """
        params = {
            'type': r_type,
            'startDate': start,
            'endDate': end,
            'dimensions': ['query', 'page'],
            'aggregationType': aggregate_by,
            'dataState': 'all',
            'rowLimit': 25000,
            'startRow': start_row
        }
        request = self.service.searchanalytics().query(siteUrl=self.domain, body=params).execute()
        return request

    def worker(self, start, end, r_type='web', aggregate_by='auto'):
        start_row = 0
        result = []
        while True:
            try:
                response = self.execute_request(start_row, start, end, r_type, aggregate_by)
                result.append(response)
                if len(response['rows']) == 25000:
                    start_row += 25000
                else:
                    logging.info(f'We got {start_row + len(response["rows"])} keywords in total.')
                    break

            except Exception as err:
                logging.error(err)

        return result


if __name__ == "__main__":

    client_secret = 'client_secret.json'
    keywords = GetKeywords(client_secret, 'https://domain.com/')

    today = date.today()
    start_date = str(today - timedelta(days=486))
    end_date = str(date.today() - timedelta(days=1))

    data = keywords.worker(start_date, end_date)
    print(f'Keywords est. got: {len(data)}')
