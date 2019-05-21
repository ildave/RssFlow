#https://docs.python-guide.org/dev/virtualenvs/
from feed import Feed 

import feedparser
import requests
from bs4 import BeautifulSoup, NavigableString

import time
import datetime
import sqlite3
from xml.dom.minidom import parse
import argparse

def load_opml(opml, conn):
    dom = parse(opml)
    outlines = dom.getElementsByTagName('outline')

    feeds = []

    for o in outlines:
        if o.hasAttribute('type') and o.getAttribute('type') == 'rss':
            url = o.getAttribute('xmlUrl')
            feedname = o.getAttribute('title')
            try:
                response = requests.head(url)
                print(url, response.status_code)
                if response.status_code < 400:
                    feed = {'url': url, 'name': feedname}
                    feeds.append(feed)
            except:
                pass

    print("="*60)
    

    now = 1557738000
    for f in feeds:
        print(f)
        url = f['url']
        feedname = f['name']
        cursor = conn.cursor()
        cursor.execute("insert into feeds(url, updated, feedname) values(?, ?, ?)", (url, now, feedname))
        conn.commit()
        cursor.close()

def strip_html(src):
    p = BeautifulSoup(src, features='html.parser')
    text = p.findAll(text=lambda text:isinstance(text, NavigableString))
 
    return u" ".join(text)

def refresh(conn):
    cursor = conn.execute('select * from feeds')
    items = []
    for row in cursor.fetchall():
        print('[{}] <{}>'.format(row['feedname'], row['url']))
        print('.'*40)
        parsed = feedparser.parse(row['url'])
        for e in parsed.entries:
            if 'published_parsed' in e:
                published = time.mktime(e.published_parsed)
                if 'link' in e and published > row['updated']:
                    feed = Feed(e.link)
                    if 'description' in e:
                        feed.description = strip_html(e.description)
                    feed.updated = published
                    feed.feedid = row['id']
                    feed.feedtitle = row['feedname']
                    feed.feedurl = row['url']
                    items.append(feed)
                    print('\t{}'.format(feed.link))
                    print('\t{}'.format(feed.description))
                    print('='*40)
        print('*'*40)
    items.sort(key=lambda x: x.updated)
    return items

def update(items, now, conn):
    feedids = set()
    for i in items:
        feedids.add(i.feedid)

    for feedid in feedids:
        cursor = conn.cursor()
        cursor.execute("update feeds set updated = ? where id = ?", (now, feedid))
        conn.commit()
        cursor.close()

def main():
    conn = sqlite3.connect('feeds.sqlite')
    conn.row_factory = sqlite3.Row

    parser = argparse.ArgumentParser()
    parser.add_argument('--load', help='Load a opml file and import it')
    parser.add_argument('--refresh', help='Refresh feeds', action='store_true')
    args = parser.parse_args()
    if args.load:
        print(args.load)
        opml = args.load
        load_opml(opml, conn)

    if args.refresh:
        print('Refresh feeds')
        now = time.time()
        items = refresh(conn)
        update(items, now, conn)

    conn.close()


if __name__ == "__main__":
    main()

