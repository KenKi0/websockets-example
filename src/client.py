import asyncio
import typing

import aioconsole
import websockets
import websockets.legacy.protocol as ws_protocol

import models


class ClientApp:
    def __init__(self, name: str) -> None:
        self.name = name
        self.websocket: typing.Optional[ws_protocol.WebSocketCommonProtocol] = None

    async def run_forever(self) -> None:
        uri = "ws://localhost:8765"
        async with websockets.connect(uri) as websocket:
            self.websocket = websocket
            login = models.LoginMessage(sender=self.name)
            await self.websocket.send(login.json())
            tasks = [
                asyncio.create_task(self._receive_forever()),
                asyncio.create_task(self._send_forever()),
            ]
            await asyncio.gather(*tasks)

    async def _receive_forever(self) -> None:
        if self.websocket is None:
            return
        while True:
            data = await self.websocket.recv()
            message = models.Message.parse_raw(data)
            print(f"<<<{message.sender}: {message.text}")

    async def _send_forever(self) -> None:
        if self.websocket is None:
            return
        while True:
            text = await aioconsole.ainput("")
            message = models.Message(sender=self.name, text=text)
            await self.websocket.send(message.json())


async def main() -> None:
    name = input("Введите имя:")
    app = ClientApp(name)
    await app.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
