from channels.generic.websocket import WebsocketConsumer
import docker, threading, logging, json, math
# from random import randint
# from time import sleep

logger = logging.getLogger('django')

class CommandConsumer(WebsocketConsumer):
    def connect(self):
      self.container_id = self.scope['url_route']['kwargs']['cid']
      self.accept()
      self.client=docker.APIClient()
      self.send(text_data=self.client.logs(self.container_id,stdout=True, stderr=True).decode('utf-8'))
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

class DetailConsumer(WebsocketConsumer):
  def connect(self):
    self.container_id = self.scope['url_route']['kwargs']['cid']
    self.accept()
    self.client=docker.APIClient()
    client = docker.from_env()
    container = client.containers.get(self.container_id)

    for stats in container.stats(stream=True, decode=True):
        total_usage = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        online_cpus = stats['cpu_stats']['online_cpus']

        total_cpu_percentage = round((total_usage / (online_cpus * 1e9)) * 100, 2)
        container_cpu_percentage = total_cpu_percentage * online_cpus

        memory_usage = stats['memory_stats']['usage']
        memory_limit = stats['memory_stats']['limit']

        memory_percentage = round((memory_usage / memory_limit) * 100, 2)

        self.send(json.dumps(
            {
              'total_cpu_percentage': total_cpu_percentage,
              'container_cpu_percentage': container_cpu_percentage,
              'memory_percentage': memory_percentage
            }
          )
        )

  def disconnect(self, close_code):
    self.stop_thread=True
    self.socket._sock.send('stop\r\n'.encode('utf-8'))

    self.socket.close()

    # self.client.stop(self.container_id)
    self.client.wait(self.container_id)
    self.client.remove_container(self.container_id)

    self.client.close()
