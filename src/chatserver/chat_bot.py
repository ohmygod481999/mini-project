import asyncio
from datetime import datetime
from urllib.parse import parse_qs, urlparse
import pytz
from websockets import WebSocketServerProtocol
import websockets
from chat_history.chat_history import ChatHistory
from websockets.frames import CloseCode

from chatserver.chatbot_reply_policy import ChatBotReplyPolicy
from chatserver.concurrency_control import ConcurrencyControl
from chatserver.exceptions import MessagePolicyException
from request import RequestPayload, RequestType
from response import (
    ResponsePayload,
    ResponseType,
    get_error_payload,
    get_sample_response_payload,
)


class ChatBot:
    """
    ChatBot class to handle the chat server

    handle_ws_connection: function to handle the websocket connection
    """

    def __init__(self):
        self.chat_history = ChatHistory()
        self.concurrent_control = ConcurrencyControl(
            max_connections=4,
            max_connection_per_client=1,
            redis_key="concurrency_control",
        )

    def handle_response_for_text(
        self, client_id: str, client_time: datetime, req_payload: RequestPayload
    ) -> ResponsePayload:
        if req_payload.type != RequestType.TEXT:
            raise ValueError("Invalid request type")

        if not ChatBotReplyPolicy.accept_text_msg_policy(client_id, client_time):
            raise MessagePolicyException("We can not accept text message now")

        return get_sample_response_payload(ResponseType.TEXT)

    def handle_response_for_audio(
        self, client_id: str, client_time: datetime, req_payload: RequestPayload
    ) -> ResponsePayload:
        if req_payload.type != RequestType.AUDIO:
            raise ValueError("Invalid request type")

        if not ChatBotReplyPolicy.accept_audio_msg_policy(client_id, client_time):
            raise MessagePolicyException("We can not accept audio message now")
        return get_sample_response_payload(ResponseType.TEXT_AUDIO)

    def handle_response_for_video(
        self, client_id: str, client_time: datetime, req_payload: RequestPayload
    ) -> ResponsePayload:
        if req_payload.type != RequestType.VIDEO:
            raise ValueError("Invalid request type")

        if not ChatBotReplyPolicy.accept_video_msg_policy(client_id, client_time):
            raise MessagePolicyException("We can not accept video message now")
        return get_sample_response_payload(ResponseType.TEXT_AUDIO)

    def generate_response(
        self, client_id: str, client_time: datetime, req_payload: RequestPayload
    ) -> ResponsePayload:
        response_handler = {
            RequestType.TEXT: self.handle_response_for_text,
            RequestType.AUDIO: self.handle_response_for_audio,
            RequestType.VIDEO: self.handle_response_for_video,
        }

        handler = response_handler.get(req_payload.type)
        if not handler:
            raise ValueError("Invalid request type")

        return handler(client_id, client_time, req_payload)

    async def handle_ws_connection(self, websocket: WebSocketServerProtocol, path: str):
        query_params = parse_qs(urlparse(path).query)
        client_ids = query_params.get("client_id")
        time_zones = query_params.get("time_zone")
        if not client_ids or not time_zones:
            print("Invalid query parameters")
            await websocket.close(CloseCode.INVALID_DATA, "Invalid query parameters")
            return

        client_id = client_ids[0]
        time_zone = time_zones[0]
        ok = await self.concurrent_control.acquire_connection(client_id)
        if not ok:
            print(f"Can not serve {client_id} because of too many connections")
            await websocket.close(CloseCode.POLICY_VIOLATION, "Too many connections")
            return

        await websocket.send("connected")
        print(f"Connection to {client_id} has established time zone: {time_zone}")

        timezone = pytz.timezone(time_zone)
        client_time = datetime.now(timezone)

        if client_time.hour < 9 or client_time.hour > 17:
            print("Out of working hours")
            await websocket.close(CloseCode.TRY_AGAIN_LATER, "Out of working hours")
            return

        async def handle_msgs():
            """
            Handle incoming messages from the client
            """
            try:
                async for message in websocket:
                    # Handle ping
                    if message == "ping":
                        await websocket.send("pong")
                        continue

                    # incoming message is a bytes object contain all the text (utf-8), audio(mp3) and video(mp4) data
                    req_payload = RequestPayload.decode(bytes(message))
                    print(
                        f"[Client {client_id}] new incoming message: {req_payload.message_id}, message type {req_payload.type}"
                    )
                    resp_payload = self.generate_response(
                        client_id, client_time, req_payload
                    )
                    await websocket.send(resp_payload.encode())
            except websockets.exceptions.ConnectionClosedError:
                print(f"[Client {client_id}] disconnected")
            except MessagePolicyException as e:
                await websocket.send(get_error_payload(e.message).encode())
            except Exception as e:
                print(f"Error: {e}")
                await websocket.close(
                    CloseCode.UNEXPECTED_CONDITION, "Unexpected error"
                )

        async def handle_disconnect():
            await websocket.wait_closed()

        await asyncio.gather(handle_msgs(), handle_disconnect())
        await self.concurrent_control.release_connection(client_id)
