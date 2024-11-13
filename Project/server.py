import socket
import sys
import threading
import time
import os


# Define socket host, port, website folder path and log file path
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000
WEB_FOLDER = './website'
LOG_FILE_PATH = os.path.join(os.getcwd(), "log.txt")

# Helper function to get the last modified time of a file
def get_last_modified_time(file_path):
    return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(os.path.getmtime(file_path)))

# Helper function to log the response header to a log file
def log_header(header):
    with open(LOG_FILE_PATH, "a") as log_file:
        # Split the header into fields, add brackets around each field, and join them back together
        log_file.write(''.join([f'[{field}]' for field in header.split('\r\n') if field]) + '\n')

# Function to create the HTTP response header
def create_response_header(status_code, content_type, last_modified, connection_type):
    header = f'HTTP/1.1 {status_code} '
    if status_code == 200:
        header += 'OK\r\n'
    elif status_code == 304:
        header += 'Not Modified\r\n'
    elif status_code == 400:
        header += 'Bad Request\r\n'
    elif status_code == 404:
        header += 'File Not Found\r\n'
        content_type = 'N/A'

    header += f'Date: {time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())}\r\n'
    header += f'Connection: {connection_type}\r\n'
    header += 'Keep-Alive: timeout=10, max=100\r\n'
    header += f'Last-Modified: {last_modified}\r\n'
    header += f'Content-Type: {content_type}\r\n\r\n'
    return header


# Handle the HTTP request
def handle_request(client_socket,client_address):
    # Default to persistent connection
    connection_type = 'keep-alive'
    try:
        request = client_socket.recv(1024).decode()  # Receive the request from the client
        # Parse HTTP headers
        headers = request.split('\n')
        fields = headers[0].split()
        if len(fields) >= 2:
            request_type = fields[0] 
            filename = fields[1]
        else:
            client_socket.close()
            print(f'Timeout, the client socket {client_address[0]}:{client_address[1]} has been closed')
            return

        # Indicate request type is GET or HEAD
        if not request_type in ['GET','HEAD']:
            response_header = create_response_header(400, 'text/html', 'N/A',connection_type)
            client_socket.sendall(response_header.encode())
            print(response_header)
            # Log the response header
            log_header(response_header)
            return

        # Default to index.html if root is requested
        if filename == '/':
            filename = '/index.html'

        # Construct the full file path
        file_path = WEB_FOLDER + filename

        # Check if the requested file exists
        if not os.path.isfile(file_path):
            # Send 404 Not Found response
            response_header = create_response_header(404, 'text/html', 'N/A',connection_type)
            client_socket.sendall(response_header.encode())
        else:
            if_modified_since = None

            for header in headers:
                if header.startswith('If-Modified-Since'):
                    if_modified_since = header.split(': ')[1].strip()
                    break
            
            # Detect any if_modified_since
            if if_modified_since:
                if_modified_since = time.mktime(time.strptime(if_modified_since, "%a, %d %b %Y %H:%M:%S"))
                if if_modified_since >= os.path.getmtime(file_path):
                    # Send 304 Not Modified response
                    response_header = create_response_header(304, 'text/html', last_modified,connection_type)
                    client_socket.sendall(response_header.encode())
                    print(response_header)
                    # Log the response header
                    log_header(response_header)
                    return

            
            # Get the last modified time of the file
            last_modified = get_last_modified_time(file_path)
            # Determine the content type based on the file extension
            if filename.endswith('.html'):
                content_type = 'text/html'
            elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif filename.endswith('.png'):
                content_type = 'image/png'
            else:
                # Send 404 Not Found response
                response_header = create_response_header(404, 'text/html', 'N/A',connection_type,connection_type)
                client_socket.sendall(response_header.encode())
                print(response_header)
                # Log the response header
                log_header(response_header)
                return
            
            # Create the response header
            response_header = create_response_header(200, content_type, last_modified,connection_type)
            # Send the response header
            client_socket.sendall(response_header.encode())

            # Send the file content
            if filename.endswith('.html'):
                with open(file_path, 'r') as file:
                    response_data = file.read()
                    client_socket.sendall(response_data.encode())

            else:
                with open(file_path, 'rb') as file:
                    response_data = file.read()
                    client_socket.sendall(response_data)
        
        print(response_header)
        # Log the response header
        log_header(response_header)

    except Exception as e:
        print(f'Error handling request: {e}')
    finally:
        if connection_type != 'close':
            client_socket.close()



# Server Initialization
def run_server():

    # Create socket
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print ("socket successfully created") 
    except socket.error as err:
        print("socket screation failed with error %s" %(err))


    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        print(f'socket binded to {SERVER_PORT}')
        print(f'Server running on {SERVER_HOST}:{SERVER_PORT}')
    except Exception as e:
        print("Socket binding failed with error:" + str(e))
        server_socket.close()
        sys.exit()

    server_socket.listen(5)
    try:
        # Main loop to accept connections
        while True:
            # Wait for client connections
            client_connection, client_address = server_socket.accept()

            print("Got connection from: " + client_address[0] + ":" + str(client_address[1]))
            # Handle client connection in a new thread
            client_handler = threading.Thread(
                target=handle_request,
                args=(client_connection,client_address)
            )
            client_handler.start()
    except KeyboardInterrupt:
        print('Server is shutting down.')
    finally:
        server_socket.close()


# Entry point of the script
if __name__ == '__main__':
    run_server()