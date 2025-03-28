import tenseal as ts
import socket
import pickle
import time
with open(r"public_context_file_path_to_be_used_for_encrypted_processing", "rb") as filepu:
    serialized_context_pu = filepu.read()
context = ts.context_from(serialized_context_pu)


HOST = 'IP_Address_of_Module_3' 
PORT = 65442        # Port to communicate

# Create a socket
send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
send.connect((HOST, PORT))
send.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
print("Connected to Node 3 ")

HOST = 'IP_Address_of_Module_2'  
PORT = 65432  # Port number

# Create a socket
rcv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rcv.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
rcv.bind((HOST, PORT))
rcv.listen()
print("Node 2 is listening on 65432...")






# loading the image.
filr = open(r"file_path_of_encrypted_embeddings_with_labels","rb")
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
file_path = r"file_path_to_save_encrypted_embeddings_at_runtime\emb"+time.strftime("%H_%M_%S")+".pkl"

def main():
    embeddings_list = []
    print("starting 2.1")
    while True:  # Keep the server running
        print("Waiting for a new connection...")
        conn, addr = rcv.accept()
        print(f"Connected to {addr}")

        try:
            while True:
                # Try receiving timestamp first
                try:
                    data = conn.recv(450000)
                    if not data:
                        raise ConnectionResetError  # If empty, assume disconnection
                    timestamp = data.decode()
                    print(timestamp)
                except (UnicodeDecodeError, ConnectionResetError, socket.error):
                    print("Client disconnected. Waiting for a new connection...")
                    break  # Exit inner loop, wait for a new connection

                # Try receiving encrypted embeddings
                try:
                    data = conn.recv(450000)

                    if not data:
                        raise ValueError("Incomplete data received")
                    embeddingsenc = data
                    print("Received embeddings")
                    embeddings_list.append(embeddingsenc)
                    with open(file_path, "wb") as emb_file:
                        pickle.dump(embeddings_list, emb_file)
                    print(f"Overwrote {len(embeddings_list)} embeddings to {file_path}")

                    embeddings = ts.ckks_vector_from(context, embeddingsenc)
                    print("Processed embeddings")

                    distances = encrypted_recognition(embeddings)
                    send.sendall(timestamp.encode())

                    for label in distances:
                        send.sendall(distances[label].serialize())

                    print(f"Frame at {timestamp} is processed and sent.")

                except (IndexError, ValueError) as e:
                    print(f"Data processing error: {e}, skipping frame.")



        except (ConnectionResetError, socket.error) as e:
            print(f"Client disconnected unexpectedly: {e}. Waiting for a new connection...")

        except Exception as e:
            print(f"Unexpected error: {e}")

        finally:
            conn.close()

main()
