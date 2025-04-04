import cv2
import os
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import tkinter as tk
from tkinter import filedialog
def select_file(type,func,title,flag):
    root = tk.Tk()
    root.withdraw()  
    path = ""
    if func == "input":
        if flag == 1:
            path = filedialog.askopenfilename(
                title=title,
                filetypes=[type]
            )
        if flag == 2:
            path = filedialog.askopenfilenames(
                title=title,
                filetypes=[type]
            )
    elif func == "output":
        path = filedialog.askdirectory(
            title=title
        )

    if path:
        print(f"Selected file/folder: {path}")
        return path
    else:
        print("No file selected.")
        return None


AES_KEY_PATH = select_file(("BIN files","*.bin"),"input","Select 256-bit AES key that you want to use",1)

def load_or_generate_key():
    if os.path.exists(AES_KEY_PATH):
        with open(AES_KEY_PATH, "rb") as key_file:
            return key_file.read()
    else:
        key = os.urandom(32)  # 256-bit AES key
        with open(AES_KEY_PATH, "wb") as key_file:
            key_file.write(key)
        return key

Ka = load_or_generate_key()

def decrypt_frames_from_file(file_path, key):
    frames = []
    with open(file_path, "rb") as file:
        while True:
            # Read frame size (4 bytes)
            size_data = file.read(4)
            if not size_data:
                break

            frame_size = int.from_bytes(size_data, 'big')

            # Read IV (12 bytes) and Tag (16 bytes)
            iv = file.read(12)
            tag = file.read(16)

            # Read the encrypted frame bytes
            ciphertext = file.read(frame_size)

            if len(iv) < 12 or len(tag) < 16 or len(ciphertext) < frame_size:
                print("Error: Incomplete frame data, skipping")
                break

            # Decrypt frame
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_frame_data = decryptor.update(ciphertext) + decryptor.finalize()

            frames.append(decrypted_frame_data)

    return frames

def reconstruct_video(frames, output_file):
    if not frames:
        print("No frames to reconstruct!")
        return

    frame_width, frame_height, frame_channels = 640, 480, 3
    fourcc = cv2.VideoWriter.fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, 30.0, (frame_width, frame_height))

    for frame_data in frames:
        try:
            frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((frame_height, frame_width, frame_channels))
            out.write(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except ValueError as e:
            print(f"Error: Frame reshaping failed: {e}")

    out.release()
    cv2.destroyAllWindows()



def main():
    file_path = select_file(("video files","*.mp4"),"input","Select encrypted files for decryption",2)
    for file in file_path:
        output_video_path = file.strip(".mp4")+"_decrypted.avi"
        frames = decrypt_frames_from_file(file, Ka)
        reconstruct_video(frames, output_video_path)
        print(f"Decrypted video saved at {output_video_path}")
    print("Program ended. Press START for decrypting other files")

if __name__ == "__main__":
    main()
