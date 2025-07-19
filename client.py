import tkinter as tk
from tkinter import messagebox, simpledialog
import socket
import threading
import random
import datetime

# === Connect to Server ===
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.connect(("13.62.57.248", 244))
except Exception as e:
    messagebox.showerror("Connection Error", f"Could not connect to server:\n{e}")
    exit()

# === Ask for Username ===
username = simpledialog.askstring("Username", "Please enter your username:")
if not username or username.strip() == "":
    messagebox.showwarning("Empty Username", "Entering Guest Mode.")
    username = "Guest" + str(random.randint(1, 100))

# === Initialize UI ===
root = tk.Tk()
root.title("Messenger")
root.geometry("800x800")
root.configure(bg="#f0f0f0")

# === Chat Display + Scroll ===
frame = tk.Frame(root)
frame.pack(pady=20, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text = tk.Text(frame, bg="#f0f0f0", fg="black", font=("Arial", 12),
               state="disabled", yscrollcommand=scrollbar.set, wrap=tk.WORD)
text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=text.yview)

# === Input Field ===
input_field = tk.Entry(root, bg="#ffffff", fg="black", font=("Arial", 12))
input_field.pack(pady=10, fill=tk.X, padx=20)

# === Send Message ===
def send():
    message = input_field.get().strip()
    if message == "":
        return
    # Add timestamp (optional)
    # now = datetime.datetime.now().strftime("%H:%M")
    # full_message = f"[{now}] {username}: {message}"
    full_message = f"{username}: {message}"
    try:
        server.send(full_message.encode("utf-8"))
    except:
        messagebox.showerror("Error", "Failed to send message.")
    input_field.delete(0, tk.END)

# Bind Enter Key
input_field.bind("<Return>", lambda event: send())

# === Receive Messages in Background ===
def receive():
    while True:
        try:
            message = server.recv(1024).decode("utf-8")
            if not message:
                break
            text.config(state="normal")
            text.insert(tk.END, message + "\n")
            text.yview(tk.END)  # Auto-scroll
            text.config(state="disabled")
        except ConnectionAbortedError:
            break
        except Exception as e:
            print("Receive error:", e)
            break

threading.Thread(target=receive, daemon=True).start()

# === Send Button ===
send_button = tk.Button(root, text="Send", command=send, font=("Arial", 12), bg="#4CAF50", fg="white")
send_button.pack(pady=10)

# === Show Username at Bottom ===
user_label = tk.Label(root, text="Logged in as: " + username, bg="#f0f0f0", fg="black", font=("Arial", 12))
user_label.pack(side="bottom", anchor="w", padx=10, pady=10)

# === Start UI Loop ===
root.mainloop()
