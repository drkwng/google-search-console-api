# Google Search Console API by [DRKWNG](https://drkwng.rocks)

- **Search Analytics API** - get all (ALL!) keywords from Google Search Console.
- **URL Inspection API** - check URLs indexation status and other params for Google.
- **Indexing API** - send up to 200 URLs to Googlebot with URL_UPDATED or URL_DELETED param.

## Activate API and create credentials
### OAuth client ID (Search Analytics and URL Inspection)
1. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/) -> APIs & Services -> Credentials. If it is your first project in Cloud Console create one.
2. Click "Create Credentials" -> "OAuth client ID" (**Application type = Desktop app**) and click "Create".
3. Download JSON and put it in the same folder with the program.
4. Go to APIs & Services -> Library and activate Google Search Console API.
5. Start the program and follow instructions in the console.

## Run Program
1. Made on [Python 3.8.x](https://www.python.org/downloads/) (recommended) 
Tick the "Add to PATH" option during the installation process. 

2. **Install packages:**

`pip install --upgrade google-api-python-client, google-auth-oauthlib, google-auth`

_Type in this command into your terminal._

3. Start Terminal in the program folder and type in:  
`python main.py` or `python3 main.py`
 
4. Enjoy😻


I appreciate your bug reports and suggestions🖖
