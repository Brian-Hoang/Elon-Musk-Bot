import sys
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import defaultdict
from bs4 import BeautifulSoup
import requests
import urllib.request
import re
import glob


def cleaner():
    counter = 0
    # for every rawfile in directory...
    # remove newlines and tabs
    # extract sentences with NLTK’s sentence tokenizer
    # write the sentences for each file to a new file. (if you have 15 files in, you have 15 files out)
    for file in glob.glob('rawfile*.txt'):
        with open(file, 'r') as f:
            text = f.read()
            text = text.replace('\n', '').replace('\r', '')  # replace newlines with spaces
            text = text.replace('\t', '').replace('\r', '')  # replace tabs with spaces
            # tokens = nltk.word_tokenize(text)  # tokenize text
            tokens = nltk.sent_tokenize(text)  # tokenize text
            with open('processedfile{}.txt'.format(counter), 'w') as f2:
                f2.write(str(tokens))
            counter += 1


# function to determine if an element is visible
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True


def scraper():
    with open('urls.txt') as f:
        lines = f.readlines()
        lines = [url.strip() for url in lines]
        for counter, url in enumerate(lines):
            if url:
                print(url)
                try:
                    html = urllib.request.urlopen(url)
                except:
                    continue  # if URL is invalid, don't end program
                soup = BeautifulSoup(html)
                data = soup.findAll(text=True)
                result = filter(visible, data)
                temp_list = list(result)  # list from filter
                temp_str = ' '.join(temp_list)
                with open('rawfile{}.txt'.format(counter), 'w') as f2:
                    f2.write(temp_str)

    # end of function
    print("end of scraper")


def crawler():
    starter_url = "https://en.wikipedia.org/wiki/Elon_Musk"

    r = requests.get(starter_url)

    data = r.text
    soup = BeautifulSoup(data)
    url_count = 0

    # write urls to a file
    with open('urls.txt', 'w') as f:
        for link in soup.find_all('a'):
            link_str = str(link.get('href'))
            print(link_str)
            if 'Musk' in link_str or 'musk' in link_str:
                if url_count >= 20:  # crawling 20 instead of 15 in case of bad URLs
                    break
                if link_str.startswith('/url?q='):
                    link_str = link_str[7:]
                    print('MOD:', link_str)
                if '&' in link_str:
                    i = link_str.find('&')
                    link_str = link_str[:i]
                if link_str.startswith('http') and 'wikipedia' not in link_str:
                    f.write(link_str + '\n')
                    url_count += 1

    with open('urls.txt', 'r') as f:
        urls = f.read().splitlines()
    for u in urls:
        print(u)

    # end of function
    print("end of crawler")


def main():
    crawler()
    scraper()
    cleaner()

if __name__ == "__main__":
    main()