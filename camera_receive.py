import cv2
import socket
import numpy as np

# Cấu hình socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host_ip = '192.168.2.1'  # Địa chỉ IP của Raspberry Pi
port = 5001
socket_address = (host_ip, port)

# Liên kết socket
client_socket.bind(socket_address)

frame_data = b""  # Dữ liệu video đã nhận

while True:
    data, addr = client_socket.recvfrom(65536)  # Nhận gói UDP
    frame_data += data  # Nối các phần dữ liệu lại với nhau

    # Kiểm tra xem dữ liệu có đủ để giải mã không
    try:
        frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
        if frame is not None:
            cv2.imshow('Received Video', frame)
        frame_data = b""  # Đặt lại buffer sau khi đã giải mã thành công
    except Exception as e:
        pass  # Bỏ qua nếu chưa đủ dữ liệu để giải mã

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

client_socket.close()
cv2.destroyAllWindows()
