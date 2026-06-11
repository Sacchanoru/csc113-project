###
### arithmetic_server.py
###

import socket
import random

def get_help_text(command=None):
    if command == "ADD":
        return "OK ADD <N1> <N2> to add N1 and N2\n"
    elif command == "SUB":
        return "OK SUB <N1> <N2> to subtract N2 from N1\n"
    elif command == "MUL":
        return "OK MUL <N1> <N2> to multiply N1 by N2\n"
    elif command == "DIV":
        return "OK DIV <N1> <N2> to divide N1 by N2\n"
    elif command == "RND":
        return "OK RND <N> to generate a random number between 1 and N, inclusive\n"
    elif command == "HIST":
        return "OK HIST to show the last 5 valid operations in the session\n"
    elif command == "QUIT":
        return "OK QUIT to end the current session of the arithmetic server\n"
    elif command == "HELP":
        return ("OK HELP [command] to display the syntax and semantics of a specific\n"
                "command. If no command is specified, it will display all the available\n"
                "commands and their meanings\n")
    
    return (
        "OK The following commands are available:\n"
        "ADD <N1> <N2> to add N1 and N2\n"
        "SUB <N1> <N2> to subtract N2 from N1\n"
        "MUL <N1> <N2> to multiply N1 by N2\n"
        "DIV <N1> <N2> to divide N1 by N2\n"
        "RND <N> to generate a random number between 1 and N, inclusive\n"
        "HIST to show the last 5 valid operations in the session\n"
        "HELP [command] to display the syntax and semantics of a specific\n"
        "command. If no command is specified, it will display all the available\n"
        "commands and their meanings\n"
        "QUIT to end the current session of the arithmetic server\n"
    )

def process_command(line, history):
    parts = line.split()
    if not parts:
        return ""
        
    cmd = parts[0].upper()
    args = parts[1:]
    
    try:
        if cmd == "ADD":
            if len(args) != 2: return f"ERR Invalid number of arguments to {cmd}.\n"
            n1, n2 = int(args[0]), int(args[1])
            res = n1 + n2
            history.append(f"ADD {n1} {n2} -> {res}")
            return f"OK {res}\n"
            
        elif cmd == "SUB":
            if len(args) != 2: return f"ERR Invalid number of arguments to {cmd}.\n"
            n1, n2 = int(args[0]), int(args[1])
            res = n1 - n2
            history.append(f"SUB {n1} {n2} -> {res}")
            return f"OK {res}\n"
            
        elif cmd == "MUL":
            if len(args) != 2: return f"ERR Invalid number of arguments to {cmd}.\n"
            n1, n2 = int(args[0]), int(args[1])
            res = n1 * n2
            history.append(f"MUL {n1} {n2} -> {res}")
            return f"OK {res}\n"
            
        elif cmd == "DIV":
            if len(args) != 2: return f"ERR Invalid number of arguments to {cmd}.\n"
            n1, n2 = int(args[0]), int(args[1])
            if n2 == 0:
                return "ERR Division by 0.\n"
            res = n1 // n2
            history.append(f"DIV {n1} {n2} -> {res}")
            return f"OK {res}\n"
            
        elif cmd == "RND":
            if len(args) != 1: return f"ERR Invalid number of arguments to {cmd}.\n"
            n = int(args[0])
            res = random.randint(1, n)
            history.append(f"RND {n} -> {res}")
            return f"OK {res}\n"
            
        elif cmd == "HIST":
            if not history:
                return "OK The last valid operations from this session (up to 5) are:\n"
            
            while len(history) > 5:
                history.pop(0)
                
            resp = "OK The last valid operations from this session (up to 5) are:\n"
            for item in history:
                resp += f"{item}\n"
            return resp
            
        elif cmd == "HELP":
            if len(args) == 1:
                return get_help_text(args[0].upper())
            return get_help_text()
            
        elif cmd == "QUIT":
            return "OK Bye.\n"
            
        else:
            return f"ERR Unknown operation {parts[0]}.\n"
            
    except ValueError:
        return "ERR Non-numeric argument provided.\n"


def handle_client(connection, client_address):
    print(f"Connection established with {client_address}")
    
    connection.sendall(b"OK Welcome to the CSC 113 Arithmetic Server!\n")

    buffer = ""
    history = []
    
    try:
        while True:
            data = connection.recv(1024)
            if not data:
                break
                
            buffer += data.decode('ascii', errors='ignore')
            
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                
                if not line:
                    continue 
                    
                response = process_command(line, history)
                
                if response:
                    connection.sendall(response.encode('ascii'))
                    
                if line.upper() == "QUIT":
                    return
                    
    except ConnectionResetError:
        print(f"Client {client_address} abruptly reset the connection.")
    finally:
        print(f"Closing connection for {client_address}")
        connection.close()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    
    server_address = ('127.0.0.1', 5000)
    print(f"Starting up on {server_address[0]} port {server_address[1]}")
    sock.bind(server_address)
    sock.listen(5)
    
    try:
        while True:
            print('Waiting for a connection...')
            connection, client_address = sock.accept()
            handle_client(connection, client_address)
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()