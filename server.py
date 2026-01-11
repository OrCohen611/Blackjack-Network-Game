import socket
import time
import threading
import struct
import random

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

    # Continuously broadcast the offer message until the server is stopped
    while True:
        try:
            # Send the packet to the entire local network on the specified UDP port
            udp_socket.sendto(packet, ('<broadcast>', UDP_PORT))
            time.sleep(1)
        except Exception as e:
            print(f"Error sending UDP offer: {e}")

def handle_client(client_socket, client_address):
    try:
        # Receive request packet
        request_data = client_socket.recv(38)
        if len(request_data) < 38: return
        magic_cookie, msg_type, num_rounds, team_name = struct.unpack('!IbB32s', request_data)

        team_name_str = team_name.decode('utf-8').strip('\x00')
        print(f"Starting {num_rounds} rounds with team: {team_name_str}")

        for r in range(num_rounds):
            player_cards = [get_card(), get_card()]
            dealer_cards = [get_card(), get_card()]

            player_sum = calculate_hand_value(player_cards)
            dealer_sum = calculate_hand_value(dealer_cards)

            # Send initial cards to client
            status_msg = f"\nRound {r + 1}\nYour cards: {player_cards[0][0]},{player_cards[1][0]} (Sum: {player_sum})\n"
            status_msg += f"Dealer's visible card: {dealer_cards[0][0]}\n"
            payload = pack_game_payload(player_cards, dealer_cards)
            client_socket.send(payload)

            time.sleep(0.3)

            # Player turn:
            while player_sum < 21:
                client_socket.send(b"Type 'H' for Hit or 'S' for Stand: ")
                choice = client_socket.recv(1024).decode().strip().lower()

                if choice == 'h':
                    new_card = get_card()
                    player_cards.append(new_card)
                    player_sum = calculate_hand_value(player_cards)
                    client_socket.send(pack_game_payload(player_cards, dealer_cards))
                    time.sleep(0.1)
                else:
                    break

            # Dealer turn:
            if player_sum > 21:
                client_socket.send(b"Bust! You lose this round.\n")
            else:
                client_socket.send(f"Dealer reveals second card: {dealer_cards[1][0]}. Total: {dealer_sum}\n".encode())

                while dealer_sum < 17:
                    new_card = get_card()
                    dealer_cards.append(new_card)
                    dealer_sum = calculate_hand_value(dealer_cards)
                    client_socket.send(f"Dealer draws {new_card[0]}. Dealer sum: {dealer_sum}\n".encode())

                # Determine winner:
                if dealer_sum > 21 or player_sum > dealer_sum:
                    client_socket.send(b"You win!\n")
                elif player_sum < dealer_sum:
                    client_socket.send(b"Dealer wins!\n")
                else:
                    client_socket.send(b"It's a tie!\n")

            time.sleep(0.1)

        client_socket.send(b"\nGame Over. Thanks for playing!\n")

    except Exception as e:
        print(f"Error with client {client_address}: {e}")
    finally:
        client_socket.close()

def pack_game_payload(player_cards, dealer_cards):
    header = struct.pack('!IbBB', MAGIC_COOKIE, 0x4, len(player_cards), len(dealer_cards))
    cards_bytes = b""
    # Combine both hands into one stream of cards
    for rank, suit, value in player_cards + dealer_cards:
        cards_bytes += struct.pack('!HB', rank, suit)

    return header + cards_bytes


def get_card():
    rank = random.randint(1, 13)
    suit = random.randint(0, 3)

    value = 11 if rank == 1 else (10 if rank >= 10 else rank)
    return rank, suit, value


def calculate_hand_value(cards):
    value = 0
    aces = 0

    for _, _, card_val in cards:
        value += card_val
        if card_val == 11:
            aces += 1

    while value > 21 and aces > 0:
        value -= 10
        aces -= 1

    return value


def main():
    # Create a TCP socket for handling game connections
    server_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Bind to an empty string to listen on all interfaces
        server_tcp_socket.bind(('', 0))
        tcp_port = server_tcp_socket.getsockname()[1]

        # Start listening for incoming connections
        server_tcp_socket.listen(5)

        # Start the UDP broadcasting in a separate daemon thread
        udp_thread = threading.Thread(target=send_udp_offers, args=(tcp_port,), daemon=True)
        udp_thread.start()

        local_ip = socket.gethostbyname(socket.gethostname())
        print(f"Server started, listening on IP address {local_ip}")

        while True:
            # wait for a new client to connect via TCP
            client_socket, client_address = server_tcp_socket.accept()
            print(f"New client connected from {client_address}")

            game_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            game_thread.start()

    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_tcp_socket.close()

if __name__ == "__main__":
    main()