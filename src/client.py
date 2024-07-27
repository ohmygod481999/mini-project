from websockets.sync.client import connect
import pytz
from tzlocal import get_localzone
from request import RequestPayload
from request import RequestType

if __name__ == "__main__":
    client_id = "123"
    path = "ws://localhost:8765/connect/clientId={client_id}&timeZone={time_zone}".format(client_id=client_id, time_zone=get_localzone())
    print(path)
    #with connect(path) as websocket:
    while True :
        input_type = int(input())
        if input_type == 1:
            text_msg = str(input())
            payload = RequestPayload(type=RequestType.TEXT, text=text_msg, audio=None, video=None)
        elif input_type == 2:
            audio_path = str(input())
            with open(audio_path, mode='rb') as file:
                content = file.read()
                print(content)

        elif input_type == 3:
            pass


