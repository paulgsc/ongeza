"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""


import os
import json
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from services.routing import websocket_urlpatterns
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from rest_framework.request import Request

User = get_user_model()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'services.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

jwt_authentication = JWTAuthentication()


class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        token = None
        headers = dict(scope["headers"])
        token = headers.get(b"authorization", b"").decode(
            "utf-8").replace("Bearer ", "")
        print('token: ', token)
        # Check if it's a WebSocket connection
        if scope['type'] == 'websocket.connect':
            # The connection is being established; proceed with the handshake
            await send({
                'type': 'websocket.accept',
            })

            # Get the authentication message from the WebSocket
            auth_message = await receive()

            if auth_message:
                # Parse the JSON message
                print('message: ', auth_message, 'type: ', type(auth_message))
                auth_data = json.loads(auth_message.get('text', '{}'))
                print('auth_data: ', auth_data)

                # Extract the token from the message
                token = auth_data.get('token')


        if token:
            try:

                validated_token = await self.get_validated_token(token)
                user = await self.get_user(validated_token)

                scope['user'] = user
            except Exception as e:
                raise Exception(str(e))
        # Print the scope and user information

        # Continue with the rest of the middleware
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_validated_token(self, token):
        return jwt_authentication.get_validated_token(token)

    @database_sync_to_async
    def get_user(self, validated_token):
        # Assuming the user ID is stored in the 'user_id' claim
        user_id = validated_token.get('user_id')
        return User.objects.get(id=user_id)


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            )
        ))

})