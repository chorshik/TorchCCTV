import json
from pathlib import Path

from channels.generic.websocket import AsyncWebsocketConsumer

from stream import AsyncWebClient


async def async_gen(cl):
    return await cl.get_frames()


class VideoStream(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.cl = None

    async def connect(self):
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connection',
            'data': {
                'message': "Connected to server"
            }
        }))

    async def websocket_disconnect(self, message):
        print('web_dis')
        await super().websocket_disconnect(message)

    async def disconnect(self, code):
        print('dis')
        await super().disconnect(code)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # print(text_data_json)

        event_type = text_data_json['type']
        # print(event_type)

        if event_type == 'receive':
            hostname = text_data_json['data']['hostname']

            self.cl = AsyncWebClient(moc=True, address="tcp://{}:{}".format('127.0.0.1', 9998), cam=False,
                                     path=Path(__file__).parent, key_name='client', server_pub_key='server2',
                                     hostname=hostname)
            try:
                while True:
                    frame = await async_gen(self.cl)
                    dict_data = {'frame': frame.tolist()}
                    data_json = {
                        'type': 'video_stream',
                        'data': dict_data,
                    }

                    await self.send(text_data=json.dumps(data_json))
                    # await self.send(bytes_data=frame.tobytes())

            except Exception as e:
                await self.close()
