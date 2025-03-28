import cv2
import time
from facenet_pytorch import InceptionResnetV1, MTCNN
import tenseal as ts
import socket
from datetime import datetime


def facial_recognition(he_queue):
    HOST = 'IP_address_of_module_2'
    PORT = 65432
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
    s.connect((HOST, PORT))

    time.sleep(2)  # Wait 2 seconds before reading the file

    filepu = open(r"public_context_file_path", "rb")
    context = ts.context_from(filepu.read())
    filepu.close()

    mtcnn = MTCNN(keep_all=True)
    model = InceptionResnetV1(pretrained='vggface2').eval()

    while True:
        frame = he_queue.get()  # **Blocking Call - No Empty Check**
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = mtcnn(frame_rgb)

        if faces is not None:
            face_embedding = model(faces[0].unsqueeze(0))
            encrypted_embedding = ts.ckks_vector(context, face_embedding.detach().numpy().flatten().tolist())

            time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            time.sleep(0.2)
            s.sendall(time_stamp.encode())
            s.sendall(encrypted_embedding.serialize())

            print(f"Sent encrypted face data at {time_stamp}")
