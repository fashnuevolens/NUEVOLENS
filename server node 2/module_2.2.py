import os
from datetime import datetime

import socket
import time

HOST = '0.0.0.0'
PORT = 65452  # Port number

base_directory = r"C:\Users\pc\PycharmProjects\NUEVOLENS"

rcv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rcv.bind((HOST, PORT))
rcv.listen()
print("Node 2 is listening on loopback...")

def get_current_hour_folder():
    current_hour = datetime.now().strftime('%Y-%m-%d_%H00')
    folder_path = os.path.join(base_directory, "enc", current_hour)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def recv_all(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def main():
    start_time = time.time()
    encrypted_frames = []
    while True:
        print("Waiting for a new connection...")
        conn, addr = rcv.accept()
        print(f"Connected to {addr}")
        c = 1
        while True:
            encrypted_frame = recv_all(conn, 921632)

            if not encrypted_frame:  # 🚀 If empty, sender is gone, break loop
                print("Sender disconnected. Waiting for a new connection...")
                break
            print(f"{c} : received {len(encrypted_frame)}")
            c = c + 1
            encrypted_frames.append(encrypted_frame)


            if len(encrypted_frames) >= 300:
                save_folder = get_current_hour_folder()
                filename = datetime.now().strftime('%Y-%m-%d_%H%M%S') + ".mp4"
                save_path = os.path.join(save_folder, filename)

                with open(save_path, "wb") as file:
                    for enc_frame in encrypted_frames:
                        file.write(enc_frame)

                print(f"Saved {len(encrypted_frames)} encrypted frames to {save_path}")
                encrypted_frames = []
                start_time = time.time()

main()
