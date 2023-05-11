import logging
import random
import re
import sys
from bs4 import BeautifulSoup
from queue import PriorityQueue, Queue
from urllib import parse, request

logging.basicConfig(level=logging.DEBUG, filename='output.log', filemode='w')
visitlog = logging.getLogger('visited')
extractlog = logging.getLogger('extracted')

base = -1
solution = ""

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
            count = link.count('/')
            q.put((count, link))

    return q


def get_links(url):
    res = request.urlopen(url)
    return list(parse_links(url, res.read().decode('utf-8')))


def get_nonlocal_links(url):
    '''Get a list of links on the page specificed by the url,
    but only keep non-local links and non self-references.
    Return a list of (link, title) pairs, just like get_links()'''

    links = get_links(url)
    o = parse.urlparse(url)
    domain = o.netloc
    filtered = []
    for link, title in links:
        if (parse.urlparse(link).netloc != domain and parse.urlparse(link).netloc != "www." + domain and (not check_self_referencing(link))): # check non-locality
            filtered.append((link, title))
    return filtered

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

    visited = []
    extracted = []

    while not queue.empty():
        url = queue.get()[1]
        if(url in visited):
            continue
        if within_domain:
            o = parse.urlparse(url)
            domain = o.netloc
            if (domain != parse.urlparse(root).netloc and domain != "www." + parse.urlparse(root).netloc):
                continue
        try:
            req = request.urlopen(url)
            html = req.read().decode('utf-8')
            if len(wanted_content) > 0 and req.headers['Content-Type'] not in wanted_content:
                continue
            visited.append(url)
            visitlog.debug(url)
            for ex in extract_information(url, html):
                extracted.append(ex)
                extractlog.debug(ex)
            q = parse_links_sorted(url, html)
            if base == 2 and classifier(url, html) == 2:
                solution = 2
            if base == 0 and classifier(url, html) == 1:
                solution = 1
            if base == 1 and classifier(url, html) == 0:
                solution = 0
            if solution == base:
                solution = -1
            while not q.empty():
                x, y = q.get()
                queue.put((x, y))
        except Exception as e:
            print(e, url)

    return visited, extracted


def extract_information(address, html):
    '''Extract contact information from html, returning a list of (url, category, content) pairs,
    where category is one of NEWS, TOPIC'''
    results = []
    for match in re.findall('(?i)\bnews\b', str(html)):
        results.append((address, 'NEWS', match))
    for match in re.findall('(?i)\babortion\b', str(html)):
        results.append((address, 'TOPIC', match))
    return results


def writelines(filename, data):
    with open(filename, 'w') as fout:
        for d in data:
            print(d, file=fout)

def classifier(url, html):
    soup = BeautifulSoup(html, 'html.parser')
    data = []

    for x in soup.find_all('p', class_ = ""):
        data.append(x.get_text(strip = True))

    data = " ".join(data)
    data = data.replace("\n", " ")

    options = [0, 1, 2]
    result = random.choice(options)
    
    return result

def main():
    site = sys.argv[1]
    req = request.urlopen(site)
    html = req.read().decode('utf-8')
    base = classifier(site, html)

    links = get_links(site)
    writelines('links.txt', links)

    nonlocal_links = get_nonlocal_links(site)
    writelines('nonlocal.txt', nonlocal_links)

    visited, extracted = crawl(site)
    writelines('visited.txt', visited)
    writelines('extracted.txt', extracted)

    print(base)
    print(solution)


if __name__ == '__main__':
    main()
