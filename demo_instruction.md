## Demo instruction
### Application requirements
- Docker
- docker compose

### build docker image
```bash
docker compose build
```

(Sorry, the build time is a bit slow because I didn’t remove unused packages in requirements.txt :<)

### Test server functionality
I am mostly focusing on testing encoding, decoding messages, and concurrent requests logic

```bash
docker compose up pytest
```
### Run server

Open a terminal session
```bash
docker compose up -d chat_server
docker compose exec chat_server bash
python src/chatserver/chat_server.py
```

### Run clients
Open another terminal session (step 1)
```bash
docker compose run client bash
```

Run a client with {clientId} and {timeZone} of your choice

timeZone you can get a random value I provide in timezones.txt file

The clientId is an arbitrary string without spaces
```bash
python src/client/client.py {clientId} {timeZone}
```
Example:
```bash
python src/client/client.py 123 America/New_York
```

The CLI will ask for type of input you want to send
> Enter the type of input (accept 0, 1, 2)

0: send a text (I fix "Hello world!" here)

1: send a audio (I fix sample.mp3 in sample folder)

2: send a video (I fix sample.mp4 in sample folder)

Press 0, 1, or 2 and then enter. The server will respond according to your request

You can open another client by opening a different terminal session and run from (step 1)
Note that with current configuration that
- MAX_CONNECTIONS=5
- MAX_CONNECTION_PER_CLIENT=1

You can only connect to the server with 1 clientId, or 5 clients with different id

You will receive this response if you connect for more than the maximum allowed connections

> Connection failed: received 1008 (policy violation) Too many connections; then sent 1008 (policy violation) Too many connections

Change MAX_CONNECTIONS and MAX_CONNECTIONS environment variables in docker-compose.yml file to try another maximum connections

(Sorry if I haven't make a script to generate large a mount of clients to test)