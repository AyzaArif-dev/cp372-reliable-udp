"""Implement sender:
Send multiple packets without waiting
Timer for oldest unacknowledged packet
Process cumulative ACKs
Retransmit window after timeout"""

import socket
import time
import random

class GBN_Sender:
    """
    GBN Sender Class
    """
    def __init__(self, self_port, peer_address, peer_port, window_size, loss_type, n):
        self.self_port = self_port
        self.peer_address = peer_address
        self.peer_port = peer_port
        self.window_size = window_size
        self.loss_type = loss_type
        self.n = n
        self.base = 0
        self.next_seqnum = 0
        self.timer_running = False
        self.packet_loss_count = 0
        self.total_packets_sent = 0
        self.total_acks_received = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', self.self_port))
        self.socket.settimeout(0.05)
        self.buffer = []
        self.start_time = 0

    def run(self):
        while True:
            message = input("node>")
            if message == 'exit':
                break
            elif message.startswith("send "):
                payload = message.split("send ")[1]
                for i in payload:
                    packet = self.make_packet(i.encode())
                    self.buffer.append(packet)
                    # Send multiple packets without waiting for each ACK
                    if self.next_seqnum < self.base + self.window_size:
                        self.send_packet(packet)
                        self.total_packets_sent += 1
                        # Start timer for the oldest unacknowledged packet
                        if not self.timer_running:
                            self.start_timer()
                            self.start_time = time.time()
                        self.next_seqnum += 1
                    else:
                        print(f"Window full, waiting for ACKs...")
                    while self.base < self.next_seqnum:
                        self.ack_rcvd()

        self.socket.close()
        loss_rate = round(self.packet_loss_count / self.total_acks_received, 2) if self.total_acks_received != 0 else 0
        print(f"[Summary] {self.packet_loss_count}/{self.total_acks_received} packets discarded, loss rate = {loss_rate}%")

    def ack_rcvd(self):
        """
        Function to deal with the acknowledgements received
        """
        try:
            packet, address = self.socket.recvfrom(1024)
            if not packet:
                print("no packets received")
                return

            ack = self.extract_ack(packet)
            self.total_acks_received += 1
            if ack < self.base:
                print(f"[{time.time()}] duplicate ACK{ack} ignored")
                return

            if self.loss_or_not(ack):
                print(f"ACK{ack} discarded")
                self.packet_loss_count += 1
                return

            # Process cumulative ACKs: ACK n means all packets up to n are received
            print(f"[{time.time()}] ACK{ack} received, window moves to {ack + 1}")
            num_new_acks = ack - self.base + 1
            self.base = ack + 1
            if self.base == self.next_seqnum:
                self.stop_timer()
            else:
                self.start_timer()
                self.start_time = time.time()

            # Remove acknowledged packets from the send buffer
            self.buffer = self.buffer[num_new_acks:]
        except (socket.timeout, ConnectionResetError) as e:
            if isinstance(e, ConnectionResetError):
                print(f"[{time.time()}] connection reset by remote host, retrying packet{self.base}")
            else:
                print(f"[{time.time()}] packet{self.base} timeout")
            # Retransmit the entire current window after timeout or connection reset
            self.timer_running = False
            self.next_seqnum = self.base
            for packet in self.buffer:
                self.send_packet(packet)
                self.next_seqnum += 1


    def make_packet(self, message):
        """
        Function to make packets to send to the peer port
        """
        seqnum = self.next_seqnum
        packet = b'%d:%s' % (seqnum, message)
        return packet

    def send_packet(self, packet):
        """
        Function to send the packet
        """
        seqnum = int(packet.decode().split(':', 1)[0])
        print(f"[{time.time()}] packet{seqnum} {packet.decode()} sent")
        self.socket.sendto(packet, (self.peer_address, self.peer_port))

    def extract_ack(self, packet):
        """
        Function to extract the acknowledgement received
        """
        return int(packet.decode().split(':')[1])

    def start_timer(self):
        """
        Function to keep track of the time when packet is sent and the timer is started
        """
        self.timer_running = True
        # print(f"[{time.time()}] timer started")

    def stop_timer(self):
        """
        Function to keep track of the time when the acknowledgement is received and the timer is stopped

        """
        self.timer_running = False
        # print(f"[{time.time()}] timer stopped")

    def loss_or_not(self, ack):
        """
        function to determine the loses
        """
        if self.loss_type == "deterministic":
            if ack != 0 and ack % self.n == 0:
                return True
            else:
                return False
        elif ack != 0 and self.loss_type == "probabilistic":
            if random.random() < self.n:
                return True
            else:
                return False


