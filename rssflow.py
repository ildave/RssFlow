#https://docs.python-guide.org/dev/virtualenvs/
from feed import Feed
from refresher import Refresher
from shower import Shower

import feedparser
import requests


import time
import datetime
import sqlite3
from xml.dom.minidom import parse
import argparse
import logging
import queue

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

def main():
    
    conn = sqlite3.connect('feeds.sqlite')
    conn.row_factory = sqlite3.Row
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--load', help='Load a opml file and import it')
    parser.add_argument('--refresh', help='Refresh feeds', action='store_true')
    parser.add_argument('--add_feed', help='Add a new rss or atom feed')
    parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger('main')

    
    if args.load:
        logging.info('Load OPML')
        opml = args.load
        load_opml(opml, conn)
    
    if args.refresh:
        logger.info('Refresh feeds')
        data_queue = queue.Queue()
        refresher = Refresher(data_queue, logging.getLogger('refresher'))
        shower = Shower(data_queue, logging.getLogger('shower'))
        refresher.start()
        shower.start()

    
    if args.add_feed:
        logging.info('Add feed')
        feed_url = args.add_feed
        now = time.time()
        add_feed(feed_url, now, conn)

    conn.close()
    

if __name__ == "__main__":
    main()
