from facenet_pytorch import InceptionResnetV1, MTCNN
import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from PIL import Image
import pickle
import numpy as np
import tenseal as ts

# Load pre-trained FaceNet model (without classification head)
model = InceptionResnetV1(pretrained='vggface2').eval()  # Evaluation mode
mtcnn = MTCNN(keep_all=True)
# Transformations for input images
transform = transforms.Compose([
    transforms.Resize((512, 512)),  # Match model input size
])

# Function to convert images to RGB
def convert_to_rgb(image):
    if isinstance(image, np.ndarray):  # If it's a NumPy array (e.g., from OpenCV)
        if image.shape[-1] == 4:  # Convert RGBA to RGB
            image = Image.fromarray(image).convert("RGB")
        else:  # Convert BGR to RGB
            image = Image.fromarray(image[:, :, ::-1])
    elif image.mode != "RGB":  # Convert grayscale or RGBA to RGB
        image = image.convert("RGB")
    return image

# Load dataset
dataset = datasets.ImageFolder(root=r"C:\Users\pc\PycharmProjects\fypfash\dataset", transform=None)

# Store embeddings for each class
class_embeddings = {}  # {class_name: [embedding1, embedding2, ...]}

with torch.no_grad():  # No gradient calculation needed (faster)
    for img_path, label in dataset.samples:
        label_name = dataset.classes[label]  # Convert label index to class name

        # Open the image and convert it to RGB
        image = Image.open(img_path)
        image = convert_to_rgb(image)  # Convert BGR or RGBA to RGB
        image = transform(image) # Apply transformations and add batch dimension
        boxes, _ = mtcnn.detect(image)

        if boxes is not None:
            print("face detected in image")
            face = mtcnn(image)
            del(image)
            if face is None:
                print(f"[WARNING] No face detected in {img_path}. Skipping.")
                continue  # Skip images without faces

            embedding = model(face)  # Get the 512D embedding

            if label_name not in class_embeddings:
                class_embeddings[label_name] = []

            class_embeddings[label_name].append(embedding.detach().numpy().flatten().tolist())  # Store embedding
for label in class_embeddings:
    print(len(class_embeddings[label]))
# Compute the reference embedding as the mean of all embeddings per class
reference_embeddings = {}  # {class_name: reference_embedding}

for label, embeddings in class_embeddings.items():
    if not embeddings:  # Skip empty lists
        print(f"[WARNING] No embeddings found for class {label}. Skipping.")
        continue

    # Convert embeddings to a NumPy array, ensuring all elements have the same shape
    try:
        embeddings_array = np.array(embeddings, dtype=np.float32)
        reference_embeddings[label] = np.mean(embeddings_array, axis=0)
    except ValueError as e:
        print(f"[ERROR] Shape mismatch in embeddings for {label}: {e}")
        continue  # Skip problematic classes









file = open(r"file_path_to_save_unencrypted_embeddings","wb")
pickle.dump(reference_embeddings,file)
file.close()

with open(r"public_context_for_encryption", "rb") as fileu:
    serialized_context = fileu.read()
context = ts.context_from(serialized_context)

encrypted_embs={}
for label in reference_embeddings:
    encrypted_embedding = ts.ckks_vector(context, reference_embeddings[label])
    encrypted_embs[label]=encrypted_embedding.serialize()
print (len(encrypted_embs))

filenc = open(r"file_path_for_saving_encrypted_embeddings","wb")
pickle.dump(encrypted_embs,filenc)
filenc.close()

print(len(reference_embeddings))
for label in reference_embeddings:
    print(len(reference_embeddings[label]))


