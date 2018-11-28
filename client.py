# Name: Joshua Westbrook
# Date: 11/21/2018
# Student ID: 14262905
# CS4850 Lab 3 Chatroom
# Client Application

import socket 
import select 
import sys 
import time
import os

# define the IP Address and Port of the server
IPAddress = "192.168.1.10"
port = 12905

print("Chatroom Client (CS4850 - Lab 3)\n")

while True:
	# create the socket to connect to the server
	server = socket.socket()  
	
	# receive input for a command, strip the newline character, and split into 3 parts
	# the 3 parts are: <command> <option> <option>. the second option will be the remainder of the input
	print("Please enter a command.")
	command = sys.stdin.readline()
	command = command.strip('\n')
	command = command.split(' ', 2)

	# if the command is 'login' or 'newuser'
	if command[0] == "login" or command[0] == "newuser":
		# establish a connection to the server
		server.connect((IPAddress, port))
		
		# if the command is 'login': login <username> <password>
		if command[0] == "login":
			# verify the username and password are not empty. if they are, send an error message and repeat the loop. if not, send the message to the server
			try:
				if not command[1] or not command[2]:
					print("Invalid command.\nSyntax: login <username> <password>")
					continue
				else:
					server.send(' '.join(command))
			except:
				print("Invalid command.\nSyntax: login <username> <password>")
				continue
		# if the command is 'newuser': newuser <username> <password>
		elif command[0] == "newuser":
			# verify the username and password are not empty. if they are, send an error message and repeat the loop. if not, send the message to the server
			try:
				if not command[1] or not command[2]:
					print("Invalid command.\nSyntax: newuser <username> <password>")
					continue
				else:
					server.send(' '.join(command))
			except:
				print("Invalid command.\nSyntax: newuser <username> <password>")
				continue

		# set check variable to True, repeat below loop until it is false
		check = True
		while check:
			# establish inputs as the server's messages and keyboard input and listen on them
			socketList = [sys.stdin, server]
			readSockets,writeSocket,errorSocket = select.select(socketList,[],[]) 

			for socks in readSockets: 
				# if the message is from the server
				if socks == server:
					# receive the message from the server
					message = socks.recv(2048)
					
					# if the message is a status message (preceded with a '|'), handle the status message.
					if message == "|login-success":
						print("Welcome to the Chatroom!")
					elif message == "|login-syntaxerror":
						print("Invalid command.\nSyntax: login <username> <password>")
						server.close()
						check = False
						break
					elif message == "|login-useralreadyloggedin":
						print("User is already logged into the chatroom!")
						server.close()
						check = False
						break
					elif message == "|login-chatroomfull":
						print("The chatroom is full!")
						server.close()
						check = False
						break
					elif message == "|login-incorrectpassword":
						print("Incorrect password.")
						server.close()
						check = False
						break
					elif message == "|login-userdne":
						print("The specified user does not exist!")
						server.close()
						check = False
						break
					elif message == "|invalid-command":
						print("Invalid command.")
					elif message == "|newuser-user-exists":
						print("User already exists. Please try a different username.")
						server.close()
						check = False
						break
					elif message == "|newuser-success":
						print("Successfully created user!")
						server.close()
						check = False
						break
					elif message == "|login-currentlyloggedin":
						print("You are already logged in!")
					# if the message was not a status message, print it to the client
					else:
						print(message)
				# if the input is from the keyboard, 
				else:
					# read a line from the console, strip the newline character, and split it into 3 parts as before.
					message = sys.stdin.readline().strip("\n")
					command = message.split(' ', 2)
					
					# if the command is logout, send the logout message to the server, notify the client, 
					# wait 1 second for the server to receive the message, close the connection, and end the loop
					if command[0] == "logout":
						server.send("logout")
						print("You have been logged out.")
						time.sleep(1)
						server.close()
						check = False
						break
					# otherwise, send the message to the server
					else:
						server.send(message)
						if command[0] == "send":
							# if the command was send all, print the message to the client console as well
							try:
								if command[1] == "all":
									print("<You> " + command[2])
							except:
								continue
	# if the command is 'who', notify the user they must be logged in to the server and repeat the loop
	elif command[0] == 'who':
		print("You must be logged in to the chatroom to use who!")
		continue
	# if the command is 'send', notify the user they must be logged in to the server and repeat the loop
	elif command[0] == 'send':
		print("You must be logged in to the chatroom to use send!")
		continue
	# if the command is 'exit', logout the user if they are connected, wait 1 second, 
	# close the connection to the server, and shutdown the client
	elif command[0] == "exit":
		print("Closing Client...")
		try:
			server.send("logout")
			time.sleep(1)
			server.close()
		except:
			pass
		
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)		
	# if the command was not matched, notify the client and repeat the loop
	else:
		print("Invalid command.")
		
		