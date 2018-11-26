# Python program to implement server side of chat room. 
import socket 
import select 
import sys 
import csv
from thread import *

"""The first argument AF_INET is the address domain of the 
socket. This is used when we have an Internet Domain with 
any two hosts The second argument is the type of socket. 
SOCK_STREAM means that data or characters are read in 
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

# checks whether sufficient arguments have been provided 
#if len(sys.argv) != 3: 
#	print "Correct usage: script, IP address, port number"
#	exit() 

# takes the first argument from command prompt as IP address 
IP_address = "192.168.1.10" 

# takes second argument from command prompt as port number 
Port = 12905 

credentials = {}
with open('credentials.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        credentials[str(row[0])] = str(row[1])
        line_count += 1
    
    print(row[0] + " : " + row[1])
    
print(credentials)

""" 
binds the server to an entered IP address and at the 
specified port number. 
The client must be aware of these parameters 
"""
server.bind((IP_address, Port)) 

""" 
listens for 100 active connections. This number can be 
increased as per convenience. 
"""
server.listen(100) 

clientList = [] 
chatroomList = []
MAXCLIENTS = 3

def clientthread(conn, addr):
    
    username = None
    
    while True:
        try: 
            message = conn.recv(2048) 
            if message:
                message = message.strip("\n")
#                print(message)
                command = message.split(' ', 5)
                print(command)            
            
                if command[0] == "|login":
                    if (command[1] == "" or command[1] == None) and (command[2] != "" or command[2] != None):
                        conn.send("|login-syntaxerror")
#                        conn.close()
                    else:
                        if str(command[1]) in credentials:
                            if credentials[str(command[1])] == str(command[2]):
                                if str(command[1]) in chatroomList:
                                    conn.send("|login-useralreadyloggedin")
#                                    conn.close()
                                if len(chatroomList) >= MAXCLIENTS:
                                    conn.send("|login-chatroomfull")
#                                    conn.close()
                                else:
                                    username = command[1]
                                    chatroomList.append({
                                                            "connection":conn,
                                                            "username":username
                                                        })
#                                    print(chatroomList)
                                    print(username + " has entered the chatroom")
                                    broadcast(username + " has entered the chatroom")
                                    conn.send("Welcome to the Chat Room!")
                            else:
                                conn.send("|login-incorrectpassword")
#                                conn.close()
                        else:
                            conn.send("|login-userdne")
#                            conn.close()
                            
                    print(chatroomList)
                elif command[0] == "who" or command[0] == "|who":
                    whoList = ""
                    for pair in chatroomList:
                        if whoList == "":
                            whoList += pair["username"]
                        else:
                            whoList += ", " + pair["username"]
                        
                    if whoList == "":
                        conn.send("The chatroom is empty!")
                    else:
                        conn.send(whoList)
                elif command[0] == "|logout":
#                    conn.close()
                    remove(conn)
                    print(username + " has left the chatroom")
                    broadcast(username + " has left the chatroom")
                else:
#                    if conn in chatroomList:
                    """prints the message and address of the 
                    user who just sent the message on the server 
                    terminal"""
                    print("<" + username + "> " + message)

                    # Calls broadcast function to send message to all 
                    broadcast("<" + username + "> " + message, conn)
                
                whoList = ""
                for pair in chatroomList:
                    if whoList == "":
                        whoList += pair["username"]
                    else:
                        whoList += ", " + pair["username"]
                print("Chatroom: " + whoList)
            else: 
                """message may have no content if the connection 
                is broken, in this case we remove the connection"""
                remove(conn)

        except: 
            continue

"""Using the below function, we broadcast the message to all 
clients who's object is not the same as the one sending 
the message """
def broadcast(message, connection): 
    for pair in chatroomList: 
        if pair["connection"] != connection: 
			try: 
				pair["connection"].send(message) 
			except: 
				pair["connection"].close() 

				# if the link is broken, we remove the client 
				remove(pair["connection"]) 

"""The following function simply removes the object 
from the list that was created at the beginning of 
the program"""
def remove(connection): 
    for pair in clientList:
        if pair["connection"] == connection:
            clientList.remove(pair)
            break

while True: 

	"""Accepts a connection request and stores two parameters, 
	conn which is a socket object for that user, and addr 
	which contains the IP address of the client that just 
	connected"""
	conn, addr = server.accept() 

	"""Maintains a list of clients for ease of broadcasting 
	a message to all available people in the chatroom"""
	clientList.append(conn) 

	# prints the address of the user that just connected 
#	print addr[0] + " connected"

	# creates and individual thread for every user 
	# that connects 
	start_new_thread(clientthread,(conn,addr))	 

conn.close() 
server.close() 