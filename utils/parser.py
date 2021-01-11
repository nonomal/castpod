from bs4 import BeautifulSoup
def parse_opml(f):
    feeds = []
    soup = BeautifulSoup(f, 'lxml', from_encoding="utf-8")
    for podcast in soup.find_all(type="rss"):
        print(podcast.attrs.values())
        # _, name, url = podcast.attrs.values()
        # feeds.append({"name":name, "url":url})
    return feeds