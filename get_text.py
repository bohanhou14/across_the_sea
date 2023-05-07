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
    # print(soup.get_text())
    for item in soup.find_all('p', class_ = ""):
        texts.append(item.get_text(strip = True))
    texts = " ".join(texts)
    texts = texts.replace("\n", " ")
    return texts
        
def main():
    site = sys.argv[1]
    text = get_text(site)
    print(text)

if __name__ == '__main__':
    main()