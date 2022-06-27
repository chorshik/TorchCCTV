import json
from pathlib import Path
from channels.generic.websocket import AsyncWebsocketConsumer

from stream import AsyncWebClient


async def async_gen(cl):
    return await cl.get_frames()


class VideoStream(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connection',
            'data': {
                'message': "Connected to server"
            }
        }))

    def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)

        eventType = text_data_json['type']

        if eventType == 'receive':
            hostname = text_data_json['data']['hostname']
            # print(hostname)

            cl = AsyncWebClient(moc=True, address="tcp://{}:{}".format('127.0.0.1', 9998), cam=False,
                                path=Path(__file__).parent, key_name='client', server_pub_key='server2',
                                hostname=hostname)

            while True:
                frame = await async_gen(cl)

                await self.send(bytes_data=frame.tobytes())
