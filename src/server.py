import asyncio
import typing

import websockets
import websockets.exceptions as ws_exceptions
import websockets.legacy.protocol as ws_protocol

import models


class User:
    def __init__(self, name: str, websocket: ws_protocol.WebSocketCommonProtocol) -> None:
        self.name = name
        self.websocket = websocket

    @classmethod
    async def from_websocket(cls, websocket: ws_protocol.WebSocketCommonProtocol) -> "User":
        data = await websocket.recv()
        login = models.LoginMessage.parse_raw(data)
        return cls(name=login.sender, websocket=websocket)

    async def receive_forever(self) -> typing.AsyncIterator[models.Message]:
        while True:
            try:
                yield await self._receive()
            except ws_exceptions.ConnectionClosed:
                return

    async def _receive(self) -> models.Message:
        data = await self.websocket.recv()
        message = typing.cast(models.Message, models.Message.parse_raw(data))
        return message

    async def send(self, message: models.Message) -> None:
        if self.name == message.sender:
            return
        await self.websocket.send(message.json())


class App:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.messages: asyncio.queues.Queue[models.Message] = asyncio.queues.Queue()

    async def start(self) -> None:
        async with websockets.serve(self._handle_websocket, "localhost", 8765):
            await self._send_forever()

    async def _handle_websocket(self, websocket: ws_protocol.WebSocketCommonProtocol) -> None:
        user = await User.from_websocket(websocket)
        if user.name in self.users:
            print("Already logged in: {login.sender}")
            return

        self.users[user.name] = user
        print(f"Logged in: {user.name}")
        async for message in user.receive_forever():
            await self.messages.put(message)

        print(f"Logged out: {user.name}")
        del self.users[user.name]

    async def _send_forever(self) -> None:
        while True:
            message = await self.messages.get()
            tasks = [asyncio.create_task(user.send(message)) for user in self.users.values()]
            await asyncio.gather(*tasks)


async def main() -> None:
    app = App()
    await app.start()


if __name__ == "__main__":
    asyncio.run(main())
