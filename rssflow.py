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
import logging

def load_opml(opml, conn):
    logger.info('opml file: {}'.format(opml))
    dom = parse(opml)
    outlines = dom.getElementsByTagName('outline')

    feeds = []

    for o in outlines:
        if o.hasAttribute('type') and o.getAttribute('type') == 'rss':
            url = o.getAttribute('xmlUrl')
            feedname = o.getAttribute('title')
            try:
                response = requests.head(url)
                logging.debug('<{}> - response code: {}'.format(url, response.status_code))
                if response.status_code < 400:
                    feed = {'url': url, 'name': feedname}
                    feeds.append(feed)
                else:
                    logging.info('[{}] - <{}> - Link is broken'.format(feedname, url))
            except:
                logging.warning('Error while retrieving <{}>'.format(url))

    print("="*60)
    

    now = time.time() - 60*60*24 #default to yesterday
    for f in feeds:
        print(f)
        url = f['url']
        feedname = f['name']
        cursor = conn.cursor()
        logging.debug('Execute query: [insert into feeds(url, updated, feedname) values({}, {}, {})]'.format(url, now, feedname))
        cursor.execute("insert into feeds(url, updated, feedname) values(?, ?, ?)", (url, now, feedname))
        conn.commit()
        cursor.close()

def add_feed(url, now, conn):
    logging.info('Feed url [{}]'.format(url))
    feed =  feedparser.parse(url)
    title = feed.feed.title
    now = now - 60*60*24 #yesterday
    cursor = conn.cursor()
    logging.debug('Execute query: [insert into feeds(url, updated, feedname) values({}, {}, {})]'.format(url, now, title))
    cursor.execute("insert into feeds(url, updated, feedname) values(?, ?, ?)", (url, now, title))
    conn.commit()
    cursor.close()

def strip_html(src):
    p = BeautifulSoup(src, features='html.parser')
    text = p.findAll(text=lambda text:isinstance(text, NavigableString))
 
    return u" ".join(text)

def refresh(conn):
    cursor = conn.execute("select count(*) FROM feeds")
    n = cursor.fetchone()[0]
    cursor.close()
    logging.info('{} feeds to refresh'.format(n))
    cursor = conn.execute('select * from feeds')
    items = []
    for row in cursor.fetchall():
        logging.debug('Refreshing [{}] <{}>'.format(row['feedname'], row['url']))
        parsed = feedparser.parse(row['url'])
        for e in parsed.entries:
            if 'published_parsed' in e:
                published = time.mktime(e.published_parsed)
                logging.debug('Published: {} -  updated: {}'.format(published, row['updated']))
                if 'link' in e and published > row['updated']:
                    feed = Feed(e.link)
                    if 'description' in e:
                        feed.description = strip_html(e.description)
                    if 'title' in e:
                        feed.title = e.title
                    feed.updated = published
                    feed.feedid = row['id']
                    feed.feedtitle = row['feedname']
                    feed.feedurl = row['url']
                    items.append(feed)
                    logging.debug('\t{}'.format(feed.link))
                    logging.debug('\t{}'.format(feed.description))
    items.sort(key=lambda x: x.updated)
    logging.info('{} new items found'.format(len(items)))
    return items

def update(items, now, conn):
    logging.info('Updated value for feeds: {}'.format(datetime.datetime.fromtimestamp(now)))
    feedids = set()
    for i in items:
        feedids.add(i.feedid)

    for feedid in feedids:
        cursor = conn.cursor()
        cursor.execute("update feeds set updated = ? where id = ?", (now, feedid))
        conn.commit()
        cursor.close()

def show(items):
    for i in items:
        print('-'* 40)
        print('|[{}] - {}'.format(i.feedtitle, i.title))
        print('-'* 40)
        print(i.description)
        print('.'*40)
        print('\t{}'.format(datetime.datetime.fromtimestamp(i.updated)))
        print('\t[{}]'.format(i.link))
        print('='*40)

def main():
    logging.basicConfig(level=logging.INFO)

    conn = sqlite3.connect('feeds.sqlite')
    conn.row_factory = sqlite3.Row

    parser = argparse.ArgumentParser()
    parser.add_argument('--load', help='Load a opml file and import it')
    parser.add_argument('--refresh', help='Refresh feeds', action='store_true')
    parser.add_argument('--add_feed', help='Add a new rss or atom feed')
    args = parser.parse_args()
    if args.load:
        logging.info('Load OPML')
        opml = args.load
        load_opml(opml, conn)

    if args.refresh:
        logging.info('Refresh feeds')
        now = time.time()
        items = refresh(conn)
        update(items, now, conn)
        show(items)

    if args.add_feed:
        logging.info('Add feed')
        feed_url = args.add_feed
        now = time.time()
        add_feed(feed_url, now, conn)

    conn.close()


if __name__ == "__main__":
    main()
