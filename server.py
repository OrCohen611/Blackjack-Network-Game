import socket
import time
import threading
import struct

UDP_PORT = 13122
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE_OFFER = 0x2
SERVER_NAME = "Need-To-Choose".ljust(32, '\x00')


def send_udp_offers(tcp_port):
    # Create a UDP socket for broadcasting
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Enable broadcasting mode
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Pack the offer message into a binary format according to the protocol
    packet = struct.pack('!IbH32s', MAGIC_COOKIE, MESSAGE_TYPE_OFFER, tcp_port, SERVER_NAME.encode())

    print(f"Server started, listening on IP address {socket.gethostbyname(socket.gethostname())}")

    # Continuously broadcast the offer message until the server is stopped
    while True:
        try:
            # Send the packet to the entire local network on the specified UDP port
            udp_socket.sendto(packet, ('<broadcast>', UDP_PORT))
            time.sleep(1)
        except Exception as e:
            print(f"Error sending UDP offer: {e}")