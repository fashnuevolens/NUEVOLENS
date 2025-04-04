from datetime import datetime
import tenseal as ts
import socket
import pickle
import time
with open(r"C:\Users\pc\PycharmProjects\NUEVOLENS\public_context.tenseal", "rb") as filepu:
    serialized_context_pu = filepu.read()
context = ts.context_from(serialized_context_pu)


HOST = '127.0.0.1'
PORT = 65442        # Port to communicate

# Create a socket
send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
send.connect((HOST, PORT))
send.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)

print("Connected to Node 3 ")

HOST = '0.0.0.0'
PORT = 65432  # Port number

# Create a socket
rcv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rcv.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2097152)
rcv.bind((HOST, PORT))
rcv.listen()
print("Node 2 is listening on 65432...")






# loading the image.
filr = open(r"C:\Users\pc\PycharmProjects\NUEVOLENS\encrypted_emebeddings.pkl","rb")
embeddings_read  = pickle.load(filr)
filr.close()




ready_embs = {}
for label in embeddings_read:
    # Ensure it's in the correct format
    ready_embs[label] = ts.ckks_vector_from(context, embeddings_read[label])



# function to perform encrypted facial recognition using Euclidean distance.
def encrypted_recognition(encrypted_embedding):
    distances = {}
    for label in embeddings_read:
        # calculating the Euclidean distance between the encrypted embeddings.
        distance = encrypted_embedding - ready_embs[label]
        distance_encrypted = distance.dot(distance) # computing dot product to reduce it to a scalar.
        distances[label]=distance_encrypted
    return distances




# main function to capture video and perform facial recognition in real-time.
file_path = r"C:\Users\pc\PycharmProjects\NUEVOLENS\emb"+time.strftime("%H_%M_%S")+".pkl"


def recv_all(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def main():
    embeddings_list = []
    print("starting 2.1")
    while True:  # Keep the server running
        print("Waiting for a new connection...")
        conn, addr = rcv.accept()
        print(f"Connected to {addr}")

        try:
            while True:

                # Try receiving encrypted embeddings
                try:
                    frame_size_bytes = recv_all(conn, 4)
                    size = int.from_bytes(frame_size_bytes, 'big')
                    print(size," bytes size\n")
                   # size = siz.decode()
                    data = recv_all(conn,size)
                    if not data:
                        raise ValueError("Incomplete data received")

                    print(f"received {len(data)} bytes")
                    embeddingsenc = data
                    print("Received embeddings")
                    embeddings_list.append(embeddingsenc)
                    with open(file_path, "wb") as emb_file:
                        pickle.dump(embeddings_list, emb_file)
                    print(f"Overwrote {len(embeddings_list)} embeddings to {file_path}")

                    embeddings = ts.ckks_vector_from(context, embeddingsenc)
                    print("Processed embeddings")
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    distances = encrypted_recognition(embeddings)
                    send.sendall(timestamp.encode())

                    for label in distances:
                        send.sendall(distances[label].serialize())

                    print(f"Frame at {timestamp} is processed and sent.")

                except (IndexError, ValueError) as e:
                    print(f"Data processing error: {e}, skipping frame.")
                    break



        except (ConnectionResetError, socket.error) as e:
            print(f"Client disconnected unexpectedly: {e}. Waiting for a new connection...")

        except Exception as e:
            print(f"Unexpected error: {e}")

        finally:
            conn.close()

main()
