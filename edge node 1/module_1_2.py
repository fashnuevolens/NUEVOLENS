import os
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import socket

AES_KEY_PATH = r"C:\Users\pc\PycharmProjects\NUEVOLENS\256_bit_AES_key.bin"


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
    HOST = '127.0.0.1'
    PORT = 65452
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    print("connected")
    while True:
        frame = aes_queue.get()
        print ( len (frame))  # **Blocking Call - No Empty Check**
        encrypted_frame = encrypt_frame_gcm(frame, Ka)
        s.sendall(encrypted_frame)
        print (f" sent {len(encrypted_frame)} bytes")
