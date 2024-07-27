import os
from typing import Optional
from dataclasses import dataclass
import uuid

from utils import get_sample_audio, get_sample_image, get_sample_text


class ResponseType:
    TEXT = 0
    TEXT_AUDIO = 1
    TEXT_AUDIO_IMAGE = 2


@dataclass
class ResponsePayload:
    message_id: uuid.UUID
    type: int
    text: str
    audio: Optional[bytes]
    image: Optional[bytes]

    def encode(self) -> bytes:
        text_bytes = self.text.encode("utf-8")
        text_bytes_len = len(text_bytes)
        audio_bytes_len = len(self.audio) if self.audio else 0
        image_bytes_len = len(self.image) if self.image else 0

        print(f"--DEBUG-- text_bytes_len: {text_bytes_len}")
        print(f"--DEBUG-- audio_bytes_len: {audio_bytes_len}")
        print(f"--DEBUG-- image_bytes_len: {image_bytes_len}")

        # 1MB
        MAX_FILE_SIZE = 1024 * 1024
        if audio_bytes_len > MAX_FILE_SIZE:
            raise ValueError("Audio file too large")

        if image_bytes_len > MAX_FILE_SIZE:
            raise ValueError("Image file too large")

        header = b"".join(
            [
                self.message_id.bytes,
                self.type.to_bytes(1, byteorder="big"),
                text_bytes_len.to_bytes(4, byteorder="big"),
                audio_bytes_len.to_bytes(4, byteorder="big"),
            ]
        )
        body = b"".join(
            [
                text_bytes,
                self.audio or b"",
                self.image or b"",
            ]
        )
        return header + body

    @staticmethod
    def decode(payload: bytes) -> "ResponsePayload":
        message_id = uuid.UUID(bytes=payload[:16])
        type = int.from_bytes(payload[16:17], byteorder="big")
        text_bytes_len = int.from_bytes(payload[17:21], byteorder="big")
        audio_bytes_len = int.from_bytes(payload[21:25], byteorder="big")

        text = payload[25 : 25 + text_bytes_len].decode("utf-8")
        audio = payload[25 + text_bytes_len : 25 + text_bytes_len + audio_bytes_len]
        image = payload[25 + text_bytes_len + audio_bytes_len :]

        return ResponsePayload(
            message_id=message_id,
            type=type,
            text=text,
            audio=audio if audio else None,
            image=image if image else None,
        )


def get_sample_response_payload(type: int) -> ResponsePayload:
    audio = None if type == ResponseType.TEXT else get_sample_audio()
    image = (
        None
        if type == ResponseType.TEXT_AUDIO or type == ResponseType.TEXT
        else get_sample_image()
    )
    return ResponsePayload(
        message_id=uuid.uuid4(),
        type=type,
        text=get_sample_text(),
        audio=audio,
        image=image,
    )
