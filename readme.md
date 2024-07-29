## Introduction
Overall, our job is to design and implement a system that enables multiple clients to connect to a chatbot server, which automatically responds based on the input they provide. With the constraints provided by the requirements—namely, a maximum of 50 concurrent connections and 500 messages that users can process—we can simply use a monolithic architecture on a single machine to serve clients smoothly.
However, if the requirements change in the future, we will need to rebuild and change the architecture, which costs time and money. Therefore, I want to approach the project with a microservice architecture from the beginning, as it can scale with changing requirements.
## Component diagram
The system consists of several common components, which I will explain individually
### Client
A WebSocket client can establish a connection to the chatbot server. It can send text, audio, and video, and it can receive responses in text, audio, and video as well
### Load balancer
Since we may serve a large number of clients, a load balancer will be used to route and balance traffic across multiple server nodes
The choice of load balancer will depend on the company’s existing infrastructure. For instance, if the company uses AWS, the AWS Elastic Load Balancer (ELB) would be an appropriate choice. This service provides both Application Load Balancers (ALB) and Network Load Balancers (NLB) to meet different needs
### Chat service
This core service accepts WebSocket connections from clients and generates appropriate responses based on the input received
Main logic of this service:
- Receive the connection and extract parameters to identify the client ID and time zone of the client
- Check the time zone and deny request if doesn't match condition.
- Connect to the distributed semaphore to acquire a lock. If no connection is available, the process will need to wait until one becomes available (Maybe It have to have a timeout mechanism. This would ensure that the process does not wait indefinitely if the lock cannot be acquired within a reasonable period)
- Response to client base on input received
- Call chat history to save messages
### Distributed semaphore
The requirement is to ensure that the server does not handle more than a specific number of connections or messages at a time. Therefore, this component is responsible for rate limiting or connection throttling
This service will use a hash map data structure, where the key is the clientId and the value represents the number of connections that the client is currently using
example:
```json
{
	"clientId1": 1,
	"clientId2": 1
}
```
When a client acquires a new connection, the value associated with that clientId will be increased by 1. Conversely, when the client releases a connection, the value will be decreased by 1.
Any database that supports locking can be used. Redis is my choice because it is fast and has a built-in hash map data structure
### Chat history service
It provide an API layer for persisting and listing message. 
It connect to a database to save text message, and connect to a file storage like S3 to store audio, video files
```plantuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml
' uncomment the following line and comment the first to use locally
' !include C4_Container.puml

LAYOUT_TOP_DOWN()
LAYOUT_AS_SKETCH()
' LAYOUT_WITH_LEGEND()

title Component diagram for Chatbot system

System(client, Client, "A client want to connect and chat with the chatbot system")

System_Boundary(c1, "Chatbot server") {
    Container(load_balancer_1, "Load Balancer", "A load balancer to balance trafic throw servers")
    Container(load_balancer_2, "Load Balancer", "A load balancer to balance trafic throw servers")
    Container(chat_real_time_server, "Chat services", "Websocket servers accept request from user", "Handle receive and response logic to serve clients")
    Container(semaphore, "Distributed semaphore", "Concurrency Control", "Limit the maxium connections \n Limit the maxium messages\n Limit connections per client")
    Container(chat_retrieve_api, "Chat history services", "CRUD api for chat history", "Provides interface for saving, listing chat sessions, chat messages to clients")
    ContainerDb(database, "Database", "SQL Database", "Stores chat history, chat session of client with bot.")
    ContainerDb(file_database, "File Storage", "S3/gcs/...", "Stores audio, video file of the chat.")
}


client <-d--> load_balancer_1 : "Send and Recevie msg [wss]"
client -d--> load_balancer_2 : "Get msg history [https]"

load_balancer_1 <-d-> chat_real_time_server
load_balancer_2 -d-> chat_retrieve_api

chat_real_time_server -r-> chat_retrieve_api: save msgs

semaphore <-r-> chat_real_time_server : "Grant connection if available"

chat_retrieve_api -d-> database
chat_retrieve_api -d-> file_database

```

## Sequence diagram
### Open a connection and messaging flow
```plantuml

title Messaging Sequence Diagram

skinparam shadowing false
skinparam actor {
	BorderColor black
	BackgroundColor white
}
skinparam participant {
	BorderColor black
	BackgroundColor #94de5e
}
skinparam sequence {
    LifeLineBorderColor black
}
skinparam ArrowColor black
skinparam noteBorderColor black
skinparam sequenceMessageAlign center

participant client
participant "Load Balancer" as lb
participant "Chat Server" as chatServer
participant "Distributed Semaphore" as ds
participant "Chat history" as ch

client -> lb: WSS /connect?clientId=xxx&timeZone=xxx
lb -> chatServer: route trafic
chatServer -> chatServer: check timeZone if it match condition

alt Fail: timezone doesn't match
    chatServer -> client: disconnect 400 bad request
end

chatServer -> ds: aquireConnection for {clientId}
ds -> chatServer: connectionGranted for {clientId}
chatServer <-[dotted]-> client: connection established
client -> chatServer: send msg
activate chatServer
chatServer -> chatServer: Check msg type and\ngenerate response
chatServer -> ch: save message (async)
return response msg
client -> chatServer: disconnect
chatServer -> ds: releaseConnection for {clientId}
```

