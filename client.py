import tkinter as tk
from tkinter import messagebox, simpledialog
import socket
import threading
import random
import datetime
from tkinter.font import BOLD

# === Connect to Server ===
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.connect(("13.62.57.248", 244))
except Exception as e:
    messagebox.showerror("Connection Error", f"Could not connect to server:\n{e}")
    exit()

# === Ask for Username ===
username = simpledialog.askstring("Username", "Enter your username:")
if not username or username.strip() == "":
    messagebox.showwarning("Empty Username", "Guest mode activated.")
    username = "Guest" + str(random.randint(1, 100))

# === Initialize UI ===
root = tk.Tk()
root.title("Messenger")
root.geometry("800x800")
root.configure(bg="#f0f0f0")

# === Chat Display Frame ===
chat_frame = tk.Frame(root, bg="#f0f0f0")
chat_frame.pack(pady=(20, 10), fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(chat_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text = tk.Text(chat_frame, bg="#ffffff", fg="black",
               font=("Segoe UI Emoji", 12, "italic"),
               state="disabled", wrap=tk.WORD,
               yscrollcommand=scrollbar.set)
text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=text.yview)

# === Tags for formatting ===
text.tag_config("bold", font=("Segoe UI Emoji", 12, "bold"))
text.tag_config("italic", font=("Segoe UI Emoji", 12, "italic"))

# === Input and Button Frame ===
bottom_frame = tk.Frame(root, bg="#f0f0f0")
bottom_frame.pack(pady=(0, 10), fill=tk.X)

input_field = tk.Entry(bottom_frame, bg="white", fg="black", font=("Segoe UI Emoji", 12))
input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

def send():
    message = input_field.get().strip()
    if message == "":
        return
    full_message = f"{username}: {message}"
    try:
        server.send(full_message.encode("utf-8"))
    except:
        messagebox.showerror("Error", "Failed to send message.")
    input_field.delete(0, tk.END)

input_field.bind("<Return>", lambda event: send())

send_button = tk.Button(bottom_frame, text="Send", command=send,
                        font=("Arial", 12), bg="#4CAF50", fg="white", width=10)
send_button.pack(side=tk.LEFT, padx=5)

def emoji():
    emoji_frame = tk.Toplevel(root)
    emoji_frame.title("Emoji Picker")
    emoji_frame.geometry("300x400")
    emoji_frame.configure(bg="#f0f0f0")
    emoji_frame.attributes("-topmost", True)

    emoji_canvas = tk.Canvas(emoji_frame, bg="#f0f0f0")
    emoji_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(emoji_frame, orient=tk.VERTICAL, command=emoji_canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    emoji_canvas.configure(yscrollcommand=scrollbar.set)

    emoji_inner = tk.Frame(emoji_canvas, bg="#f0f0f0")
    emoji_canvas.create_window((0, 0), window=emoji_inner, anchor="nw")

    emoji_list = ["😊", "😂", "😔", "😢", "😠", "😡", "😍", "😘", "😚", "😜", "👍", "🔥", "🎉", "💀", "💯", "😎", "🤖", "🙈", "👀"]
    for e in emoji_list:
        b = tk.Button(emoji_inner, text=e, font=("Segoe UI Emoji", 14),
                      command=lambda e=e: input_field.insert(tk.END, e),
                      bg="#4CAF50", fg="white", width=4)
        b.pack(pady=4, padx=10, anchor="w")

    def resize_canvas(event):
        emoji_canvas.configure(scrollregion=emoji_canvas.bbox("all"))

    emoji_inner.bind("<Configure>", resize_canvas)

emoji_button = tk.Button(bottom_frame, text="Emoji", command=emoji,
                         font=("Arial", 12), bg="#4CAF50", fg="white", width=10)
emoji_button.pack(side=tk.LEFT, padx=5)

# === Username + Time Label Frame ===
status_frame = tk.Frame(root, bg="#f0f0f0")
status_frame.pack(side="bottom", fill=tk.X, padx=10, pady=5)

user_label = tk.Label(status_frame, text="Logged in as: " + username,
                      bg="#f0f0f0", fg="black", font=("Arial", 12))
user_label.pack(side="left")

time_label = tk.Label(status_frame, text="Time: " + datetime.datetime.now().strftime("%H:%M"),
                      bg="#f0f0f0", fg="black", font=("Arial", 12))
time_label.pack(side="right")

text.tag_config("normal", font=("Arial", 12))

# === Receiving Messages Thread ===
def receive():
    while True:
        try:
            message = server.recv(1024).decode("utf-8")
            if not message:
                break

            text.config(state="normal")
            if "[bold]" in message:
                sender, content = message.split(":", 1)
                content = content.replace("[bold]", "").strip()
                text.insert(tk.END, sender + ":", "bold")
                text.insert(tk.END, content + "\n", "bold")
            elif "[italic]" in message:
                sender, content = message.split(":", 1)
                content = content.replace("[italic]", "").strip()
                text.insert(tk.END, sender + ":", "italic")
                text.insert(tk.END, content + "\n", "italic")
            else:
                text.insert(tk.END, message + "\n", "normal")
                text.config(state="disabled")
                text.yview(tk.END)
        except Exception as e:
            print("Error:", e)
            break

threading.Thread(target=receive, daemon=True).start()

# === Start App ===
root.mainloop()
