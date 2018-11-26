# Python program to implement client side of chat room. 
import socket 
import select 
import sys 
import time

IP_address = "192.168.1.10"
Port = 12905

while True:
    server = socket.socket()  
    
    print("Please enter a command. Type 'help' to see available commands.")
    command = sys.stdin.readline()
#    command = command.strip('\n')
    command = command.split(' ', 2)

    if command[0] == "login":
        try:
            if (command[1] != "" or command[1] != None) and (command[2] != "" or command[2] != None):
                server.connect((IP_address, Port))
                server.send("login " + str(command[1]) + " " + str(command[2]))
            else:
                print("Invalid command.\nSyntax: login <username> <password>")
                continue
        except:
            print("Invalid command.\nSyntax: login <username> <password>")
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
                        print("Invalid command. Type 'help' for a list of commands.")
                    elif message == "|newuser-user-exists":
                        print("User already exists. Please try a different username.")
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
                    elif command[0] == "newuser":
                        try:
                            if (command[1] != "" or command[1] != None) and (command[2] != "" or command[2] != None):
                                server.send(message)
                            else:
                                print("Invalid command.\nSyntax: newuser <username> <password>")
                                continue
                        except:
                            print("Invalid command.\nSyntax: newuser <username> <password>")
                            continue
                    else:
                        server.send(message)
                        if command[0] == "send":
                            try:
                                if command[1] == "all":
                                    print("<You> " + command[2])
                                else:
                                    print("<You to " + command[1] + "> " + command[2])
                            except:
                                continue
