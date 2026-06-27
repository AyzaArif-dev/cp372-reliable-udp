import socket
import base64
from shared.packet import make_packet, parse_packet

HOST = "0.0.0.0"
PORT = 5000

LOSS_RATE = 0.2  # change for testing later


def should_drop():
    import random
    return random.random() < LOSS_RATE


def run_receiver(output_file="received.txt"):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))

    expected_seq = 0

    file = open(output_file, "wb")

    print("Receiver running...")

    while True:
        data, addr = sock.recvfrom(4096)

        if should_drop():
            print("Packet dropped (simulated)")
            continue

        pkt = parse_packet(data)
        if not pkt:
            continue

        ptype = pkt["type"]
        seq = pkt["seq"]

        # START
        if ptype == "START":
            print("START received")
            sock.sendto(make_packet("ACK", ack=seq), addr)
            expected_seq = 1

        # DATA
        elif ptype == "DATA":
            if seq == expected_seq:
                decoded = base64.b64decode(pkt["payload"])
                file.write(decoded)

                print(f"Accepted seq={seq}")

                sock.sendto(make_packet("ACK", ack=seq), addr)
                expected_seq += 1

            else:
                print(f"Discarded seq={seq}")

                sock.sendto(make_packet("ACK", ack=expected_seq - 1), addr)

        # END
        elif ptype == "END":
            print("END received")

            sock.sendto(make_packet("ACK", ack=seq), addr)
            break

    file.close()
    sock.close()
    print("File transfer complete")


if __name__ == "__main__":
    run_receiver()