#!/usr/bin/env python3

from socket import *

serverName = "127.0.0.1"
serverPort = 12000

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((serverName,serverPort))

print(f"The Server is ready to receive...")

while True:
    sentence, clientAddress = serverSocket.recvfrom(2048)
    capitalizedSentence = sentence.decode().upper()
    serverSocket.sendto(capitalizedSentence.encode(),clientAddress)