import os
from datetime import datetime

import socket
import time

HOST = 'IP_of_module_2'  
PORT = 65452  # Port number

base_directory = r"file_path_to_save_our_AES_encrypted_feed_to"

rcv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rcv.bind((HOST, PORT))
rcv.listen()
print("Node 2 is listening on loopback...")

def get_current_hour_folder():
    current_hour = datetime.now().strftime('%Y-%m-%d_%H00')
    folder_path = os.path.join(base_directory, "enc", current_hour)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path



def main():
    start_time = time.time()
    encrypted_frames = []
    while True:
        print("Waiting for a new connection...")
        conn, addr = rcv.accept()
        print(f"Connected to {addr}")

        while True:
            encrypted_frame = conn.recv(1000000)
            if not encrypted_frame:  # 🚀 If empty, sender is gone, break loop
                print("Sender disconnected. Waiting for a new connection...")
                break
            encrypted_frames.append(encrypted_frame)


            if time.time() - start_time >= 10:
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
