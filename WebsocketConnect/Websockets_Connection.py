import websockets


class Websockets_Connection:

    async def listen(self, messageBot):
        url = 'ws://127.0.0.1:8085/connectiongate'
        headersWebsocket = {'Authorization': messageBot[0]}
        async with websockets.connect(url, extra_headers=headersWebsocket) as ws:
            await ws.send(messageBot[1])