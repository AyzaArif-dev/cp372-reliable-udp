import json

# -----------------------------
# Packet Creation
# -----------------------------

def make_packet(packet_type, seq=0, ack=0, payload=""):
    packet = {
        "type": packet_type,
        "seq": seq,
        "ack": ack,
        "payload": payload
    }
    return json.dumps(packet).encode()


# -----------------------------
# Packet Decoding
# -----------------------------

def parse_packet(data):
    try:
        packet = json.loads(data.decode())
        return packet
    except:
        return None