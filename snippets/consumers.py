# snippets/consumers.py
import json
from .models import ChatMessage
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.me = self.scope["user"]
        # Obtenemos el nombre del otro usuario de la URL
        self.other_username = self.scope["url_route"]["kwargs"]["username"]

        if not self.me.is_authenticated:
            await self.close()
            return

        # Creamos un nombre de sala único para la pareja (ordenado alfabéticamente)
        usernames = sorted([self.me.username, self.other_username])
        self.room_group_name = f"chat_{usernames[0]}_{usernames[1]}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        try:
            old_messages = await self.get_old_messages()
            for msg in old_messages:
                await self.send(
                    text_data=json.dumps(
                        {"message": f"{msg['sender__username']}: {msg['message']}"}
                    )
                )
        except Exception as e:
            print(f"Error carregant missatges: {e}")

    async def receive(self, text_data):
        if self.me.is_authenticated:
            # Guardamos el mensaje con el destinatario real
            await self.save_message(self.me, self.other_username, text_data)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": text_data,
                    "sender": self.me.username,
                },
            )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps({"message": f"{event['sender']}: {event['message']}"})
        )

    @database_sync_to_async
    def save_message(self, sender, recipient_username, msg):
        recipient = User.objects.get(username=recipient_username)
        return ChatMessage.objects.create(
            sender=sender, recipient=recipient, message=msg
        )

    @database_sync_to_async
    def get_old_messages(self):
        from django.db.models import Q

        # Fem un print per depurar a la consola si està arribant aquí
        print(f"Buscant missatges entre {self.me.username} i {self.other_username}")

        qs = ChatMessage.objects.filter(
            (Q(sender=self.me) & Q(recipient__username=self.other_username))
            | (Q(sender__username=self.other_username) & Q(recipient=self.me))
        ).order_by("-timestamp")[:50]

        # Important: Convertir el QuerySet a llista dins del thread síncron
        return list(qs.values("sender__username", "message"))[::-1]
