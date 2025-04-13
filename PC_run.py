import multiprocessing
import os

# Chạy test_joystickV2.py
def run_joystick():
    os.system("python test_joystickV2.py")

# Chạy camera_receive.py
def run_camera():
    os.system("python camera_receive.py")

if __name__ == "__main__":
    # Tạo các tiến trình cho joystick và camera
    joystick_process = multiprocessing.Process(target=run_joystick)
    camera_process = multiprocessing.Process(target=run_camera)

    # Khởi động các tiến trình
    joystick_process.start()
    camera_process.start()

    # Đợi cho các tiến trình hoàn tất
    joystick_process.join()
    camera_process.join()
