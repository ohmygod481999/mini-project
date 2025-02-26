import asyncio
from datetime import datetime
import os
import sys
import pytz
import websockets
from chatserver.config import Config
from file_storage import FileStorage, LocalFileStorage
from request import get_sample_request_payload
from request import RequestType
from response import ResponsePayload, ResponseType
import aioconsole

client_file_storage: FileStorage = LocalFileStorage(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../client_file_storage")
    )
)


def print_response(resp_payload: ResponsePayload) -> None:
    if resp_payload.type == ResponseType.TEXT:
        print(f"Receive msg: {resp_payload.message_id}")
        print(f"message type: {resp_payload.type}")
        print(f"text: {resp_payload.text}")

    elif resp_payload.type == ResponseType.TEXT_AUDIO:
        print(f"Receive msg: {resp_payload.message_id}")
        print(f"message type: {resp_payload.type}")
        print(f"text: {resp_payload.text}")
        audio_file_path = client_file_storage.save_file(
            f"{str(resp_payload.message_id)}.mp3", resp_payload.audio
        )
        print(f"Audio: {audio_file_path}")

    elif resp_payload.type == ResponseType.TEXT_AUDIO_IMAGE:
        print(f"Receive msg: {resp_payload.message_id}")
        print(f"message type: {resp_payload.type}")
        print(f"text: {resp_payload.text}")
        image_file_path = client_file_storage.save_file(
            f"{str(resp_payload.message_id)}.jpg", resp_payload.image
        )
        audio_file_path = client_file_storage.save_file(
            f"{str(resp_payload.message_id)}.mp3", resp_payload.audio
        )
        print(f"Image: {image_file_path}")
        print(f"Audio: {audio_file_path}")

    elif resp_payload.type == ResponseType.ERROR:
        print(f"Receive msg: {resp_payload.message_id}")
        print(f"message type: {resp_payload.type} (error)")
        print(f"error message: {resp_payload.error_message}")


async def chat_handler(websocket: websockets.WebSocketClientProtocol):
    while True:
        print()
        input_type = int(
            await aioconsole.ainput("Enter the type of input (accept 0, 1, 2)\n")
        )
        if input_type == RequestType.TEXT:
            req_payload = get_sample_request_payload(RequestType.TEXT)
        elif input_type == RequestType.AUDIO:
            req_payload = get_sample_request_payload(RequestType.AUDIO)
        elif input_type == RequestType.VIDEO:
            req_payload = get_sample_request_payload(RequestType.VIDEO)
        else:
            print("Invalid input")
            continue
        try:
            request_encoded = req_payload.encode()
            await websocket.send(request_encoded)
            message = await websocket.recv()
            resp_payload = ResponsePayload.decode(bytes(message))

            print_response(resp_payload)
        except Exception as e:
            print(e)


async def keep_alive(websocket: websockets.WebSocketClientProtocol):
    while True:
        await websocket.ping()
        await asyncio.sleep(1)


async def main():
    # get client_id from args

    client_id = sys.argv[1] if len(sys.argv) > 1 else None
    time_zone = sys.argv[2] if len(sys.argv) > 2 else None
    if not client_id:
        print("Client id is required")
        return
    if not time_zone:
        print("Time zone is required")
        return
    tz = pytz.timezone(time_zone)
    client_time = datetime.now(tz)
    print(f"Client time zone: {time_zone}, current time: {client_time}")

    SERVER_HOST = Config.SERVER_HOST
    SERVER_PORT = Config.SERVER_PORT
    path = "ws://{server_host}:{server_port}?client_id={client_id}&time_zone={time_zone}".format(
        server_host=SERVER_HOST,
        server_port=SERVER_PORT,
        client_id=client_id,
        time_zone=time_zone,
    )
    print(path)
    try:
        async with websockets.connect(path) as websocket:
            first_msg = await websocket.recv()
            if first_msg != "connected":
                print(f"Connection failed")
                return
            print(f"Connected to {path}")
            keep_alive_task = asyncio.create_task(keep_alive(websocket))
            chat_handler_task = asyncio.create_task(chat_handler(websocket))

            done, pending = await asyncio.wait(
                [keep_alive_task, chat_handler_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            for task in done:
                if task.exception():
                    print(f"Task completed with exception: {task.exception()}")
    except (
        websockets.ConnectionClosedError,
        websockets.InvalidURI,
        websockets.InvalidHandshake,
    ) as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
