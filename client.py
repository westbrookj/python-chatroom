# Python program to implement client side of chat room. 
import socket 
import select 
import sys 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
#if len(sys.argv) != 3: 
#	print "Correct usage: script, IP address, port number"
#	exit() 
IP_address = "192.168.1.10"
Port = 12905

while True:
    print("Please enter a command. Type 'help' to see available commands.")
    command = sys.stdin.readline()
    command = command.strip('\n')
    command = command.split(' ', 3)

    if command[0] == "login":
        if (command[1] == "" or command[1] == None) and (command[2] != "" or command[2] != None):
            print("Invalid command.\nSyntax: login <username> <password>")
        else:
            server.connect((IP_address, Port))
            server.send("|login " + str(command[1]) + str(command[2]))
            
            while True:
                sockets_list = [sys.stdin, server]
                read_sockets,write_socket, error_socket = select.select(sockets_list,[],[]) 
                
                for socks in read_sockets: 
                    if socks == server: 
                        message = socks.recv(2048) 
#                        print message
                        if message == "|login-syntaxerror":
                            print("Invalid command.\nSyntax: login <username> <password>")
                            server.close()
                            break
                        elif message == "|login-useralreadyloggedin":
                            print("User is already logged into the chatroom!")
                            server.close()
                            break
                        elif message == "|login-chatroomfull":
                            print("The chatroom is full!")
                            server.close()
                            break
                        elif message == "|login-incorrectpassword":
                            print("Incorrect password.")
                            server.close()
                            break
                        elif message == "|login-userdne":
                            print("The specified user does not exist!")
                            server.close()
                            break
                    else:
                        message = sys.stdin.readline() 
                        server.send(message) 
                        sys.stdout.write("<You>") 
                        sys.stdout.write(message) 
                        sys.stdout.flush() 

#while True: 
#
#	# maintains a list of possible input streams 
#	sockets_list = [sys.stdin, server] 
#
#	""" There are two possible input situations. Either the 
#	user wants to give manual input to send to other people, 
#	or the server is sending a message to be printed on the 
#	screen. Select returns from sockets_list, the stream that 
#	is reader for input. So for example, if the server wants 
#	to send a message, then the if condition will hold true 
#	below.If the user wants to send a message, the else 
#	condition will evaluate as true"""
#	read_sockets,write_socket, error_socket = select.select(sockets_list,[],[]) 
#
#	for socks in read_sockets: 
#		if socks == server: 
#			message = socks.recv(2048) 
#			print message 
#		else: 
#			message = sys.stdin.readline() 
#			server.send(message) 
#			sys.stdout.write("<You>") 
#			sys.stdout.write(message) 
#			sys.stdout.flush() 
#server.close() 
