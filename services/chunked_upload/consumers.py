import json
from channels.generic.websocket import AsyncWebsocketConsumer


class UploadCompletionConsumer(AsyncWebsocketConsumer):
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

    async def upload_completion(self, event):
        task_id = event['task_id']
        status = event['status']
        await self.send(text_data=json.dumps({
            'task_id': task_id,
            'status': status
        }))
