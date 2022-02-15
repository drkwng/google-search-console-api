import logging

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import httplib2
from oauth2client.service_account import ServiceAccountCredentials

from googleapiclient.errors import HttpError


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
            service = build(self.SERVICE_NAME, self.VERSION, credentials=credentials)
            return service

        except HttpError as err:
            logging.error(err)


class GoogleServiceAccount:
    def __init__(self, file_path, scopes):
        """
        Google Service Account Auth for Google Indexing API
        :param file_path: service account json file
        :type file_path: str
        :param scopes: e.g. ["https://www.googleapis.com/auth/indexing"]
        :type scopes: list
        """
        self.SERVICE_ACCOUNT_FILE = file_path
        self.SCOPES = scopes

    def auth(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES
        )
        try:
            http = credentials.authorize(httplib2.Http())
            return http

        except HttpError as err:
            logging.error(err)


if __name__ == "__main__":
    SCOPES = ['https://www.googleapis.com/auth/webmasters']
    CLIENT_SECRET = 'client_secret.json'
    SERVICE_NAME = 'searchconsole'
    VERSION = 'v1'

    google_api = GoogleOAuth(CLIENT_SECRET, SCOPES, SERVICE_NAME, VERSION)
    auth = google_api.auth()
    print(dir(auth))

