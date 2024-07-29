from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import uuid
from enum import Enum


class ChatHistoryMessageType(Enum):
    USER = 0
    BOT = 1


@dataclass
class ChatHistoryMessage:
    id: uuid.UUID
    client_id: str
    text: str
    audio_url: str
    image_url: str
    video_url: str
    type: ChatHistoryMessageType
    time: str


class IChatHistory(ABC):
    @abstractmethod
    @abstractmethod
    def add_chat_message(self, client_id: str, message: ChatHistoryMessage) -> None:
        pass

    @abstractmethod
    def get_all_chat_history(self, client_id: str) -> List[ChatHistoryMessage]:
        pass


class ChatHistory(IChatHistory):
    """
    Dummy chat history service store data on RAM
    further implementation can store data in remote file storate like S3
    """

    def __init__(self):
        self.chat_history = {}

    def add_chat_message(self, client_id: str, message: ChatHistoryMessage) -> None:
        if client_id not in self.chat_history:
            self.chat_history[client_id] = []
        self.chat_history[client_id].append(message)

    def get_all_chat_history(self, client_id: str) -> List[ChatHistoryMessage]:
        return self.chat_history.get(client_id, [])
