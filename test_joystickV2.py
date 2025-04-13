import pygame
import socket

pygame.init()
pygame.joystick.init()

# Kiểm tra nếu không có tay cầm nào
if pygame.joystick.get_count() == 0:
    print("Không tìm thấy tay cầm nào!")
    pygame.quit()
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

HOST = "192.168.2.2"  # IP tĩnh của Raspberry Pi
PORT = 5000           # Cổng lắng nghe trên Pi

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

try:
    while True:
        pygame.event.pump()

        # Đọc giá trị joystick trái (trục X và Y) và joystick phải (trục X và Y)
        left_x = round(joystick.get_axis(0), 2)  # Joystick trái trục X
        left_y = round(joystick.get_axis(1), 2)  # Joystick trái trục Y
        right_x = round(joystick.get_axis(2), 2) # Joystick phải trục X
        right_y = round(joystick.get_axis(3), 2) # Joystick phải trục Y
        left_z = round(joystick.get_axis(4), 2) # Left trigger
        right_z = round(joystick.get_axis(5), 2) # Right trigger

        # Đọc trạng thái các nút bấm (0 hoặc 1) và nối thành chuỗi
        buttons = "".join(str(joystick.get_button(i)) for i in range(joystick.get_numbuttons()))

        # Đọc trạng thái các hat
        hat_x, hat_y = joystick.get_hat(0) 
        # Chuỗi dữ liệu đầu ra: Joystick trái - Joystick phải - Nút bấm (chỉ số, phân cách bởi dấu cách)
        data = f"{left_x} {left_y} {right_x} {right_y} {left_z} {right_z} {hat_x} {hat_y} {buttons}"
        
        print(f"\r{data}", end="", flush=True)  # In trên một hàng ngang duy nhất

        # Gửi dữ liệu đến Raspberry Pi
        sock.sendall((data + "\n").encode())

        # Nếu nhấn nút "Start", thoát chương trình
        if joystick.get_button(7) or joystick.get_button(8):
            print("\nThoát chương trình!")
            break

        pygame.time.wait(100)

finally:
    sock.close()
    pygame.quit()
