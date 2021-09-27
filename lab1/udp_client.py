#!/usr/bin/env python3

from socket import *

serverName = "127.0.0.1"
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)

sentence = input("Input lowercase sentence: ")
clientSocket.sendto(sentence.encode(), (serverName,serverPort))

modifiedSentence, serverAddress = clientSocket.recvfrom(2048)
print(f"From Server {serverAddress}: {modifiedSentence.decode()}")
clientSocket.close()