import argparse
from .receiver_gbn import GBN_Receiver
from .sender_gbn import GBN_Sender

class GBNApp:
    def __init__(
        self,
        role='sender',
        self_port=5000,
        peer_ip='localhost',
        peer_port=5001,
        window_size=4,
        loss_type='none',
        loss_param=0,
    ):
        self.role = role
        self.self_port = self_port
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.window_size = window_size
        self.loss_type = loss_type
        self.loss_param = loss_param
        self.endpoint = self._create_endpoint()

    def _create_endpoint(self):
        if self.role == 'sender':
            return GBN_Sender(
                self.self_port,
                self.peer_ip,
                self.peer_port,
                self.window_size,
                self.loss_type,
                self.loss_param,
            )
        elif self.role == 'receiver':
            return GBN_Receiver(
                self.self_port,
                self.peer_ip,
                self.peer_port,
                self.window_size,
                self.loss_type,
                self.loss_param,
            )
        else:
            raise ValueError("role must be 'sender' or 'receiver'")

    def run(self):
        self.endpoint.run()


def parse_args():
    parser = argparse.ArgumentParser(description='GBN sender/receiver app')
    parser.add_argument('role', nargs='?', choices=['sender', 'receiver'], default='sender', help='Run as sender or receiver')
    parser.add_argument('self_port', nargs='?', type=int, default=5000, help='Local port number')
    parser.add_argument('peer_port', nargs='?', type=int, default=5001, help='Remote port number')
    parser.add_argument('window_size', nargs='?', type=int, default=4, help='Window size')
    parser.add_argument('--peer_ip', default='localhost', help='Peer IP address')
    parser.add_argument('--d', type=int, help='Deterministic loss interval')
    parser.add_argument('--p', type=float, help='Probabilistic loss probability')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.d is not None:
        loss_type = 'deterministic'
        loss_param = args.d
    elif args.p is not None:
        loss_type = 'probabilistic'
        loss_param = args.p
    else:
        loss_type = 'none'
        loss_param = 0

    app = GBNApp(
        args.role,
        args.self_port,
        args.peer_ip,
        args.peer_port,
        args.window_size,
        loss_type,
        loss_param,
    )
    app.run()


if __name__ == '__main__':
    main()
