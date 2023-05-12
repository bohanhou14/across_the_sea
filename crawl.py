import logging
import random
import re
import sys
from bs4 import BeautifulSoup
from queue import PriorityQueue, Queue
from urllib import parse, request
from util import get_text, classify

logging.basicConfig(level=logging.DEBUG, filename='output.log', filemode='w')
visitlog = logging.getLogger('visited')
extractlog = logging.getLogger('extracted')

ideology_map = {
    0: "liberal",
    1: "conservative",
    2: "neutral"
}

def parse_links(root, html):
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            text = link.string
            if not text:
                text = ''
            text = re.sub('\s+', ' ', text).strip()
            yield (parse.urljoin(root, link.get('href')), text)


def parse_links_sorted(root, html):
    q= PriorityQueue(0)
    links = parse_links(root, html)

    for link, title in links:
        if(check_self_referencing(link) == False):
            count = link.count('/') * 10
            if(link.count("abortion") > 0):
                count = count - 100 * link.count("abortion")
            count = count - 1 * link.count("news")
            q.put((count, link))

    return q


def check_self_referencing(url):
    last = url.rfind('/')
    if ('#' in url[last:-1]):
        return True
    return False

def crawl(root, wanted_content=[], within_domain=True):
    '''Crawl the url specified by `root`.
    `wanted_content` is a list of content types to crawl
    `within_domain` specifies whether the crawler should limit itself to the domain of `root`
    '''
    
    queue = PriorityQueue()
    queue.put((10, root))
    ro = parse.urlparse(root)

    while not queue.empty():
        url = queue.get()[1]
        if(url in visited):
            continue
        if within_domain:
            o = parse.urlparse(url)
            domain = o.netloc
            if (domain != ro.netloc and domain != "www." + ro.netloc):
                continue
        try:
            req = request.urlopen(url)
            html = req.read().decode('utf-8')
            if len(wanted_content) > 0 and req.headers['Content-Type'] not in wanted_content:
                continue
            visited.append(url)
            visitlog.debug(url)
            text = get_text(url)
            pred, score = classify(text)
            if pred not in ideologies and len(text.split()) > 100 and "news/" in o.path:
                ex = "alternative article with " + ideology_map[pred] + " ideology found with an extreme score of " + str(score) 
                print(ex)
                ex += "\ntext: " + text + "\n\nurl: " + str(url)
                extracted.append(ex)
                ideologies.add(pred)
            # if all three ideologies are collected, then break the loop and terminate the program
            if len(ideologies) == 3:
                break
            q = parse_links_sorted(url, html)
            while not q.empty():
                x, y = q.get()
                queue.put((x, y))
        except Exception as e:
            print(e, url)

    return visited, extracted

def writelines(filename, data):
    with open(filename, 'w') as fout:
        for d in data:
            print(d, file=fout)

def main():
    site = sys.argv[1]
    article = get_text(site)
    article_ideology, score = classify(article)
    global ideologies, visited, extracted
    ideologies = {article_ideology}
    visited = [] ; extracted = []
    print("The stance of the article on abortion you are reading is: " + str(ideology_map[article_ideology]))
    print("with extremeness: " + str(score))

    # crawl on a conservative abortion website
    crawl("https://www.catholicnewsagency.com/tags/35/abortion")
    # crawl on a liberal abortion website
    crawl("https://www.nbcnews.com/politics/abortion-news")

    writelines('visited.txt', visited)
    writelines('extracted.txt', extracted)

if __name__ == '__main__':
    main()
