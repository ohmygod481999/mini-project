from datetime import datetime


class ChatBotReplyPolicy:
    @staticmethod
    def accept_text_msg_policy(client_id: str, client_time: datetime) -> bool:
        """
        Accept if the message is sent between 5am and midnight
        """
        return 5 <= client_time.hour < 24

    @staticmethod
    def accept_audio_msg_policy(client_id: str, client_time: datetime) -> bool:
        """
        Accept if the message is sent between 8am and 12pm
        """
        return 8 <= client_time.hour < 12

    @staticmethod
    def accept_video_msg_policy(client_id: str, client_time: datetime) -> bool:
        """
        Accept if the message is sent between 8pm and midnight
        """
        return 20 <= client_time.hour < 24
