from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import uuid
from enum import Enum


class ChatMessageType(Enum):
    USER = 0
    BOT = 1


@dataclass
class ChatMessage:
    id: uuid.UUID
    message: str
    type: ChatMessageType
    time: str


class IChatHistory(ABC):
    @abstractmethod
    @abstractmethod
    def add_chat_message(self, client_id: str, message: ChatMessage) -> None:
        pass

    @abstractmethod
    def get_all_chat_history(self, client_id: str) -> List[ChatMessage]:
        pass


class ChatHistory(IChatHistory):
    def __init__(self):
        self.chat_history = {}

    def add_chat_message(self, client_id: str, message: ChatMessage) -> None:
        if client_id not in self.chat_history:
            self.chat_history[client_id] = []
        self.chat_history[client_id].append(message)

    def get_all_chat_history(self, client_id: str) -> List[ChatMessage]:
        return self.chat_history.get(client_id, [])
