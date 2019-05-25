from feed import Feed 
import strip 

import threading
import feedparser
import time
import datetime
import sqlite3


class Refresher(threading.Thread):
    def __init__(self, queue, logger):
        threading.Thread.__init__(self)
        self.queue = queue        
        self.logger = logger
        self.running = True

    def run(self):
        self.conn = sqlite3.connect('feeds.sqlite')
        self.conn.row_factory = sqlite3.Row
        while self.running:
            self.logger.info("Run")
            cursor = self.conn.execute("select count(*) FROM feeds")
            n = cursor.fetchone()[0]
            cursor.close()
            self.logger.info('{} feeds to refresh'.format(n))
            cursor = self.conn.execute('select * from feeds')
            items = []
            for row in cursor.fetchall():
                now = time.time()
                self.logger.debug('Refreshing [{}] <{}>'.format(row['feedname'], row['url']))
                parsed = feedparser.parse(row['url'])
                for e in parsed.entries:
                    if 'published_parsed' in e:
                        published = time.mktime(e.published_parsed)
                        self.logger.debug('Published: {} -  updated: {}'.format(datetime.datetime.fromtimestamp(published), datetime.datetime.fromtimestamp(row['updated'])))
                        if 'link' in e and published > row['updated']:
                            feed = Feed(e.link)
                            if 'description' in e:
                                feed.description = strip.strip_html(e.description)
                            if 'title' in e:
                                feed.title = e.title
                            feed.updated = published
                            feed.feedid = row['id']
                            feed.feedtitle = row['feedname']
                            feed.feedurl = row['url']
                            self.logger.info('Add item to queue')
                            self.logger.debug('\t{}'.format(feed.link))
                            self.logger.debug('\t{}'.format(feed.description))
                            self.queue.put(feed)
                            
                
                self.update(row['id'], now)
            time.sleep(60)

    def stop(self):
        self.conn.close()
        self.running = False

    def update(self, feedid, now):
        self.logger.info("Update feed id {}".format(feedid))
        cursor = self.conn.cursor()
        cursor.execute("update feeds set updated = ? where id = ?", (now, feedid))
        self.conn.commit()
        cursor.close()

