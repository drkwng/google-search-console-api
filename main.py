################################################
# Google Search Console & Indexing API Tools
# by @drkwng (https://drkwng.rocks)
################################################

import os
import re
import csv
import logging

from datetime import date, timedelta

from gsc_api import indexing, search_analytics


def choose_tool():
    print('Choose tool (enter number) \n'
          '1 - Keywords from Google Search Console\n'
          '2 - Check URLs indexation and other params\n'
          '3 - Send URLs to Googlebot')
    while True:
        mode = input('').strip()
        if int(mode) not in [1, 2, 3]:
            print('Please enter the correct number (1, 2 or 3)\n')
        else:
            break
    return mode


def search_api_key(mask):
    r = re.compile(f"{mask}.*")
    files = os.listdir()
    key = list(filter(r.match, files))
    if len(key) > 0:
        key = key[0]
    else:
        while True:
            key = input(f'{mask} json key file not found. Please enter your json key filename below:\n')
            if key in files:
                break
    return key


def normalize_resource_name():
    name = input('Enter the Google Search Console resource name\n').strip()
    if 'http' not in name:
        name = f'sc-domain:{name}'
    elif not name.endswith('/'):
        name += '/'
    return name


def get_file():
    while True:
        file = input('Enter the txt filename:\n').strip()
        if file in os.listdir():
            break
        else:
            print('Please enter a correct filename')
    return file


def keywords_to_csv(file, mode, dimensions, result):
    res_folder = '\\results\\'
    path = os.getcwd() + res_folder + file
    with open(path, mode, encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        if mode == 'w':
            heading = dimensions
            heading += ['clicks', 'impressions', 'ctr', 'position']
            writer.writerow(heading)

        for elem in result['rows']:
            row = [key for key in elem['keys']]
            row += [elem['clicks'], elem['ctr'], elem['impressions'], elem['position']]
            writer.writerow(row)


def check_index_to_csv(file, result):
    res_folder = '\\results\\'
    path = os.getcwd() + res_folder + file
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        heading = ['url', 'coverageState', 'robotsTxtState', 'indexingState', 'lastCrawlTime',
                   'googleCanonical', 'userCanonical', 'mobileUsabilityResult']
        writer.writerow(heading)

        for key, value in result.items():
            row = [key]
            if value is not None:
                row += [
                    value['inspectionResult']['indexStatusResult']['coverageState'],
                    value['inspectionResult']['indexStatusResult']['robotsTxtState'],
                    value['inspectionResult']['indexStatusResult']['indexingState'],
                    value['inspectionResult']['indexStatusResult']['lastCrawlTime'],
                ]
                try:
                    row += [
                        value['inspectionResult']['indexStatusResult']['googleCanonical'],
                        value['inspectionResult']['indexStatusResult']['userCanonical']
                    ]
                except KeyError:
                    row += [None, None]

                try:
                    row.append(value['inspectionResult']['mobileUsabilityResult']['verdict'])
                except KeyError:
                    row.append(None)
            else:
                row.append(value)

            writer.writerow(row)


def init_get_keywords(key):
    resource = normalize_resource_name()

    today = date.today()

    while True:
        num_months = input('Please enter number of months period (1-16) you want to get data '
                           'or press Enter to get data with the default 16 months period:\n').strip()
        if 16 > int(num_months) > 0:
            start_date = str(today - timedelta(days=int(num_months)*30))
            break
        elif len(num_months) == 0:
            start_date = str(today - timedelta(days=486))
            print(f'Start date is: {start_date}')
            break
        else:
            print("Please enter the number in 1 to 16 range or press Enter")

    end_date = str(date.today() - timedelta(days=1))

    available_dimensions = ["date", "query", "page", "country", "device", "search_appearance"]
    while True:
        dimensions = list(input(f"Please input one of the available dimensions \n"
                                f"{available_dimensions} divided by ',' WITHOUT SPACES\n"
                                f"or press Enter to get data with the 'query' dimension:\n").strip().split(','))
        if set(dimensions).issubset(set(available_dimensions)):
            break
        elif len(dimensions) == 0:
            dimensions = ['query', ]
            print("You chose a 'query' dimension")
            break
        else:
            print("Please enter correct dimensions or press Enter")

    get_keywords = search_analytics.GetData(key, resource)
    print('Keywords parsing has started. \n'
          'Please wait and stay calm ^_____^')

    result = get_keywords.worker(start_date, end_date, dimensions=dimensions)

    res_file = 'search_analytics.csv'
    for num, elem in enumerate(result):
        keywords_to_csv(res_file, 'w' if num == 0 else 'a', dimensions, elem)

    print(f'Done! Check the {res_file} file in "results/" folder')


def init_indexation_check(key, file):
    resource = normalize_resource_name()
    data = {}

    with open(file, 'r', encoding='utf-8') as f:
        data[resource] = [url.strip() for url in f]

    check_index = indexing.CheckIndexation(key)
    print('URLs indexation check has started. \n'
          'Please wait and stay calm ^_____^')
    result = check_index.worker(data)

    res_file = 'check_urls.csv'
    check_index_to_csv(res_file, result)

    print(f'Done! Check the {res_file} file in "results/" folder')


def init_send_urls(key, file):
    while True:
        choose_msg = input('\nChoose one of methods (print number) and press Enter \n'
                           '1 - URL_UPDATED\n'
                           '2 - URL_DELETED:\n')
        if '1' in choose_msg:
            method = 'URL_UPDATED'
            break
        elif '2' in choose_msg:
            method = 'URL_DELETED'
            break
        else:
            print('Please enter correct number')

    with open(file, 'r', encoding='utf-8') as f:
        urls = [url.strip() for url in f]

    index = indexing.Indexation(key)
    print('URLs sending to Googlebot has started. \n'
          'Please wait and stay calm ^_____^')
    if 100 < len(urls) <= 200:
        index.worker(urls[:99], method)
        index.worker(urls[100:], method)
        print(f'Done! Check the logs.log file in "logs/" folder')
    elif len(urls) < 100:
        index.worker(urls, method)
        print(f'Done! Check the logs.log file in "logs/" folder')
    else:
        print('You are trying to send more than 200 URLs. \n'
              'There is a 200 URLs quota =(')
        exit()


def main():
    tool = choose_tool()
    path = os.getcwd()

    logging.basicConfig(level=logging.INFO, filename=f'{path}/logs/logs.log')

    api_key = search_api_key('client_secret')
    if int(tool) == 1:
        init_get_keywords(api_key)

    elif int(tool) == 2:
        file = get_file()
        init_indexation_check(api_key, file)

    elif int(tool) == 3:
        file = get_file()
        init_send_urls(api_key, file)


if __name__ == "__main__":
    main()

    # Old clear not unique values func for Keywords Search Analytics results
    # One day it will be back :-)
    # def clear_not_unique(self):
    #     with open(self.file, 'r', encoding='utf-8', newline='') as f:
    #         reader = csv.reader(f, delimiter=';')
    #         all_keys = {rows[0]: rows[1:] for rows in reader}
    #     with open(self.file, 'w', encoding='utf-8', newline='') as f:
    #         writer = csv.writer(f, delimiter=';')
    #         for _key, _value in all_keys.items():
    #             row = [_key, _value[0], _value[1], _value[2], _value[3], _value[4]]
    #             writer.writerow(row)
