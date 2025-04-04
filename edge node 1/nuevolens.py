import cv2
import multiprocessing
from module_1_1 import facial_recognition
from module_1_2 import encrypt_and_save

def capture_frames(aes_queue, he_queue,  frame_skip=45):
    video = cv2.VideoCapture(0)
    if not video.isOpened():
        print("Error: Cannot open webcam")
        return

    frame_count = 0

    while True:
        ret, frame = video.read()
        if not ret:
            break

        # **Always send frames to AES queue (No frame loss)**
        aes_queue.put(frame)

        # **Only send every `frame_skip`th frame to HE queue**
        if frame_count % frame_skip == 0:
            he_queue.put(frame)

        frame_count += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    manager = multiprocessing.Manager()
    aes_queue = manager.Queue(maxsize=5)  # Larger size for AES (real-time)
    he_queue = manager.Queue(maxsize=2)   # Smaller size for HE (slow)

    capture_process = multiprocessing.Process(target=capture_frames, args=(aes_queue,he_queue))
    aes_process = multiprocessing.Process(target=encrypt_and_save, args=(aes_queue,))
    he_process = multiprocessing.Process(target=facial_recognition, args=(he_queue,))

    capture_process.start()
    aes_process.start()
    he_process.start()

    capture_process.join()
    aes_process.join()
    he_process.join()
