#!/usr/bin/env python3
"""
Client script on Windows to read joystick and send TCP commands to Raspberry Pi.
Automatically retries connection if Pi node isn't up yet, and attempts to reconnect on send failure.
"""
import pygame
import socket
import time

# Configuration
HOST = "192.168.2.2"  # IP of Raspberry Pi
PORT = 5000           # Port of joystick_input_node
RECONNECT_DELAY = 1.0  # seconds
def connect_to_pi(host, port):
    """Attempt to connect, retrying until successful."""
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            print(f"✅ Connected to {host}:{port}")
            return sock
        except Exception as e:
            print(f"❌ Connection failed: {e}. Retrying in {RECONNECT_DELAY}s...")
            time.sleep(RECONNECT_DELAY)


def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No joystick detected. Exiting.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    # Connect to Pi
    sock = connect_to_pi(HOST, PORT)

    try:
        while True:
            pygame.event.pump()

            # Read joystick axes and buttons
            left_x   = round(joystick.get_axis(0), 2)
            left_y   = round(joystick.get_axis(1), 2)
            right_x  = round(joystick.get_axis(2), 2)
            right_y  = round(joystick.get_axis(3), 2)
            left_z   = round(joystick.get_axis(4), 2)
            right_z  = round(joystick.get_axis(5), 2)
            hat_x, hat_y = joystick.get_hat(0)
            buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

            # Format data string
            data = f"{left_x} {left_y} {right_x} {right_y} {left_z} {right_z} {hat_x} {hat_y} {''.join(str(b) for b in buttons)}"
            print(f"Sending: {data}", end='\r')

            # Send and handle failure
            try:
                sock.sendall((data + "\n").encode())
            except Exception as e:
                print(f"\n❌ Send failed: {e}. Reconnecting...")
                sock.close()
                sock = connect_to_pi(HOST, PORT)

            # Exit on Start button (commonly button 7 or 8)
            if joystick.get_button(7) or joystick.get_button(8):
                print("\n🛑 Exit command received. Shutting down.")
                break

            pygame.time.wait(100)

    finally:
        sock.close()
        pygame.quit()

if __name__ == '__main__':
    main()
