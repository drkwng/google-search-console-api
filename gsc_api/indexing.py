import logging
from .auth import GoogleOAuth


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
        self.service = self.auth()

    def exec_request(self, _url, _domain):
        try:
            request = {
                'inspectionUrl': _url,
                'siteUrl': _domain
            }
            return self.service.urlInspection().index().inspect(body=request).execute()

        except Exception as err:
            logging.error(err)
            return None

    def worker(self, _data):
        response = {}
        for key, value in _data.items():
            for val in value:
                response[val] = self.exec_request(val, key)
                logging.info(f'Check URL {val} response: {response[val]}')
        return response


class Indexation(GoogleOAuth):
    def __init__(self, _service_account_file):
        """
        Send URLs to Googlebot via Indexing API
        :param _service_account_file: OAuth json file path
        :type _service_account_file: str
        """
        self.CLIENT_SECRET = _service_account_file
        self.SCOPES = ["https://www.googleapis.com/auth/indexing"]
        self.SERVICE_NAME = 'indexing'
        self.VERSION = 'v3'

        super().__init__(self.CLIENT_SECRET, self.SCOPES, self.SERVICE_NAME, self.VERSION)
        self.service = self.auth()

    @staticmethod
    def callback_callable(request_id, response, exception):
        if exception is not None:
            logging.info(f'{exception}')
        else:
            data = (
                response['urlNotificationMetadata']['latestUpdate']['notifyTime'],
                response['urlNotificationMetadata']['url'],
                response['urlNotificationMetadata']['latestUpdate']['type'],
            )
            logging.info(data)

    def worker(self, _urls, _method):
        batch = self.service.new_batch_http_request(callback=self.callback_callable)
        for url in _urls:
            batch.add(self.service.urlNotifications().publish(
                body={"url": url, "type": _method}
            ))
        return batch.execute()

