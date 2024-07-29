import asyncio
from datetime import datetime
import random
from urllib.parse import parse_qs, urlparse
import pytz
from websockets import WebSocketServerProtocol
import websockets
from chat_history.chat_history import (
    ChatHistory,
    ChatHistoryMessage,
    ChatHistoryMessageType,
)
from websockets.frames import CloseCode

from chatserver.chatbot_reply_policy import ChatBotReplyPolicy
from chatserver.concurrency_control import ConcurrencyControl
from chatserver.config import Config
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
            max_connections=Config.MAX_CONNECTIONS,
            max_connection_per_client=Config.MAX_CONNECTION_PER_CLIENT,
            redis_key=Config.CONCURRENT_CONTROL_REDIS_KEY
        )

    async def handle_response_for_text(
        self, client_id: str, client_time: datetime, req_payload: RequestPayload
    ) -> ResponsePayload:
        await asyncio.sleep(random.uniform(0, 1))
        if req_payload.type != RequestType.TEXT:
            raise ValueError("Invalid request type")

        if not ChatBotReplyPolicy.accept_text_msg_policy(client_id, client_time):
            raise MessagePolicyException("We can not accept text message now")

        return get_sample_response_payload(ResponseType.TEXT)

    async def handle_response_for_audio(
        self, client_id: str, client_time: datetime, req_payload: RequestPayload
    ) -> ResponsePayload:
        await asyncio.sleep(random.uniform(1, 2))

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

    async def generate_response(
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

        return await handler(client_id, client_time, req_payload)

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

        async def handle_msgs():
            """
            Handle incoming messages from the client
            """
            async for message in websocket:
                try:
                    # Handle heartbeat message
                    if message == "ping":
                        await websocket.send("pong")
                        continue

                    # incoming message is a bytes object contain all the text (utf-8), audio(mp3) and video(mp4) data
                    req_payload = RequestPayload.decode(bytes(message))

                    print(
                        f"[Client {client_id}] new incoming message: {req_payload.message_id}, message type {req_payload.type}"
                    )
                    # Save request message to chat history
                    self.chat_history.add_chat_message(
                        client_id,
                        ChatHistoryMessage(
                            id=req_payload.message_id,
                            client_id=client_id,
                            type=ChatHistoryMessageType.USER,
                            text=req_payload.text,
                            audio_url=None,  # TODO: save audio file and return the url
                            image_url=None,  # TODO: save image file and return the url
                            video_url=None,  # TODO: save video file and return the url
                            time=client_time.strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                    )

                    resp_payload = await self.generate_response(
                        client_id, client_time, req_payload
                    )

                    # Save response message to chat history
                    self.chat_history.add_chat_message(
                        client_id,
                        ChatHistoryMessage(
                            id=resp_payload.message_id,
                            client_id=client_id,
                            type=ChatHistoryMessageType.BOT,
                            text=req_payload.text,
                            audio_url=None,  # TODO: save audio file and return the url
                            image_url=None,  # TODO: save image file and return the url
                            video_url=None,  # TODO: save video file and return the url
                            time=client_time.strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                    )

                    await websocket.send(resp_payload.encode())
                except websockets.exceptions.ConnectionClosedError:
                    print(f"[Client {client_id}] disconnected")
                    break
                except MessagePolicyException as e:
                    print(f"[Client {client_id}]: Message Policy Exception: {e}")
                    await websocket.send(get_error_payload(e.message).encode())
                except Exception as e:
                    print(f"[Client {client_id}]Error: {e}")
                    # TODO: return server error information to client is just for debugging
                    # we should return a user-friendly message
                    await websocket.send(get_error_payload(str(e)).encode())

        async def handle_disconnect():
            await websocket.wait_closed()

        await asyncio.gather(handle_msgs(), handle_disconnect())
        await self.concurrent_control.release_connection(client_id)
