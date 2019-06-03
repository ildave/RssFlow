import asyncio
import websockets
import logging
import queue

async def send_items(websockets, path):


async def hello(websocket, path):
    while True:
        print('§', flush=True)
        self.logger.info("Run - {} items".format(self.queue.qsize()))
        if not self.queue.empty():

            item = self.queue.get()
            self.show(item)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        await websocket.send(now)
        await asyncio.sleep(random.random() * 3)

data_queue = queue.Queue()
refresher = Refresher(data_queue, logging.getLogger('refresher'))
refresher.start()

start_server = websockets.serve(hello, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()