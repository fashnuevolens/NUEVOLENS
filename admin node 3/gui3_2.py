import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading


def start_action():
    global process
    process = subprocess.Popen(
        [r"path_to_project\NUEVOLENS\root\Scripts\python.exe", "module_3.2.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        text=True
    )

    # Start a thread to read output
    threading.Thread(target=read_output, daemon=True).start()
    threading.Thread(target=read_errors, daemon=True).start()

def read_output():

    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            output_text.insert(tk.END, output)
            output_text.see(tk.END)  # Auto-scroll to the latest output

def read_errors():

    while True:
        output = process.stderr.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            output_text.insert(tk.END, output)
            output_text.see(tk.END)
def stop_action():
    if process.poll() is None:  # Check if process is running
        process.terminate()  # Terminate the script
        output_text.insert(tk.END, "Process terminated...")
        output_text.see(tk.END)



root = tk.Tk()
root.title("NUEVOLENS Surveillance System VIDEO PLAYER")
root.geometry("2000x1000")

b=tk.Canvas(bg="#380054", height=1000,width=2000)
b.pack()


output_text = scrolledtext.ScrolledText(root, width=100, height=20, bg="hot pink", fg="#380054" , font= ("Courier New", 16)  )
text_window = b.create_window(800, 325,anchor="center", window=output_text)

start_btn = tk.Button(root, text="START", fg="#380054", bg="hot pink", font=("Bauhaus 93", 14, "bold"), command=start_action)
start = b.create_window(800, 600,anchor="center", window=start_btn)

stop_btn = tk.Button(root, text="STOP", fg="#380054", bg="hot pink", font=("Bauhaus 93", 16), command=stop_action)
stop = b.create_window(800, 650,anchor="center", window=stop_btn)

title = tk.Label(root,text="NUEVOLENS VIDEO DECRYPTOR",bg="#380054", fg="hot pink" , font= ("Bauhaus 93", 24, "bold"))
t = b.create_window(800, 50,anchor="center", window=title)

root.mainloop()
