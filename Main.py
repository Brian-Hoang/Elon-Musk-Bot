# Elon Musk Bot
# Brian Hoang, Marwan Kodeih, Devin Ashmore
#
# Recommended to run on a Mac

import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import requests
import urllib
import re
import glob
import ast


# Clean up cleanfiles and extract frequent terms
def extract_clean():
    cum_text = ""
    # Loop over every file, lower case, remove punctuation, and add to cumulative text
    for file in glob.glob('cleanfile*.txt'):
        with open(file, 'r') as f:
            text = f.read()
            text = text.lower()
            text = re.sub(r'\W', ' ', text)
            cum_text += text

    # Grab tokens and remove stop words
    tokens = nltk.word_tokenize(cum_text)
    tokens = [word for word in tokens if word not in stopwords.words('english')]

    # Create dict of unique words where value is frequency
    uniq_dict = {}
    for token in tokens:
        if token not in uniq_dict:
            uniq_dict[token] = 1
        else:
            uniq_dict[token] += 1

    print("Top 30 most frequent terms: ")
    # Sort list and print it
    for key in sorted(uniq_dict, key=uniq_dict.get, reverse=True)[:30]:
        print(key, ':', uniq_dict[key])

    # for every top term...
    # for every cleanfile...
    # for every sentence...
    # if a word in the sentence matches the top term, add the sentence to a list
    templist = []
    with open('top_terms.txt', 'r') as terms:
        for term in terms:
            for file in glob.glob('cleanfile*.txt'):
                with open(file, 'r') as f:
                    text = f.read()
                    sents = ast.literal_eval(text)  # convert string to list
                    for sent in sents:
                        if term in sent:
                            templist.append(sent)

    # write the list into a knowledge base file
    with open('knowledge_base.txt', 'w') as f:
        f.write(str(templist))


# function to clean and tokenize scraped text/sentences
# note: processedfiles only have tabs and newlines removed
# note: cleanfiles are the ones that have been manually cleaned afterwards, so do not override those
def cleaner():
    counter = 0
    # for every rawfile in directory...
    # remove newlines and tabs and extract sentences with NLTKs sentence tokenizer
    # write the sentences for each file to a new file. (if you have 15 files in, you have 15 files out)
    for file in glob.glob('rawfile*.txt'):
        with open(file, 'r') as f:
            text = f.read()
            text = text.replace('\n', '').replace('\r', '')  # replace newlines with spaces
            text = text.replace('\t', '').replace('\r', '')  # replace tabs with spaces
            print(file)
            tokens = nltk.sent_tokenize(text)  # tokenize text
            with open('processedfile{}.txt'.format(counter), 'w') as f2:
                f2.write(str(tokens))
            counter += 1

    # end of function
    print("end of cleaner")


# function to determine if an element is visible
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True


# function to gather text from urls
def scraper():
    with open('urls.txt') as f:
        lines = f.readlines()
        lines = [url.strip() for url in lines]  # remove empty lines
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
                    f2.write(temp_str)  # write scraped text to files

    # end of function
    print("end of scraper")


# function to gather relevant urls from a starter url
def crawler():
    starter_url = "https://en.wikipedia.org/wiki/Elon_Musk"  # crawling will start here

    r = requests.get(starter_url)

    data = r.text
    soup = BeautifulSoup(data)
    url_count = 0

    # write urls to a file
    with open('urls.txt', 'w') as f:
        for link in soup.find_all('a'):
            link_str = str(link.get('href'))
            print(link_str)
            if 'Musk' in link_str or 'musk' in link_str:  # only crawl if 'musk' is present
                if url_count >= 20:  # crawling 20 instead of 15 in case of bad URLs
                    break
                if link_str.startswith('/url?q='):
                    link_str = link_str[7:]
                    print('MOD:', link_str)
                if '&' in link_str:
                    i = link_str.find('&')
                    link_str = link_str[:i]
                if link_str.startswith('http') and 'wikipedia' not in link_str:  # don't include wiki links
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
    extract_clean()
    

if __name__ == "__main__":
    main()