import socket, threading, cv2, numpy as np

# CONFIG
PORT      = 5001
MAX_DGRAM = 65535

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', PORT))

latest = None
lock = threading.Lock()

def receiver():
    global latest
    while True:
        packet, _ = sock.recvfrom(MAX_DGRAM)
        frame_len = int.from_bytes(packet[:4], 'big')
        data = packet[4:]
        while len(data) < frame_len:
            more, _ = sock.recvfrom(MAX_DGRAM)
            data += more
        frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8),
                             cv2.IMREAD_COLOR)
        if frame is not None:
            with lock:
                latest = frame

# start receiver thread
threading.Thread(target=receiver, daemon=True).start()

try:
    while True:
        with lock:
            frame = latest.copy() if latest is not None else None
        if frame is not None:
            cv2.imshow('fast UDP w/ overlay v2', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    sock.close()
    cv2.destroyAllWindows()
