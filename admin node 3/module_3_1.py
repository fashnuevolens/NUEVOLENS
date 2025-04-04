import tenseal as ts
import win32evtlogutil
import win32evtlog
from datetime import datetime
import socket
from plyer import notification
import time
import tkinter as tk
from tkinter import filedialog
import pickle

filr = open(r"C:\Users\pc\PycharmProjects\NUEVOLENS\encrypted_emebeddings.pkl","rb")
embeddings_read  = pickle.load(filr)
filr.close()
labels = []
for label in embeddings_read:
    labels.append(label)

print("Setup loading..")
def select_file(type,func,title,flag):
    root = tk.Tk()
    root.withdraw()
    path = ""
    if func == "input":
        if flag == 1:
            path = filedialog.askopenfilename(
                title=title,
                filetypes=[type]
            )
        if flag == 2:
            path = filedialog.askopenfilenames(
                title=title,
                filetypes=[type]
            )
    elif func == "output":
        path = filedialog.askdirectory(
            title=title
        )

    if path:
        print(f"Selected file/folder: {path}")
        return path
    else:
        print("No file selected.")
        return None

with open(select_file(("TENSEAL files","*.tenseal"),"input","Select TenSEAL CKKS Private Context",1), "rb") as filepv:
    serialized_contextpv = filepv.read()
contextpv = ts.context_from(serialized_contextpv)
print("Setup Complete. Starting...")



HOST = '127.0.0.1'  # Loopback address for local testing
PORT = 65442  # Port number
# Create a socket
rcv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rcv.bind((HOST, PORT))
rcv.listen()
print("Node 3 is listening on 65442...")


last_notifications = {}
def show_notification(title, message, condition_type):
    current_time = time.time()

    # Check if the same condition type was notified within the last 10 minutes
    if (condition_type in last_notifications):
        last_time = last_notifications[condition_type]
        if condition_type == "Unknown":
            if current_time - last_time < 60:  # 600 seconds = 10 minutes
                return  # Do not send notification
        else:
            if current_time - last_time < 120:  # 600 seconds = 10 minutes
                return  # Do not send notification

    # Send notification
    notification.notify(
        title=title,
        message=message,
        timeout=5  # Notification disappears after 5 seconds
    )

    # Update last notification time
    last_notifications[condition_type] = current_time

def log(event_id=1001, event_type=win32evtlog.EVENTLOG_INFORMATION_TYPE,
                         message="Secure Surveillance", source="NUEVOLENS", custom_timestamp=None):
    try:
        # Register the source if it's not already registered
        try:
            win32evtlogutil.AddSourceToRegistry(source, "Application")
        except Exception:
            pass  # Ignore if already registered

        # If no custom timestamp is provided, use current time
        if custom_timestamp is None:
            custom_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format message with custom timestamp
        formatted_message = f"[{custom_timestamp}] {message}"

        # Write log to Windows Event Viewer (Removed SID requirement)
        win32evtlogutil.ReportEvent(source, eventID= event_id, eventType=event_type, strings=[formatted_message], data=b'fash_ss' )
        print(f"Logged event {event_id} with custom timestamp: {custom_timestamp} with source {source}")

    except Exception as e:
        print(f"Failed to log event: {e}")


def encrypted_recognition(enc_distances):
    person = "TBD"
    for i in range(len(labels)):
        threshold = 0.95  # defining a threshold for facial recognition.
        encrypted_distance = ts.ckks_vector_from(contextpv,enc_distances[i])
        decrypted_distance = encrypted_distance.decrypt()  # decrypting the result to get the distance.
        print(f"Decrypted Euclidean distance (encrypted): {decrypted_distance}")

        decrypted_distance = decrypted_distance[0] ** 0.5  # calculating the square root to get the actual distance.
        print(f"square root: {decrypted_distance}")

        # checking if the distance is below the threshold for a match.
        if decrypted_distance < threshold:
            person = labels[i]
            print("match")
            break
        else:
            print("No MATCH")
            person = "Unknown"
    return person

# main function to capture video and perform facial recognition in real-time.
def main():
    print("starting 3.1")

    while True:  # Keep the server running
        print("Waiting for a new connection...")
        conn, addr = rcv.accept()
        print(f"Connected to {addr}")

        try:
            while True:
                enc_distances = []

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

                # Try receiving encrypted distances
                try:
                    for count in range(2):
                        data = conn.recv(450000)
                        if not data:
                            raise ValueError("Incomplete data received")
                        enc_distances.append(data)

                    if len(enc_distances) < 2:
                        raise ValueError("Missing required data, skipping this frame.")

                    print(len(enc_distances))
                    text = encrypted_recognition(enc_distances)

                    if text == "Unknown":
                        print(f"Unknown detected at {timestamp}")
                        log(event_id=2002, event_type=win32evtlog.EVENTLOG_WARNING_TYPE,
                            message="Unknown person detected",
                            custom_timestamp=timestamp)
                        show_notification("WARNING", "UNKNOWN PERSON DETECTED", "Unknown")

                    elif text == "No faces":
                        continue
                    else:
                        label = f"{text} detected at {timestamp}"
                        print(label)
                        log(event_id=2030, event_type=win32evtlog.EVENTLOG_INFORMATION_TYPE,
                            message=label,
                            custom_timestamp=timestamp)
                        show_notification("ALERT", f"{text} HAS BEEN DETECTED", text)

                except (IndexError, ValueError) as e:
                    print(f"Data processing error: {e}, skipping frame.")

        except (ConnectionResetError, socket.error) as e:
            print(f"Client disconnected unexpectedly: {e}. Waiting for a new connection...")

        except Exception as e:
            print(f"Unexpected error: {e}")

        finally:
            conn.close()

main()