## Plan to execute implementation
I choose to implement the client, chat service, and distributed semaphore, as these are the most critical components. Setting up the distributed semaphore involves simply installing a Redis database, so I will not delve deeply into this aspect.

Note: The requirements specify that:

- At any time, a maximum of 500 messages are processed by the server.
- All clients must send at least one message to the server.

Due to time constraints, I couldn’t implement everything. However, it is similar to the mechanism I implemented to restrict 50 clients from connecting to the server at the same time. Sorry for that

### Some assumptions:
Sorry, I didn’t actively ask for the requirements, so I made my own assumptions about the unclear aspects
- Client can request 1 message at a time, when user send message, it have to wait for response before sending another
- The files attached with the request and response are fixed. I downloaded sample files of audio, video, and image formats, loaded them, and made them the response for every request.
### 1. Implement Chat service
- Find a web framework for serving Websocket connection
- When accept and disconnect connection. Write a mechanism for acquiring and release connection, by get data from redis and count how many connections is currently active. If numbers == max, wait for releasing and then increase the connection. When release, decrease it
- Because we need to transfer binary data (audio and video files), we have to define a message format for client-server communication. I will explain it afterward
- Implement how server response based on client message type, client timezone
### 2. Implement client
Implement a WebSocket client that can connect to the server’s WebSocket port, send and receive messages using the message format defined by the server (Can say it is a custom protocol we've defined)
Step:
- Using a websocket client to establish connection to a wss://...
- ping the server periodically to make sure the connection is active
- get input from stdin for user choosing request type (0: text, 1: audio, 3: file)
- send encoded request to server and wait for response
- decode response
- save binary file (if present) to file system
- show user the response information
#### Message format
##### Request format
Header:
first 1 byte -> REQUEST_TYPE: (I know we can just use 2 bit, but dealing with bytes is much easier)
- 00000000 -> gui text 
- 00000001 -> gui voice
- 00000010 -> gui video
Body: binary data of text/voice/video
remaining bytes
- text: utf8
- voice: mp3
- video: mp4

Visualization
```
+----------------------------------------------------+
|                      Header                        |
+----------------------------------------------------+
|  REQUEST_TYPE  |        Description                |
|----------------------------------------------------|
|  00000000      |  Text                             |
|  00000001      |  Voice                            |
|  00000010      |  Video                            |
+----------------------------------------------------+
|                      Body                          |
+----------------------------------------------------+
|  Data Type     |        Description                |
|----------------------------------------------------|
|  Text          |  UTF-8 encoded text               |
|  Voice         |  MP3 encoded audio                |
|  Video         |  MP4 encoded video                |
+----------------------------------------------------+
```
Text request:
```
Header (1 byte):
+----------------+
|  00000000      | (GUI Text)
+----------------+

Body:
+----------------+
|  UTF-8 Text    | (binary data of the text)
+----------------+
```

voice request:
```
Header (1 byte):
+----------------+
|  00000001      | (GUI Voice)
+----------------+

Body:
+----------------+
|  MP3 Data      | (binary data of the audio)
+----------------+
```

Video Request
```
Header (1 byte):
+----------------+
|  00000010      | (GUI Video)
+----------------+

Body:
+----------------+
|  MP4 Data      | (binary data of the video)
+----------------+
```

#### Response format
header:
First 1 byte: message type
- 00000000: text only
- 00000001: text and voice
- 00000010: text and voice and jpg
- 00000011: error
Next 4 bytes: size of binary text (n bytes)
Next 4 bytes: size of binary voice (m bytes)
next n bytes -> text
next m bytes -> voice
remain -> image

```
+----------------------------------------------------+
|                      Header                        |
+----------------------------------------------------+
|  Message Type  |        Description                |
|----------------------------------------------------|
|  00000000      |  Text Only                        |
|  00000001      |  Text and Voice                   |
|  00000010      |  Text, Voice, and JPG             |
|  00000011      |  Error                            |
+----------------------------------------------------+
|  Size (4 bytes each)                               |
|----------------------------------------------------|
|  Binary Text Size (n bytes)                        |
|  Binary Voice Size (m bytes)                       |
+----------------------------------------------------+
|                      Body                          |
+----------------------------------------------------+
|  Data Type     |        Description                |
|----------------------------------------------------|
|  Text          |  n bytes (UTF-8)                  |
|  Voice         |  m bytes (MP3)                    |
|  Image         |  Remaining bytes (JPG)            |
+----------------------------------------------------+
```