from typing import Optional
from dataclasses import dataclass
import uuid

from utils import get_sample_audio, get_sample_text, get_sample_video


class RequestType:
    TEXT = 0
    AUDIO = 1
    VIDEO = 2


@dataclass
class RequestPayload:
    message_id: uuid.UUID
    type: int
    text: Optional[str]
    audio: Optional[bytes]
    video: Optional[bytes]

    def encode(self) -> bytes:
        return b"".join(
            [
                self.message_id.bytes,
                self.type.to_bytes(1, byteorder="big"),
                self.text.encode("utf-8") if self.text else b"",
                self.audio or b"",
                self.video or b"",
            ]
        )

    @staticmethod
    def decode(payload: bytes) -> "RequestPayload":
        message_id = uuid.UUID(bytes=payload[:16])
        type = int.from_bytes(payload[16:17], byteorder="big")

        if type == RequestType.TEXT:
            text = payload[17:].decode("utf-8")
            return RequestPayload(
                message_id=message_id, type=type, text=text, audio=None, video=None
            )
        elif type == RequestType.AUDIO:
            return RequestPayload(
                message_id=message_id,
                type=type,
                text=None,
                audio=payload[17:],
                video=None,
            )
        elif type == RequestType.VIDEO:
            return RequestPayload(
                message_id=message_id,
                type=type,
                text=None,
                audio=None,
                video=payload[17:],
            )
        else:
            raise ValueError("Invalid request type")


def get_sample_request_payload(type: int) -> RequestPayload:
    text = None if type != RequestType.TEXT else get_sample_text()
    audio = None if type != RequestType.AUDIO else get_sample_audio()
    video = None if type != RequestType.VIDEO else get_sample_video()

    return RequestPayload(
        message_id=uuid.uuid4(), type=type, text=text, audio=audio, video=video
    )
