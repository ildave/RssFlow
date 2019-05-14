#https://docs.python-guide.org/dev/virtualenvs/
import feedparser
import requests
from bs4 import BeautifulSoup, NavigableString

import time
import datetime
import sqlite3
from xml.dom.minidom import parse
"""
 create table feeds(id INTEGER PRIMARY KEY, url TEXT, updated INTEGER)
 """
def load_opml(opml):
    dom = parse(opml)
    outlines = dom.getElementsByTagName('outline')

    feeds = []

    for o in outlines:
        if o.hasAttribute('type') and o.getAttribute('type') == 'rss':
            url = o.getAttribute('xmlUrl')
            try:
                response = requests.head(url)
                print(url, response.status_code)
                if response.status_code < 400:
                    feeds.append(url)
            except:
                pass

    print("="*60)

    db = records.Database('sqlite:///feeds.sqlite')
    now = 1557738000
    for f in feeds:
        print(f)
        db.query("insert into feeds(url, updated) values(:theurl, :thetime)", theurl=f, thetime=now)

def strip_html(src):
    p = BeautifulSoup(src, features='html.parser')
    text = p.findAll(text=lambda text:isinstance(text, NavigableString))
 
    return u" ".join(text)

conn = sqlite3.connect('feeds.sqlite')
conn.row_factory = sqlite3.Row

cursor = conn.cursor()
cursor.execute('select * from feeds')
items = []
for r in cursor.fetchall():
    print(r['url'])
    parsed = feedparser.parse(r['url'])
    if parsed.feed.has_key('title'):
        print(parsed.feed.title)
    if parsed.feed.has_key('link'):
        print(parsed.feed.link)
    for e in parsed.entries:
        if e.has_key('published_parsed'):
            published = time.mktime(e.published_parsed)
            if published > r['updated']:
                item = {'feedid': r['id'], 'description': strip_html(e.description), 'link': e.link, 'published': published}
                items.append(item)
    print('='*40)

cursor.close()
conn.close()

for item in items:
    print(item)

