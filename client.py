import socket
import struct

UDP_PORT = 13122
MAGIC_COOKIE_EXPECTED = 0xabcddcba
MESSAGE_TYPE_OFFER = 0x2
MESSAGE_TYPE_REQUEST = 0x3
TEAM_NAME = "Need-To-Choose".ljust(32, '\x00')


def get_card_display(rank, suit):
    rank_map = {1: "Ace", 11: "Jack", 12: "Queen", 13: "King"}
    suit_map = {0: "Spades", 1: "Clubs", 2: "Hearts", 3: "Diamonds"}

    rank_str = rank_map.get(rank, str(rank))
    suit_str = suit_map.get(suit, "Unknown")

    return f"{rank_str} of {suit_str}"


def start_client():
    # Create a UDP socket
    client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the hardcoded UDP port
    client_udp_socket.bind(('', UDP_PORT))

    while True:
        try:
            print("Client started, listening for offer requests...")
            # Receive message from server
            data, addr = client_udp_socket.recvfrom(1024)

            if len(data) < 39:
                continue # packet to short

            magic_cookie, msg_type, tcp_port, server_name = struct.unpack('!IbH32s', data[:39])

            # Validate magic cookie and message type
            if magic_cookie == MAGIC_COOKIE_EXPECTED and msg_type == MESSAGE_TYPE_OFFER:
                readable_server_name = server_name.decode('utf-8').strip('\x00')
                print(f"Received offer from {addr[0]} ({readable_server_name}), attempting to connect...")

                send_game_request(addr[0], tcp_port)

        except Exception as e:
            print(f"Error while listening for offers: {e}")

def unpack_game_payload(data):
    magic, msg_type, p_size, d_size = struct.unpack('!IbBB', data[:7])

    cards = []
    offset = 7
    # Extract each card
    for _ in range(p_size + d_size):
        rank, suit = struct.unpack('!HB', data[offset:offset + 3])
        cards.append((rank, suit))
        offset += 3

    player_hand = cards[:p_size]
    dealer_hand = cards[p_size:]
    return player_hand, dealer_hand


def send_game_request(server_ip, server_port):

    try:
        # Ask the user for the number of rounds
        num_rounds = int(input("How many rounds do you want to play? "))

        # Create a TCP socket
        client_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_tcp_socket.connect((server_ip, server_port))

        # Pack the Request message
        request_packet = struct.pack('!IbB32s', MAGIC_COOKIE_EXPECTED, MESSAGE_TYPE_REQUEST, num_rounds, TEAM_NAME.encode())

        # Send the packet
        client_tcp_socket.send(request_packet)
        suits_symbols = {0: 'Hearts', 1: 'Diamonds', 2: 'Clubs', 3: 'Spades'}

        # Continuous game loop
        while True:
            # Receive data from the server
            data = client_tcp_socket.recv(1024)
            if not data:
                break

            if len(data) >= 7 and struct.unpack('!I', data[:4])[0] == MAGIC_COOKIE_EXPECTED:
                p_hand, d_hand = unpack_game_payload(data)

                print("\n--- Current Game State ---")
                p_display = [get_card_display(c[0], c[1]) for c in p_hand]
                p_sum = sum(11 if c[0] == 1 else (10 if c[0] >= 10 else c[0]) for c in p_hand)
                print(f"Your cards: {p_display} (Sum: {p_sum})")
                print(f"Dealer's visible card: {d_hand[0][0]} of {suits_symbols.get(d_hand[0][1], 'Unknown')}")
                print("------------------------------------------\n")
            else:
                message = data.decode(errors='ignore')
                print(message, end="")

                # Check if the server is asking for a move
                if "Type 'H' for Hit or 'S' for Stand:" in message:
                    action = input().strip()
                    client_tcp_socket.send(action.encode())

                # If the game is over - the server will close the connection and we break
                if "Game Over" in message:
                    break

    except Exception as e:
        print(f"Failed to connect or send request: {e}")


if __name__ == "__main__":
    start_client()
