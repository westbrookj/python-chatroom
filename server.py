# Name: Joshua Westbrook
# Date: 11/21/2018
# Student ID: 14262905
# CS4850 Lab 3 Chatroom
# Server Application

import socket 
import select 
import sys 
import csv
import os
from thread import *

# sets the IP address for the server
IPAddress = "192.168.1.10" 

# sets the port to use (1 + the last four of my ID 2905)
port = 12905



# Create clientList to track all connections to the server
clientList = [] 

# Create chatroomList to track all connections in the chatroom
chatroomList = []

# Create maxClients
maxClients = 3

# Read the credentials stored in the credentials.csv file
credentials = {}
with open('credentials.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count = 0
	for row in csv_reader:
		credentials[str(row[0])] = str(row[1])
		line_count += 1

# Create the socket to receive connections from clients
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the socket options
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

# Bind the server socket to the IP Address and Port
server.bind((IPAddress, port)) 

# Begin listening for up to 5 connections (more than maxClients to allow clients to still create new users, etc.)
server.listen(100)

print("Chatroom Server (CS4850 - Lab 3)\nPress CTRL-C To Exit\n")

""" 
Define the ClientThread function.

This function creates a thread for each connection that is made to the server and handles all messages transmitted between the client and server.
"""
def ClientThread(conn, addr):
	
	username = None
	
	while True:
		try: 
			# Receive the message from client
			message = conn.recv(2048) 
			
			# If the message is not empty
			if message:
				# Strip newline character from the message
				message = message.strip("\n")
				
				# Parse the message into 3 parts: <command> <option> <option>
				# The third part will contain the remainder of the message sent including any spaces, etc.
				command = message.split(' ', 2)		
			
				# If the command is 'login': login <username> <password>
				if command[0] == "login":
					# verify username and password fields are not empty
					if not command[1] or not command[2]:
						# if username and/or password are empty, send an error message to the client
						conn.send("|login-syntaxerror")
					else:
						# if username is in the credentials file
						if str(command[1]) in credentials:
							# if password from credentials file matches password from message
							if credentials[str(command[1])] == str(command[2]):
								# set error variable to 0 (no error)
								error = 0
								
								# iterate through users in the chatroom to verify the user isn't already logged in
								for (connection, user) in chatroomList:
									# if the user is already logged in, send error message to client & set error variable to 1
									if str(command[1]) == user:
										conn.send("|login-useralreadyloggedin")
										error = 1
										break
									# if the client is already connected to the chatroom, send error message to client & set error variable to 1
									elif connection == conn:
										conn.send("|login-currentlyloggedin")
										error = 1
										break
								# if there are the max number of people in the chatroom, send error to client
								if len(chatroomList) >= maxClients:
									conn.send("|login-chatroomfull")
								# if valid login: set thread's username, add to chatroomList, send proper messages to other clients, and send success message to client
								elif error != 1:
									username = command[1]
									chatroomList.append((conn, username))
									print(username + " has entered the chatroom")
									broadcast(username + " has entered the chatroom", conn)
									conn.send("|login-success")
							# if the password was invalid, send error message to client
							else:
								conn.send("|login-incorrectpassword")
						# if the user was not found in the credentials file, send error message to client
						else:
							conn.send("|login-userdne")
				# if the command is 'who'
				elif command[0] == "who":
					whoList = ""
					
					# iterate through chatroomList and append all usernames to whoList
					for (connection, user) in chatroomList:
						if whoList == "":
							whoList += user
						else:
							whoList += ", " + user
					
					# if there is no one in the chatroom, send empty chat message to client, else send the list to the client
					if whoList == "":
						conn.send("The chatroom is empty!")
					else:
						conn.send(whoList)
				# if the command is 'logout', notify other clients, set thread username to None, and remove from the chatroomList and clientList
				elif command[0] == "logout":
					print(username + " has left the chatroom")
					broadcast(username + " has left the chatroom", conn)
					username = None
					remove(conn, username)
				# if the command is 'send'
				elif command[0] == "send":
					# verify the user is in the chatroom
					if (conn,username) in chatroomList:
						# if the command is 'send all', broadcast the message to other clients
						if command[1] == "all":
							print("<" + username + "> " + command[2]) 
							broadcast("<" + username + "> " + command[2], conn)
						# if the command is 'send <username>'
						else:
							# set sent variable to 0
							sent = 0
							
							# iterate through users in chatroomList
							for (connection,user) in chatroomList:
								# if the user is in the chatroom, send the message to the specified user and send the confirmation back to the client
								if user == command[1]:
									connection.send("<" + username + " to You> " + command[2])
									conn.send("<You to " + user + "> " + command[2])
									sent = 1
									break
							
							# if the message was never delivered, send the error message to the client, otherwise, print on server console
							if sent == 0:
								conn.send("User is not in the chatroom!")
							else:
								print("<" + username + " to " + user + "> " + command[2])
				# if the command is 'newuser'
				elif command[0] == "newuser":
					# check if the user is already in the credentials file (username taken)
					try:
						# if user doesn't exist already, add user to credentials file and sent success messages
						if not command[1] in credentials:
							addUser(str(command[1]), str(command[2]))
							print("User " + str(command[1]) + " created")
							conn.send("|newuser-success")
						# if the user already exists, send error message to client
						else:
							conn.send("|newuser-user-exists")
					# if the check failed, send error message to client
					except:
						conn.send("|newuser-user-exists")
				# if command didn't match any commands, send error message to client
				else:
					conn.send("|invalid-command")
					
				print(chatroomList)
					
			# if the message is empty, remove and disconnect the connection
			else: 
				remove(conn, username)
		# if the receive operation failed, retry
		except: 
			continue

"""
Function to add a user to the credentials file
"""
def addUser(username, password):
	# adds to credentials list
	credentials[username] = password
	
	# adds to credentials file
	with open('credentials.csv', 'a') as file:
		file.write(username + "," + password + "\n")
			
"""
Function to broadcast the message to all clients in the chatroom except the client sending it.
"""
def broadcast(message, connection): 
	# iterate through the chatroomList and send message to them if they aren't the sender.
	for (client,username) in chatroomList: 
		if client != connection: 
			try:
				client.send(message) 
			except: 
				# close the connection if sending the message fails
				client.close() 

				# remove the client from the server if sending the message fails
				remove(client, username) 

"""
Function to remove the specified connection from the clientList and chatroomList
"""
def remove(connection, username):
	if (connection,username) in chatroomList: 
		chatroomList.remove((connection,username))

	if (connection,username) in clientList:
		clientList.remove((connection,username))

"""
Loop to listen for new connections and accept them.
"""
while True:
	# try to accept an incoming connection
	try:
		conn, addr = server.accept()
	# if there is a keyboard interrupt, shutdown the application
	except KeyboardInterrupt:
		print("\nShutting Down...")

		server.close()
		
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)

	# if the connection is successfully accepted, add to the clientList
	clientList.append(conn) 

	# starts a new instance of ClientThread and passes the connection as the parameter
	start_new_thread(ClientThread, (conn, addr))	 

conn.close() 
server.close() 