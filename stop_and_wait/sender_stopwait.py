import socket
import time
import base64
import os

from shared.packet import make_packet, parse_packet

SERVER_ADDR = ("127.0.0.1", 5000)
TIMEOUT = 1
CHUNK_SIZE = 1024


# -----------------------------
# Read file in chunks
# -----------------------------
def read_file_chunks(filename, chunk_size=CHUNK_SIZE):
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


# -----------------------------
# Send packet and wait for ACK
# -----------------------------
def send_and_wait(sock, packet, expected_seq):
    while True:
        sock.sendto(packet, SERVER_ADDR)

        try:
            data, _ = sock.recvfrom(4096)
            ack = parse_packet(data)

            if ack and ack["type"] == "ACK" and ack["ack"] == expected_seq:
                return

        except socket.timeout:
            print(f"Timeout → resending seq {expected_seq}")


# -----------------------------
# Main file transfer function
# -----------------------------
def send_file(filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    seq = 0

    # ---------------- START ----------------
    print("Sending START packet")
    start_pkt = make_packet("START", seq=seq, payload="FILE_TRANSFER")
    send_and_wait(sock, start_pkt, seq)
    seq += 1

    # ---------------- DATA ----------------
    for chunk in read_file_chunks(filename):
        encoded = base64.b64encode(chunk).decode()

        pkt = make_packet("DATA", seq=seq, payload=encoded)
        print(f"Sending DATA seq={seq}")

        send_and_wait(sock, pkt, seq)
        seq += 1

    # ---------------- END ----------------
    print("Sending END packet")
    end_pkt = make_packet("END", seq=seq, payload="EOF")
    send_and_wait(sock, end_pkt, seq)

    print("File transfer complete")
    sock.close()


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    file_path = os.path.join("tests", "test.txt")
    send_file(file_path)