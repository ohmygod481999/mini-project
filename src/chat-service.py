import asyncio
from websockets import WebSocketServerProtocol
from websockets.server import serve

from response import ResponseType, get_sample_response_payload


async def echo(websocket: WebSocketServerProtocol):
    async for message in websocket:
        sample_resp_payload = get_sample_response_payload(ResponseType.TEXT_AUDIO_IMAGE)
        await websocket.send(sample_resp_payload.encode())


async def main():
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever


asyncio.run(main())
