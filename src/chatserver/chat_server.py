import asyncio
from websockets.server import serve

from chatserver.chat_bot import ChatBot
from chatserver.config import Config


async def main():
    chatbot = ChatBot()
    await chatbot.concurrent_control.clean_all_sessions()

    PORT = Config.SERVER_PORT
    MAX_SIZE = 100000000
    HOST = "0.0.0.0"
    print(f"Starting server on {HOST}:{PORT}")
    async with serve(chatbot.handle_ws_connection, HOST, PORT, max_size=MAX_SIZE):
        print(f"Server started, listening on {HOST}:{PORT}")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
