import json
from channels.generic.websocket import AsyncWebsocketConsumer


class UploadProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        # Accept the WebSocket connection
        await self.accept()

        self.group_name = 'upload_status'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def checksum_mismatch(self, event):

        mismatch = event.get('mismatch', True)

        data = {
            **mismatch
        }

        data['message'] = 'Checksum mismatch. Please retry the upload.'

        await self.send(text_data=json.dumps(data))
