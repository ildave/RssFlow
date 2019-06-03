import asyncio
import websockets
import logging
import queue
import json
from refresher import Refresher


async def send_items(websocket, path):
    global data_queue
    while True:
        print('§', flush=True)
        if not data_queue.empty():
            item = data_queue.get()
            print(json.dumps(item.to_dict()))
            await websocket.send(json.dumps(item.to_dict()))
        await asyncio.sleep(60)

data_queue = queue.Queue()
refresher = Refresher(data_queue, logging.getLogger('refresher'))
refresher.start()

start_server = websockets.serve(send_items, '127.0.0.1', 8066)


asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()