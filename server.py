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
                command = message.split(' ', 2)
#                print(command)            
            
                if command[0] == "login":
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
                                    chatroomList.append((conn, username))
#                                    print(chatroomList)
                                    print(username + " has entered the chatroom")
                                    broadcast(username + " has entered the chatroom", conn)
#                                    time.sleep(1)
                                    conn.send("|login-success")
                            else:
                                conn.send("|login-incorrectpassword")
#                                conn.close()
                        else:
                            conn.send("|login-userdne")
#                            conn.close()
                            
                    print(chatroomList)
                elif command[0] == "who":
                    whoList = ""
                    for (connection, user) in chatroomList:
                        if whoList == "":
                            whoList += user
                        else:
                            whoList += ", " + user
                        
                    if whoList == "":
                        conn.send("The chatroom is empty!")
                    else:
                        conn.send(whoList)
                elif command[0] == "logout":
#                    conn.close()
                    print(username + " has left the chatroom")
                    broadcast(username + " has left the chatroom", conn)
                    remove(conn, username)
                elif command[0] == "send":
                    if (conn,username) in chatroomList:
                        if command[1] == "all":
                            """prints the message and address of the 
                            user who just sent the message on the server 
                            terminal"""
                            print("<" + username + "> " + command[2])

                            # Calls broadcast function to send message to all 
                            broadcast("<" + username + "> " + command[2], conn)
                        else:
                            sent = 0
                            for (connection,user) in chatroomList:
                                if user == command[1]:
                                    connection.send("<" + username + " to You> " + command[2])
                                    sent = 1
                                    break
                            if sent == 0:
                                conn.send("User is not in the chatroom!")
                            else:
                                print("<" + username + " to " + user + "> " + command[2])
                elif command[0] == "newuser":
                    try:
                        if not command[1] in credentials:
                            addUser(str(command[1]), str(command[2]))
                            conn.send("|newuser-success")
                        else:
                            conn.send("|newuser-user-exists")
                    except:
                        conn.send("|newuser-user-exists")
                else:
                    conn.send("|invalid-command")
            else: 
                """message may have no content if the connection 
                is broken, in this case we remove the connection"""
                remove(conn, username)

        except: 
            continue

def addUser(username, password):
    credentials[username] = password
    fields=[username, password]
    
    with open('credentials.csv', 'a') as file:
        file.write(username + "," + password + "\n")
            
"""Using the below function, we broadcast the message to all 
clients who's object is not the same as the one sending 
the message """
def broadcast(message, connection): 
    for (client,username) in chatroomList: 
        if client != connection: 
			try: 
				client.send(message) 
			except: 
				client.close() 

				# if the link is broken, we remove the client 
				remove(client, username) 

"""The following function simply removes the object 
from the list that was created at the beginning of 
the program"""
def remove(connection, username):
    if (connection,username) in chatroomList: 
        chatroomList.remove((connection,username))

    if (connection,username) in clientList:
        clientList.remove((connection,username))

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

	# creates and individual thread for every user 
	# that connects 
	start_new_thread(clientthread,(conn,addr))	 

conn.close() 
server.close() 