import socket
import struct

UDP_PORT = 13122
MAGIC_COOKIE_EXPECTED = 0xabcddcba
MESSAGE_TYPE_OFFER = 0x2

def start_client():
    # Create a UDP socket
    client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # Bind the socket to the hardcoded UDP port
    client_udp_socket.bind(('', UDP_PORT))

    print("Client started, listening for offer requests...")

    while True:
        try:
            # Receive message from server
            data, addr = client_udp_socket.recvfrom(1024)

            if len(data) < 39:
                continue # packet to short

            magic_cookie, msg_type, tcp_port, server_name = struct.unpack('!IbH32s', data[:39])

            # Validate magic cookie and message type
            if magic_cookie == MAGIC_COOKIE_EXPECTED and msg_type == MESSAGE_TYPE_OFFER:
                readable_server_name = server_name.decode('utf-8').strip('\x00')
                print(f"Received offer from {addr[0]} ({readable_server_name}), attempting to connect...")

        except Exception as e:
            print(f"Error while listening for offers: {e}")

if __name__ == "__main__":
    start_client()