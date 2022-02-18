import logging

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.oauth2.service_account import Credentials


class GoogleOAuth:
    def __init__(self, file_path, scopes, service_name, version):
        """
        Google OAuth for Search Analytics keywords report and URL Inspect
        :param file_path: oauth json file
        :type file_path: str
        :param scopes: e.g. ['https://www.googleapis.com/auth/webmasters']
        :type scopes: list
        :param service_name: e.g. 'searchconsole'
        :type service_name: str
        :param version: e.g. 'v1'
        :type version: str
        """
        self.OAUTH_FILE_PATH = file_path
        self.SCOPES = scopes
        self.SERVICE_NAME = service_name
        self.VERSION = version

    def auth(self):
        flow = InstalledAppFlow.from_client_secrets_file(self.OAUTH_FILE_PATH, self.SCOPES)
        credentials = flow.run_local_server(port=0)

        try:
            service = build(self.SERVICE_NAME, self.VERSION,
                            credentials=credentials, cache_discovery=False)
            return service

        except HttpError as err:
            logging.error(err)


class GoogleServiceAccount:
    def __init__(self, file_path, scopes, service_name, version):
        """
        Google Service Account Auth
        :param file_path: service account json file
        :type file_path: str
        :param scopes: e.g. ["https://www.googleapis.com/auth/indexing"]
        :type scopes: list
        :param service_name: e.g. 'indexing'
        :type service_name: str
        :param version: e.g. 'v3'
        :type version: str
        """
        self.SERVICE_ACCOUNT_FILE = file_path
        self.SCOPES = scopes
        self.SERVICE_NAME = service_name
        self.VERSION = version

    def auth(self):
        credentials = Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES
        )
        try:
            client = build(self.SERVICE_NAME, self.VERSION,
                           credentials=credentials, cache_discovery=False)
            return client

        except HttpError as err:
            logging.error(err)

