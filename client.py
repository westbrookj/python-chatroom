# Python program to implement client side of chat room. 
import socket 
import select 
import sys 
import time
import os

IP_address = "192.168.1.10"
Port = 12905

print("Chatroom Client (CS4850 - Lab 3)\n")

while True:
	server = socket.socket()  
	
	print("Please enter a command.")
	command = sys.stdin.readline()
	command = command.strip('\n')
	command = command.split(' ', 2)
#	print(command)

	if command[0] == "login" or command[0] == "newuser":
		server.connect((IP_address, Port))
		if command[0] == "login":
			try:
				if (command[1] == "" or command[1] == None) or (command[2] == "" or command[2] == None):
					print("Invalid command.\nSyntax: login <username> <password>")
					continue
				else:
					server.send(' '.join(command))
			except:
				print("Invalid command.\nSyntax: login <username> <password>")
				continue
		elif command[0] == "newuser":
			try:
				if (command[1] == "" or command[1] == None) or (command[2] == "" or command[2] == None):
					print("Invalid command.\nSyntax: newuser <username> <password>")
					continue
				else:
					server.send(' '.join(command))
			except:
				print("Invalid command.\nSyntax: newuser <username> <password>")
				continue

		check = True
		while check:
			sockets_list = [sys.stdin, server]
			read_sockets,write_socket, error_socket = select.select(sockets_list,[],[]) 

			for socks in read_sockets: 
				if socks == server: 
					message = socks.recv(2048)
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
					elif message == "|newuser-success-notloggedin":
						print("Successfully created user!")
						server.close()
						check = False
						break
					elif message == "|newuser-success-loggedin":
						print("Successfully created user!")
					elif message == "|login-currentlyloggedin":
						print("You are already logged in!")
					else:
						print(message)
				else:
					message = sys.stdin.readline().strip("\n")
					command = message.split(' ', 2)
					if command[0] == "logout":
						server.send("logout")
						print("You have been logged out.")
						time.sleep(1)
						server.close()
						check = False
						break
					else:
						server.send(message)
						if command[0] == "send":
							try:
								if command[1] == "all":
									print("<You> " + command[2])
#								else:
#									print("<You to " + command[1] + "> " + command[2])
							except:
								continue
	elif command[0] == "exit":
		print("Closing Client...")
		
		try:
			server.close()
		except:
			pass
		
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
		
		