from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.core.cache import cache


class ModelsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.selected_coin = None  # Initialize selected coin

        # Accept the WebSocket connection
        await self.accept()

        # Add the consumer to the 'prices_group' group
        await self.channel_layer.group_add(
            'models_group',  # Group name
            self.channel_name  # Channel name
        )

    async def receive(self, text_data):
    data = json.loads(text_data)
        headers = data.get('headers', [])
        first_row = data.get('first_row', [])

        # Analyze data and discover appropriate mod0el and fields
        model_class, field_metadata = self.discover_model_and_fields(
            headers, first_row)

        # Push field metadata to the client
        self.send_field_metadata(field_metadata)
        # Send the selected prices to the WebSocket
        await self.send(text_data=json.dumps({
            'prices': selected_prices
        }))

    async def disconnect(self, close_code):
        # Remove the consumer from the 'prices_group' group
        await self.channel_layer.group_discard(
            'models_group',  # Group name
            self.channel_name  # Channel name
        )

    async def discover_model_and_fields(self, headers, first_row):
        """
        Analyze the headers and first row of data to discover the appropriate model
        and generate field metadata.

        This is a placeholder method and should be replaced with the actual implementation.
        """
        # Placeholder implementation
        model_class = 'SomeModel'
        field_metadata = [
            {'name': header, 'type': 'string'} for header in headers
        ]
        return model_class, field_metadata

    async def send_field_metadata(self, field_metadata):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'send_metadata',
                'metadata': field_metadata,
            }
        )

    async def send_metadata(self, event):
        if event and 'metadata' in event:
            metadata = event['metadata']
            await self.send(text_data=json.dumps({
                'metadata': metadata
            }))
