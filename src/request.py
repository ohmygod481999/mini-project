import os
from typing import Optional
from dataclasses import dataclass


class RequestType:
    TEXT = 0
    AUDIO = 1
    VIDEO = 2


@dataclass
class RequestPayload:
    type: int
    text: Optional[str]
    audio: Optional[bytes]
    image: Optional[bytes]

    def encode(self) -> bytes:
        return b"".join(
            [
                # str(self.type).encode("utf-8"),
                self.type.to_bytes(1, byteorder="big"),
                self.text.encode("utf-8") if self.text else b"",
                self.audio or b"",
                self.image or b"",
            ]
        )

    @staticmethod
    def decode(payload: bytes) -> "RequestPayload":
        type = int.from_bytes(payload[:1], byteorder="big")
