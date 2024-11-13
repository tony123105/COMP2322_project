# Project Title

	COMP2322 Project - Multi-thread Web Server

## Description

	This is a python program to implement a Web Service using the HTTP protocol

## Main function

	1. Multi-thread Web Server
	2. Proper request and response message exchanges
	3. GET command for both text files and image files
	4. HEAD command
	5. Four types of response statuses (200, 400, 404, 304)
	6. Handle Last-Modified and If-Modified-Since header fields
	7. Handle Connection header field for both HTTP persistent connection (keep-alive) and non-persistent connection (close)
	8. Logging

## Requirement

	Python 3
	build-in library socket, sys, threading, time, os

## Usage

	To start the server, run the following command:

		python server.py

	You can visit it by http://127.0.0.1:8000/

Author

	Lai Ka Chung (22080062d)
