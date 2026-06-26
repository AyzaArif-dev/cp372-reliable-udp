import argparse
import socket
import time
import random

class GBN_Receiver:
    """
    GBN Receiver class
    """
    def __init__(self, self_port, peer_address, peer_port, window_size, loss_type, n):
        self.self_port = self_port
        self.peer_address = peer_address
        self.peer_port = peer_port
        self.window_size = window_size
        self.loss_type = loss_type
        self.n = n
        self.base = 0
        self.packet_loss_count = 0
        self.total_packets_count = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', self.self_port))
        self.socket.settimeout(None)
        self.last_packet_received = -1

   
    def run(self):
        """
        Main function the receive the packets and send acknowledgements
        """
        while True:
            try:
                packet, address = self.socket.recvfrom(1024)
                packet_num, packet_content = self.unpack_packet(packet)
                print(packet_num)
                self.total_packets_count += 1
                if self.loss_or_not(packet_num):
                    print(f"Packet {packet_num} discarded")
                    self.packet_loss_count += 1
                    # Do not send ACK for a lost packet
                    continue

                # Accept only the expected packet
                if packet_num == self.base:
                    print(f"[{time.time()}] Packet{packet_num} {packet_content} received")
                    self.last_packet_received = packet_num
                    self.base += 1
                else:
                    # Discard out-of-order packets
                    print(f"[{time.time()}] Packet{packet_num} out of order discarded, expecting packet{self.base}")

                # Send cumulative ACKs for the last in-order packet received
                ack_num = self.base - 1
                ack = self.make_ack(ack_num)
                self.send_ack(ack)
                print(f"[{time.time()}] ACK{ack_num} sent expecting packet{self.base}")
               
            except socket.timeout:
                # Timeout occurred while waiting for packets.
                if self.base > 0:
                    ack = self.make_ack(self.base - 1)
                    self.send_ack(ack)
                continue
           
        self.socket.close()
        if self.total_packets_count != 0:
            loss_rate = round(self.packet_loss_count / self.total_packets_count, 2)
            print(f"[Summary] {self.packet_loss_count}/{self.total_packets_count} packets discarded, loss rate = {loss_rate}%")


    def make_ack(self, packet_num):
        """
        Function to make an acknowledgment
        """
        ack = f"ACK:{packet_num}"
        return ack.encode()

    def send_ack(self, ack):
        """
        Function to send an acknowledgment 
        """
        self.socket.sendto(ack, (self.peer_address, self.peer_port))

    def unpack_packet(self, packet):
        """
        To decode the packets received
        """
        packet_num, packet_content = packet.decode().split(':')
        packet_num = int(packet_num)
        return packet_num, packet_content

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
   