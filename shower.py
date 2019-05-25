import time
import datetime
import threading

class Shower(threading.Thread):
    def __init__(self, queue, logger):
        threading.Thread.__init__(self)
        self.queue = queue
        self.logger = logger
        self.running = True

    def run(self):
        while self.running:
            self.logger.info("Run - {} items".format(self.queue.qsize()))
            if not self.queue.empty():

                item = self.queue.get()
                self.show(item)
            time.sleep(60)

    def stop(self):
        self.running = False

    def show(self, item):
        print('-'* 40)
        print('|[{}] - {}'.format(item.feedtitle, item.title))
        print('-'* 40)
        print(item.description)
        print('.'*40)
        print('\t{}'.format(datetime.datetime.fromtimestamp(item.updated)))
        print('\t[{}]'.format(item.link))
        print('='*40)