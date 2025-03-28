import os
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import socket

AES_KEY_PATH = r"256_bit_AES_key"

def load_or_generate_key():
    if os.path.exists(AES_KEY_PATH):
        with open(AES_KEY_PATH, "rb") as key_file:
            return key_file.read()
    else:
        key = os.urandom(32)
        with open(AES_KEY_PATH, "wb") as key_file:
            key_file.write(key)
        return key

Ka = load_or_generate_key()

def encrypt_frame_gcm(frame, key):
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    frame_bytes = frame.tobytes()
    ciphertext = encryptor.update(frame_bytes) + encryptor.finalize()
    tag = encryptor.tag

    return len(ciphertext).to_bytes(4, 'big') + iv + tag + ciphertext



def encrypt_and_save(aes_queue):
    HOST = 'ip_address_of_module_1'
    PORT = 65452
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
    s.connect((HOST, PORT))
    start_time = datetime.now().timestamp()
    encrypted_frames = []

    while True:
        frame = aes_queue.get()  # **Blocking Call - No Empty Check**
        encrypted_frame = encrypt_frame_gcm(frame, Ka)
        s.sendall(encrypted_frame)
        print("sent aesframe")
