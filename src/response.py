import os
from typing import Optional
from dataclasses import dataclass


class ResponseType:
    TEXT = 0
    TEXT_AUDIO = 1
    TEXT_AUDIO_IMAGE = 2


@dataclass
class ResponsePayload:
    type: int
    text: bytes
    audio: Optional[bytes]
    image: Optional[bytes]

    def encode(self) -> bytes:
        text_bytes_len = len(self.text)
        audio_bytes_len = len(self.audio) if self.audio else 0
        image_bytes_len = len(self.image) if self.image else 0

        if audio_bytes_len > 4 or image_bytes_len > 4 or text_bytes_len > 4:
            raise ValueError("data is too large")

        header = b"".join(
            [
                self.type.to_bytes(1, byteorder="big"),
                text_bytes_len.to_bytes(4, byteorder="big"),
                audio_bytes_len.to_bytes(4, byteorder="big"),
            ]
        )
        body = b"".join(
            [
                self.text,
                self.audio or b"",
                self.image or b"",
            ]
        )
        return header + body

    @staticmethod
    def decode(payload: bytes) -> "ResponsePayload":
        type = int.from_bytes(payload[:1], byteorder="big")
        text_len = int.from_bytes(payload[1:5], byteorder="big")
        audio_len = int.from_bytes(payload[5:9], byteorder="big")
        text = payload[9 : 9 + text_len]
        audio = payload[9 + text_len : 9 + text_len + audio_len]
        image = payload[9 + text_len + audio_len :]
        return ResponsePayload(type=type, text=text, audio=audio, image=image)


def get_sample_image() -> bytes:
    sample_image_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../sample", "sample.jpg")
    )
    with open(sample_image_path, "rb") as f:
        return f.read()


def get_sample_audio() -> bytes:
    sample_audio_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../sample", "sample.mp3")
    )
    with open(sample_audio_path, "rb") as f:
        return f.read()


def get_sample_text() -> bytes:
    return "Hello, World!".encode("utf-8")


def get_sample_response_payload(type: int) -> ResponsePayload:
    audio = None if type == ResponseType.TEXT else get_sample_audio()
    image = (
        None
        if type == ResponseType.TEXT_AUDIO or type == ResponseType.TEXT
        else get_sample_image()
    )
    return ResponsePayload(
        type=type,
        text=get_sample_text(),
        audio=audio,
        image=image,
    )
