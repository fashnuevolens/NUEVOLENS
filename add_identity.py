from facenet_pytorch import InceptionResnetV1, MTCNN
import torch
from torchvision import datasets, transforms
from PIL import Image
import pickle
import numpy as np
import tenseal as ts


model = InceptionResnetV1(pretrained='vggface2').eval()
mtcnn = MTCNN(keep_all=True)

transform = transforms.Compose([
    transforms.Resize((512, 512)),
])


def convert_to_rgb(image):
    if isinstance(image, np.ndarray):
        if image.shape[-1] == 4:
            image = Image.fromarray(image).convert("RGB")
        else:
            image = Image.fromarray(image[:, :, ::-1])
    elif image.mode != "RGB":
        image = image.convert("RGB")
    return image

dataset = datasets.ImageFolder(root=r"path_to_dataset_folder/directory", transform=None)


class_embeddings = {}

with torch.no_grad():
    for img_path, label in dataset.samples:
        label_name = dataset.classes[label]


        image = Image.open(img_path)
        image = convert_to_rgb(image)
        image = transform(image)
        boxes, _ = mtcnn.detect(image)

        if boxes is not None:
            print("face detected in image")
            face = mtcnn(image)
            del(image)
            if face is None:
                print(f"[WARNING] No face detected in {img_path}. Skipping.")
                continue

            embedding = model(face)

            if label_name not in class_embeddings:
                class_embeddings[label_name] = []

            class_embeddings[label_name].append(embedding.detach().numpy().flatten().tolist())  # Store embedding
for label in class_embeddings:
    print(len(class_embeddings[label]))
# Compute the reference embedding as the mean of all embeddings per class
reference_embeddings = {}  # {class_name: reference_embedding}

for label, embeddings in class_embeddings.items():
    if not embeddings:
        print(f"[WARNING] No embeddings found for class {label}. Skipping.")
        continue

    try:
        embeddings_array = np.array(embeddings, dtype=np.float32)
        reference_embeddings[label] = np.mean(embeddings_array, axis=0)
    except ValueError as e:
        print(f"[ERROR] Shape mismatch in embeddings for {label}: {e}")
        continue  # Skip problematic classes









file = open(r"file_path_for_emebeddings.pkl","wb")
pickle.dump(reference_embeddings,file)
file.close()

with open(r"path_to_public_context.tenseal", "rb") as fileu:
    serialized_context = fileu.read()
context = ts.context_from(serialized_context)

encrypted_embs={}
for label in reference_embeddings:
    encrypted_embedding = ts.ckks_vector(context, reference_embeddings[label])
    encrypted_embs[label]=encrypted_embedding.serialize()
print (len(encrypted_embs))

filenc = open(r"file_path_to_encrypted_emebeddings.pkl","wb")
pickle.dump(encrypted_embs,filenc)
filenc.close()

