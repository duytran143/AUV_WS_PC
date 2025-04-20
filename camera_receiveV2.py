import socket
import threading
import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

# ---- CẤU HÌNH ----
VIDEO_PORT   = 5001           # cổng nhận video
CONTROL_PORT = 5002           # cổng gửi lệnh
PI_IP        = '192.168.2.2'  # IP Pi
MAX_DGRAM    = 65535
FPS          = 30
MAX_W, MAX_H = 1270, 720

# ---- Socket nhận video ----
video_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
video_sock.bind(('0.0.0.0', VIDEO_PORT))
video_sock.setblocking(False)

latest_frame = None
frame_lock   = threading.Lock()

def video_receiver():
    global latest_frame
    while True:
        try:
            packet, _ = video_sock.recvfrom(MAX_DGRAM)
            frame_len = int.from_bytes(packet[:4], 'big')
            data = packet[4:]
            while len(data) < frame_len:
                more, _ = video_sock.recvfrom(MAX_DGRAM)
                data += more
            img = cv2.imdecode(
                np.frombuffer(data, dtype=np.uint8),
                cv2.IMREAD_COLOR
            )
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                with frame_lock:
                    latest_frame = img
        except BlockingIOError:
            cv2.waitKey(1)
        except Exception:
            break

# ---- Socket gửi control ----
ctrl_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ctrl_addr = (PI_IP, CONTROL_PORT)

def send_command(cmd: str):
    try:
        ctrl_sock.sendto(cmd.encode(), ctrl_addr)
    except Exception as e:
        print("Send cmd error:", e)

# ---- GUI App với Tkinter ----
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AUV Control Panel")
        self.state('zoomed')
        self.configure(bg='navy')
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ----- LEFT: video canvas -----
        left = tk.Frame(self, bg='navy')
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(left,
                                width=MAX_W, height=MAX_H,
                                bg='navy', highlightthickness=0)
        self.canvas.grid(row=0, column=0)

        # ----- RIGHT: controls -----
        right = tk.Frame(self, bg='navy')
        right.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)
        right.rowconfigure(5, weight=1)

        btns = tk.Frame(right, bg='navy')
        btns.grid(row=1, column=0, rowspan=4, sticky="nsew")
        btns.columnconfigure(0, weight=1)
        for r in range(4):
            btns.rowconfigure(r, weight=1, pad=10)

        font = ("Arial", 18, "bold")
        button_width = 30  # khoảng 60% chiều ngang

        # RUN button
        self.btn_run = tk.Button(
            btns, text="RUN", font=font,
            bg="#aaffaa", activebackground="#00aa00",
            bd=4, relief="raised", width=button_width,
            command=self.toggle_run
        )
        self.btn_run.grid(row=0, column=0)

        # EMERGENCY STOP button
        self.btn_stop = tk.Button(
            btns, text="EMERGENCY STOP", font=font,
            bg="#ff4444", activebackground="#aa0000",
            fg="white", bd=4, relief="raised", width=button_width,
            command=self.toggle_stop
        )
        self.btn_stop.grid(row=1, column=0)

        # Distance Lock toggle
        self.dist_on = False
        self.btn_dist = tk.Button(
            btns, text="Distance Lock OFF", font=font,
            bg="#eecc00", activebackground="#aaaa00",
            bd=4, relief="raised", width=button_width,
            command=self.toggle_dist
        )
        self.btn_dist.grid(row=2, column=0)

        # SURFACE button
        self.btn_surf = tk.Button(
            btns, text="SURFACE", font=font,
            bg="#0066cc", activebackground="#004499",
            fg="white", bd=4, relief="raised", width=button_width,
            command=lambda: send_command("SURFACE")
        )
        self.btn_surf.grid(row=3, column=0)

        # Status Lights placeholder
        status = tk.LabelFrame(right, text="Status Lights",
                               font=("Arial", 14), bg='navy',
                               fg='white', bd=4, labelanchor='n')
        status.grid(row=5, column=0, sticky="se")
        for i in range(3):
            lamp = tk.Label(status, text="   ",
                            bg="grey", bd=2, relief="sunken")
            lamp.grid(row=0, column=i, padx=5)

        # scheduled update
        self.after(int(1000/FPS), self.update_frame)

    def toggle_run(self):
        send_command("RUN")
        self.btn_run.config(relief="sunken", bg="#00aa00")
        self.btn_stop.config(relief="raised", bg="#ff4444")

    def toggle_stop(self):
        send_command("STOP")
        self.btn_stop.config(relief="sunken", bg="#aa0000")
        self.btn_run.config(relief="raised", bg="#aaffaa")

    def toggle_dist(self):
        self.dist_on = not self.dist_on
        if self.dist_on:
            send_command("DIST_ON")
            self.btn_dist.config(text="Distance Lock ON",
                                 bg="#00aa00", fg="white")
        else:
            send_command("DIST_OFF")
            self.btn_dist.config(text="Distance Lock OFF",
                                 bg="#eecc00", fg="black")

    def update_frame(self):
        with frame_lock:
            frame = latest_frame.copy() if latest_frame is not None else None
        if frame is not None:
            h, w = frame.shape[:2]
            scale = min(MAX_W / w, MAX_H / h, 1.0)
            nw, nh = int(w * scale), int(h * scale)
            img = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_AREA)
            photo = ImageTk.PhotoImage(Image.fromarray(img))
            self.canvas.delete("all")
            self.canvas.create_image(MAX_W//2, MAX_H//2,
                                     image=photo, anchor="center")
            self.canvas.image = photo
        self.after(int(1000/FPS), self.update_frame)

if __name__ == "__main__":
    threading.Thread(target=video_receiver, daemon=True).start()
    App().mainloop()
