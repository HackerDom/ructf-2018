from ws4py.client import WebSocketBaseClient
from ws4py.manager import WebSocketManager
import time
import random

m = WebSocketManager()


class EchoClient(WebSocketBaseClient):
    def handshake_ok(self):
        m.add(self)

    def add_writer(self, link):
        self.writer = link

    def received_message(self, msg):
        self.writer.append(str(msg))


def run_ws(ws_addr, delegate):
    messages = []

    m.start()
    client = EchoClient(ws_addr)
    client.add_writer(messages)
    client.connect()
    time.sleep(random.randint(110, 300) / 100)
    delegate()
    time.sleep(0.5)
    m.close_all()
    m.stop()
    m.join()
    return messages
