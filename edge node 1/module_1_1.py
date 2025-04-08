import cv2
from facenet_pytorch import InceptionResnetV1, MTCNN
import tenseal as ts
import socket
import time

def facial_recognition(he_queue):
    HOST = "Ip_address_of_module_2'
    PORT = 65432
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    time.sleep(2)  # Wait 2 seconds before reading the file

    filepu = open(r"path_to_public_context.tenseal", "rb")
    context = ts.context_from(filepu.read())
    filepu.close()

    mtcnn = MTCNN(keep_all=True)
    model = InceptionResnetV1(pretrained='vggface2').eval()

    while True:
        frame = he_queue.get()  # **Blocking Call - No Empty Check**
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = mtcnn(frame_rgb)

        if faces is not None:
            print (f"{len(faces)} faces found")
            face_embedding = model(faces[0].unsqueeze(0))
            encrypted_embedding = ts.ckks_vector(context, face_embedding.detach().numpy().flatten().tolist())

            frame_size = len(encrypted_embedding.serialize()).to_bytes(4, 'big')
            s.sendall(frame_size)
            time.sleep(0.5)
            s.sendall(encrypted_embedding.serialize())
            print(f" Sent {len(encrypted_embedding.serialize())} bytes")
            print(f"Sent encrypted face data ")
