import feedparser
from bs4 import BeautifulSoup
def parse_opml(f):
    feeds = []
    soup = BeautifulSoup(f, 'lxml', from_encoding="utf-8")
    for podcast in soup.find_all(type="rss"):
        _, name, url = podcast.attrs.values()
        feeds.append({"name":name, "url":url})
    return feeds

with open('public/subscriptions/429646222.xml', 'r') as f:
    parse_opml(f)