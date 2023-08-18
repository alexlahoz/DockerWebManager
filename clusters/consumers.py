from channels.generic.websocket import WebsocketConsumer
import docker
import threading
import logging

logger = logging.getLogger('django')

class CommandConsumer(WebsocketConsumer):
    def connect(self):
        self.container_id = self.scope['url_route']['kwargs']['cid']
        self.accept()
        self.client=docker.APIClient()
        self.send(text_data=self.client.logs(self.container_id,stdout=True, stderr=True).decode('utf-8'))
        # self.send(text_data=self.client.attach(self.container_id,stderr=True,stdout=True,demux=True))
        self.socket=self.client.attach_socket(self.container_id, params={'stdin': 1, 'stream': 1})

        self.stop_thread=False
        self.t = threading.Thread(target=self.send_stream_log)
        self.t.start()

    def disconnect(self, close_code):
        pass
        # self.stop_thread=True
        # self.socket._sock.send('stop\r\n'.encode('utf-8'))

        # self.socket.close()

        # # self.client.stop(self.container_id)
        # self.client.wait(self.container_id)
        # self.client.remove_container(self.container_id)

        # self.client.close()

    def receive(self, text_data):
        self.socket._sock.send(text_data.encode('utf-8'))
        logger.info('CommandConsumer:receive')

    def send_stream_log(self):
        for b in self.client.attach(self.container_id,stderr=True,stdout=True,stream=True,demux=True):
            logger.info(b)
            if self.stop_thread:
                break
            if b[0]:
                self.send(text_data=b[0].decode('utf-8'))
            if b[1]:
                self.send(text_data=b[1].decode('utf-8'))
        logger.info('asdf')
