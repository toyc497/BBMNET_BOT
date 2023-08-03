import websockets


class Websockets_Connection:

    async def listen(self, messageBot):
        url = 'ws://127.0.0.1:8085/connectiongate'
        async with websockets.connect(url) as ws:
            await ws.send(messageBot)