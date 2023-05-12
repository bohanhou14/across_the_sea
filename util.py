import re
import sys
from bs4 import BeautifulSoup
from queue import PriorityQueue, Queue
from urllib import parse, request
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from torch.nn.functional import normalize

device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = AutoModelForSequenceClassification.from_pretrained("./abortion_news_model/").to(device)
tokenizer = AutoTokenizer.from_pretrained("launch/POLITICS")

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

def classify(article):
    input_ids = tokenizer(article, return_tensors = "pt", max_length = 512, truncation = True).input_ids.to(device)
    output = model(input_ids).logits
    pred = torch.argmax(output).item()
    score = torch.max(normalize(output, dim = 1)).item()
    return pred, score

        
def main():
    site = sys.argv[1]
    text = get_text(site)
    print(text)
    pred, score = classifier(text)
    print(pred, score)

if __name__ == '__main__':
    main()