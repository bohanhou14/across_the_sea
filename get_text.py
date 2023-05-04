import re
import sys
from bs4 import BeautifulSoup
from queue import PriorityQueue, Queue
from urllib import parse, request

def get_text(url):
    res = request.urlopen(url)
    html = res.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    texts = []
    for text in soup.find_all('p'):
        text = remove_links(text)
        text = " ".join(text)
        texts.append(text)
    texts = " ".join(texts)
    texts = texts.replace("\n", " ")
    texts = " ".join(texts.split(" "))
    return texts
        
# remove the links in the list and preserve the texts
def remove_links(data):
    return [elem if str(elem)[0] != "<" and elem[0] != ">" else "" for elem in data]
def main():
    site = sys.argv[1]
    text = get_text(site)
    print(text)

if __name__ == '__main__':
    main()