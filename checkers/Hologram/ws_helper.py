from ws4py.client import WebSocketBaseClient
from ws4py.manager import WebSocketManager
import time

m = WebSocketManager()


class EchoClient(WebSocketBaseClient):
    def handshake_ok(self):
        m.add(self)

    def add_writer(self, link):
        self.writer = link

    def received_message(self, msg):
        self.writer.append(str(msg))


def run_ws(team_addr, x, y, z, rad):
    messages = []

    try:
        m.start()
        client = EchoClient(
            'ws://{}/ws/holograms?x={}&y={}&z={}&rad={}&rad=10000'
            .format(team_addr, x, y, z, rad)
        )
        client.add_writer(messages)
        client.connect()

        while True:
            for ws in m:
                if not ws.terminated:
                   break
            else:
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print(messages)
        m.close_all()
        m.stop()
        m.join()


if __name__ == '__main__':
    run_ws("127.0.0.1:8081", 0, 0, 0, 10)
