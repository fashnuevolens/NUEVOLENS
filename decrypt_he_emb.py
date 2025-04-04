import numpy as np
import matplotlib.pyplot as plt
import tenseal as ts
import pickle

embs = open(r"C:\Users\pc\PycharmProjects\FYPfash2\emb.pkl", "rb")
serialized_embeddings = pickle.load(embs)  # ✅ Load all embeddings as a list

# Convert all embeddings back to TenSEAL encrypted vectors

file = open(r"C:\Users\pc\PycharmProjects\FYPfash2\pvt_context1.tenseal", "rb")
context = ts.context_from(file.read())
file.close()

embeddings=[]
for emb in serialized_embeddings:
    embeddings.append(ts.ckks_vector_from(context, emb) )
for emb in embeddings:
    decrypted_embedding = emb.decrypt()
    decrypted_embedding = np.array(decrypted_embedding)
    decrypted_embedding = (decrypted_embedding - np.min(decrypted_embedding)) / (np.max(decrypted_embedding) - np.min(decrypted_embedding))  # Scale to [0,1]
    decrypted_embedding = 2 * decrypted_embedding - 1  # Scale to [-1,1]
    x = decrypted_embedding[::2]  # Take even indices as X
    y = decrypted_embedding[1::2]  # Take odd indices as Y


    plt.figure(figsize=(5, 5))
    plt.plot(x, y, linestyle="-", marker="o", markersize=2, color="blue")
    plt.title("Decrypted Face Embedding Outline")
    plt.axis("equal")
    plt.show(block=True)