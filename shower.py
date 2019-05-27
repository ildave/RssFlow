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
            print('§', flush=True)
            self.logger.info("Run - {} items".format(self.queue.qsize()))
            if not self.queue.empty():

                item = self.queue.get()
                self.show(item)
            time.sleep(60)

    def stop(self):
        self.running = False

    def show(self, item):
        print('-'* 40, flush=True)
        print('|[{}] - {}'.format(item.feedtitle, item.title), flush=True)
        print('-'* 40, flush=True)
        print(item.description, flush=True)
        print('.'*40, flush=True)
        print('\t{}'.format(datetime.datetime.fromtimestamp(item.updated)), flush=True)
        print('\t[{}]'.format(item.link), flush=True)
        print('='*40, flush=True)