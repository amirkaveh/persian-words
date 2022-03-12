import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import csv
from math import log10
import glob
import os
import re

page_url = "https://dehkhoda.ut.ac.ir/fa/dictionary?page={page_number}&per-page={word_per_page}"
word_url = "https://dehkhoda.ut.ac.ir/fa/dictionary/{word_number}"
word_count = 343_318
word_per_page = 30
page_count = int(word_count / word_per_page) + 1
fill = int(log10(page_count)) + 1
words_path = "dehkhoda/words/"


def fetch_page(page_number: int) -> requests.Response:
    """ Fetch a page from url and return response """
    response = requests.get(
        page_url.format(page_number=page_number, word_per_page=word_per_page))
    return response


def get_records_from_response(response: requests.Response):
    """ Extract word records from response (a fetched page) """
    pageSoup = BeautifulSoup(response.content, 'lxml')
    records = pageSoup.find('table', {'class': 'table'}).find('tbody').find_all('tr')
    return records


def extract_text(summary):
    """ Extract text from a Tag object """
    stack = [
        summary,
    ]
    text = ""
    while len(stack) > 0:
        top = stack.pop(0)
        if isinstance(top, Tag):
            elements = list(top)
            stack = elements + stack
            continue
        text += top
    return text.replace('\n', ' ')


def make_word_list(records):
    """ Make a list of word dicts from records """
    words = list()
    for record in records:
        word = dict()
        tags = record.find_all('td')
        word['num'] = int(tags[0].contents[0])
        word['word'] = extract_text(tags[1].find('a'))
        word['summary'] = extract_text(tags[2])
        words.append(word)
    return words


def get_words(page_number: int):
    """ Get words from a page """
    response = fetch_page(page_number)
    records = get_records_from_response(response)
    words = make_word_list(records)
    return words


def write_csv(words, page_number: int):
    """ Write words to csv file """
    file_name = words_path + 'words-{}.csv'.format(str(page_number).zfill(fill))
    word_info = ['num', 'word', 'summary']
    with open(file_name, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=word_info)
        writer.writeheader()
        writer.writerows(words)


def get_last_file_number():
    """ Get the last saved csv file number """
    list_of_files = glob.glob(words_path + 'words-*.csv')
    try:
        latest_file = max(list_of_files, key=os.path.basename)
        number = re.search(words_path + 'words-(.+?)\.csv', latest_file).group(1)
    except Exception:
        number = '0'
    return int(number)

# Main
if __name__ == '__main__':
    for i in range(get_last_file_number() + 1, page_count + 1):
        words = get_words(i)
        write_csv(words, i)
        print('Page {} is done'.format(i))
    print('Done')
