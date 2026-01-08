\# Blackjack Network Game



A Python-based implementation of a networked Blackjack game using a custom binary protocol over TCP and UDP. This project demonstrates client-server communication, multi-threading, and binary data serialization.



\## Features

\* \*\*Server Discovery:\*\* The server broadcasts "Offer" messages over UDP. Clients automatically discover and connect to the server.

\* \*\*Custom Binary Protocol:\*\* All game states and requests are packed into binary formats using the `struct` module for efficiency and protocol compliance.

\* \*\*Multi-threaded Server:\*\* Supports multiple clients playing simultaneously.

\* \*\*Full Blackjack Logic:\*\* Includes card dealing, Hit/Stand options, and dealer AI (hits until 17).



\## Protocol Details

The game follows a specific message structure:

1\.  \*\*UDP Offer (Server -> Client):\*\* Magic Cookie (4 bytes), Type (1 byte), TCP Port (2 bytes), Server Name (32 bytes).

2\.  \*\*TCP Request (Client -> Server):\*\* Magic Cookie (4 bytes), Type (1 byte), Number of Rounds (1 byte), Team Name (32 bytes).

3\.  \*\*TCP Game Payload (Server -> Client):\*\* Magic Cookie (4 bytes), Type (1 byte), Player Hand Size (1 byte), Dealer Hand Size (1 byte), followed by card data (3 bytes per card).



\## Project Structure

\* `server.py`: The game server. Handles broadcasting and game logic.

\* `client.py`: The game client. Handles server discovery and user interaction.



\## How to Run



\### 1. Start the Server

Run the server first to start broadcasting offers:

```bash

python server.py

