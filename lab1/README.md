# Lab 1: A Simple Web Proxy Server
---
## Code description
---
The script is written by following the skeleton code provided.

A welcome socket is first created, and this is the server socket for the proxy that will listen for any clients.
```
welcomeSocket = socket(AF_INET, SOCK_STREAM)
welcomeSocket.bind((proxy_ip,proxy_port))
welcomeSocket.listen(1)
```
Note that we are using the TCP protocol.

This welcoming socket will then create a client-facing socket everytime it has established a connection and received a request from your browser.

```clientFacingSocket, addr = welcomeSocket.accept()```

A new thread will be started to handle each client. Since the message received are in bytes, we have to decode it into unicode.

`message = clientFacingSocket.recv(4096).decode()`

After extracting the necessary information from the message, we change the `Connection: keep-alive` to `Connection: close`, so that the connection is not persistent and closes once done.

`message=message.replace("Connection: keep-alive","Connection: close")`

We then check if we have cached the content before.

If we did, we read from the cache file and send the content back to the client.

```
with open(file_to_use, "rb") as f:
    # ProxyServer finds a cache hit and generates a response message
    print("served from the cache")
    while True:
        buff = f.read(4096)
        if buff:
            # Fill in start
            clientFacingSocket.send(buff)
            # Fill in end
        else:
            break
```

If we did not, we have to create a server facing socket (acting as a client), connect to the web server, and forward the message to the web server.

```
serverFacingSocket = socket(AF_INET, SOCK_STREAM)

serverFacingSocket.connect((webServer, port))
serverFacingSocket.send(message.encode())
```

We then read from the web server, write into a local cache file, and send the content back to the client.

```
with open(file_to_use, "wb") as cacheFile:
    print("Writing to cacheFile...")
    while True:
        # Fill in start
        buff = serverFacingSocket.recv(4096)
        # print("Response:\n", buff)
        # Fill in end
        
        if buff:
            # Fill in start
            print("Sending buff...")
            cacheFile.write(buff)
            clientFacingSocket.send(buff)
            print("Sent buff...")
            # Fill in end
        else:
            break
    print("Closing cacheFile...")
```

Finally, we have to remember to close the sockets.
```
serverFacingSocket.close()
clientFacingSocket.close()
```

## How to run code

1. Before running the code, first go to your proxy settings and set up the web proxy.

    For my case, I am using **localhost** and **port 8079**.

2. Next, run the proxy file in terminal.
    
    `python3 proxy.py`

3. Lastly, go to your web browser, eg. Chrome, and try out the following web pages.
 - http://httpforever.com/
 - http://www.neverssl.com/
 - http://www.httpvshttps.com/
 - http://www.webscantest.com/ 