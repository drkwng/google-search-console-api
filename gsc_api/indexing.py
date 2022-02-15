import json
import logging
from .auth import GoogleOAuth, GoogleServiceAccount
from googleapiclient.errors import HttpError


class CheckIndexation(GoogleOAuth):
    def __init__(self, _client_secret_file):
        """
        Check URL Indexation Status (and many other parameters)
        :param _client_secret_file: OAuth json file path
        :type _client_secret_file: str
        """
        self.SCOPES = ['https://www.googleapis.com/auth/webmasters']
        self.CLIENT_SECRET = _client_secret_file
        self.SERVICE_NAME = 'searchconsole'
        self.VERSION = 'v1'

        super().__init__(self.CLIENT_SECRET, self.SCOPES, self.SERVICE_NAME, self.VERSION)
        self.auth = self.auth()

    def exec_request(self, _url, _domain):
        try:
            request = {
                'inspectionUrl': _url,
                'siteUrl': _domain
            }
            return self.auth.urlInspection().index().inspect(body=request).execute()

        except HttpError as err:
            logging.error(err)
            return None

    def worker(self, _data):
        response = {}
        for key, value in _data.items():
            for val in value:
                response[val] = self.exec_request(val, key)
                logging.info(f'Check URL {key} response: {response[val]}')
        return response


class Indexation(GoogleServiceAccount):
    def __init__(self, _service_account_file):
        """
        Send URLs to Googlebot via Indexing API
        :param _service_account_file: OAuth json file path
        :type _service_account_file: str
        """
        self.CLIENT_SECRET = _service_account_file
        self.SCOPES = ["https://www.googleapis.com/auth/indexing"]

        super().__init__(self.CLIENT_SECRET, self.SCOPES)
        self.auth = self.auth()

    def exec_request(self, _data):
        endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"

        try:
            response, content = self.auth.request(
                endpoint, method="POST", body=_data
            )
            return json.loads(content.decode())

        except HttpError as err:
            logging.error(err)
            return None

    def worker(self, _urls, _method):
        result = {}
        for u in _urls:
            data = {
                'url': u.strip(),
                'type': _method
            }
            result[u] = self.exec_request(json.dumps(data))
            logging.info(f'Send {u} to Googlebot response: {result[u]}')

        return result


if __name__ == "__main__":

    # urls = {
    #     'https://domain.com/': ['https://domain.com/url1/', 'https://domain.com/url2/', ]
    # }
    # check_index = CheckIndexation('client_secret.json')
    # check_index.worker(urls)

    urls = ['https://winner-stile.com.ua/rjukzaki', ]
    method = "URL_UPDATED"
    index = Indexation('service_account.json')
    index.worker(urls, method)
