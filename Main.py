import nltk
from bs4 import BeautifulSoup
from nltk import FreqDist
from nltk.corpus import stopwords
import string
import requests
import urllib.request
import re
import glob
import sys

##Clean up clean files and extract 
def extract_clean():
    fdist_c = FreqDist()
    c_text = "" 

    #loop over every file, replace new lines, lower case, remove punc, add to cum text 
    for file in glob.glob('cleanfile*.txt'):
        with open(file, 'r', encoding="utf8") as f:
            text = f.read()
            text = text.replace("\n", " ")
            text = text.lower()
            text = text.translate(str.maketrans('','',string.punctuation))
            c_text+=text
            
    ##grab tokens and remove stop words 
    tokens = nltk.word_tokenize(text)
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    fdist = FreqDist(tokens)
    #tags = nltk.pos_tag(tokens)
    uniq_dic = {}

    #Create dict of unique words where val is frequency 
    for token in tokens:
        if token not in uniq_dic:
            uniq_dic[token] = 1
        else:
            uniq_dic[token] += 1

    #sort list and print it
    for pos in sorted(uniq_dic, key=uniq_dic.get, reverse=True)[:30]:
        print(pos.encode("utf-8"), ':', uniq_dic[pos])
    

# function to clean and tokenize scraped text/sentences
# note: processedfiles only have tabs and newlines removed
# note: cleanfiles are the ones that have been manually cleaned afterwards, so do not override those
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
